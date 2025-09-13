import caldav
from caldav import DAVClient
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings
from .models import Event, CalendarConnection
from icalendar import Calendar as iCalendar, Event as iEvent
import uuid


class CalendarService:
    """Service for calendar integration with Apple Calendar and other CalDAV providers"""
    
    def __init__(self, connection_id=None):
        self.connection = None
        if connection_id:
            try:
                self.connection = CalendarConnection.objects.get(id=connection_id, is_active=True)
            except CalendarConnection.DoesNotExist:
                raise ValueError(f"Calendar connection {connection_id} not found or inactive")
    
    def test_connection(self, server_url, username, password):
        """Test calendar connection without saving"""
        try:
            client = DAVClient(
                url=server_url,
                username=username,
                password=password
            )
            principal = client.principal()
            calendars = principal.calendars()
            return {'success': True, 'calendars': len(calendars)}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def sync_from_calendar(self, start_date=None, end_date=None):
        """Import events from external calendar"""
        if not self.connection:
            raise ValueError("No calendar connection configured")
        
        if not start_date:
            start_date = timezone.now().date()
        if not end_date:
            end_date = start_date + timedelta(days=30)
        
        try:
            client = DAVClient(
                url=self.connection.server_url,
                username=self.connection.username,
                password=self.connection.password
            )
            
            principal = client.principal()
            calendars = principal.calendars()
            
            imported_count = 0
            
            for calendar in calendars:
                # Get events from the calendar within date range
                events = calendar.search(
                    start=start_date,
                    end=end_date,
                    event=True,
                    expand=True
                )
                
                for event in events:
                    imported_count += self._import_event(event)
            
            # Update last sync time
            self.connection.last_sync = timezone.now()
            self.connection.save()
            
            return {'success': True, 'imported': imported_count}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _import_event(self, caldav_event):
        """Import a single event from CalDAV"""
        try:
            # Parse the iCalendar data
            cal = iCalendar.from_ical(caldav_event.data)
            
            for component in cal.walk():
                if component.name == "VEVENT":
                    # Extract event data
                    title = str(component.get('summary', 'Untitled Event'))
                    description = str(component.get('description', ''))
                    start_time = component.get('dtstart').dt
                    end_time = component.get('dtend').dt
                    external_id = str(component.get('uid', ''))
                    
                    # Convert datetime if needed
                    if isinstance(start_time, datetime):
                        if start_time.tzinfo is None:
                            start_time = timezone.make_aware(start_time)
                    else:
                        # All-day event
                        start_time = timezone.make_aware(
                            datetime.combine(start_time, datetime.min.time())
                        )
                    
                    if isinstance(end_time, datetime):
                        if end_time.tzinfo is None:
                            end_time = timezone.make_aware(end_time)
                    else:
                        # All-day event
                        end_time = timezone.make_aware(
                            datetime.combine(end_time, datetime.min.time())
                        )
                    
                    # Check if event already exists
                    existing_event = Event.objects.filter(
                        external_id=external_id,
                        calendar_source=self.connection.provider
                    ).first()
                    
                    if existing_event:
                        # Update existing event
                        existing_event.title = title
                        existing_event.description = description
                        existing_event.start_time = start_time
                        existing_event.end_time = end_time
                        existing_event.save()
                    else:
                        # Create new event
                        Event.objects.create(
                            title=title,
                            description=description,
                            start_time=start_time,
                            end_time=end_time,
                            external_id=external_id,
                            calendar_source=self.connection.provider,
                            priority='medium'
                        )
                    
                    return 1
            
            return 0
            
        except Exception as e:
            print(f"Error importing event: {e}")
            return 0
    
    def export_to_calendar(self, event_id):
        """Export a local event to external calendar"""
        if not self.connection:
            raise ValueError("No calendar connection configured")
        
        try:
            event = Event.objects.get(id=event_id)
            
            # Create iCalendar event
            cal = iCalendar()
            cal.add('prodid', '-//JAgenda//JAgenda Calendar//EN')
            cal.add('version', '2.0')
            
            ical_event = iEvent()
            ical_event.add('summary', event.title)
            ical_event.add('description', event.description)
            ical_event.add('dtstart', event.start_time)
            ical_event.add('dtend', event.end_time)
            ical_event.add('uid', str(event.id))
            ical_event.add('dtstamp', timezone.now())
            
            cal.add_component(ical_event)
            
            # Connect to calendar and add event
            client = DAVClient(
                url=self.connection.server_url,
                username=self.connection.username,
                password=self.connection.password
            )
            
            principal = client.principal()
            calendars = principal.calendars()
            
            if calendars:
                calendar = calendars[0]  # Use first available calendar
                calendar.save_event(cal.to_ical())
                
                # Update event with external ID
                event.external_id = str(event.id)
                event.calendar_source = self.connection.provider
                event.save()
                
                return {'success': True, 'message': 'Event exported successfully'}
            else:
                return {'success': False, 'error': 'No calendars found'}
                
        except Event.DoesNotExist:
            return {'success': False, 'error': 'Event not found'}
        except Exception as e:
            return {'success': False, 'error': str(e)}


def get_apple_calendar_config():
    """Return Apple iCloud calendar configuration"""
    return {
        'name': 'Apple iCloud Calendar',
        'provider': 'apple',
        'server_url': 'https://caldav.icloud.com',
        'help_text': (
            'For Apple Calendar (iCloud), you need an app-specific password. '
            'Go to appleid.apple.com > Security > App-Specific Passwords to create one.'
        )
    }