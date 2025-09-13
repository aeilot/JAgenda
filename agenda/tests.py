from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import datetime, timedelta
import json
from .models import Event, CalendarConnection
from .calendar_service import CalendarService

# Create your tests here.

class EventModelTest(TestCase):
    def test_event_creation(self):
        """Test creating an event with all required fields"""
        start_time = timezone.now()
        end_time = start_time + timedelta(hours=1)
        
        event = Event.objects.create(
            title="Test Event",
            description="Test description",
            start_time=start_time,
            end_time=end_time,
            priority="high",
            status="pending"
        )
        
        self.assertEqual(event.title, "Test Event")
        self.assertEqual(event.priority, "high")
        self.assertEqual(event.status, "pending")
        self.assertEqual(event.duration, 60)  # 1 hour = 60 minutes
        
    def test_event_str_representation(self):
        """Test string representation of event"""
        start_time = timezone.now()
        end_time = start_time + timedelta(hours=1)
        
        event = Event.objects.create(
            title="Meeting",
            start_time=start_time,
            end_time=end_time
        )
        
        expected_str = f"Meeting ({start_time.strftime('%Y-%m-%d %H:%M')})"
        self.assertEqual(str(event), expected_str)
    
    def test_event_duration_property(self):
        """Test event duration calculation"""
        start_time = timezone.now()
        end_time = start_time + timedelta(hours=2, minutes=30)
        
        event = Event.objects.create(
            title="Long Meeting",
            start_time=start_time,
            end_time=end_time
        )
        
        self.assertEqual(event.duration, 150)  # 2.5 hours = 150 minutes


class CalendarConnectionModelTest(TestCase):
    def test_calendar_connection_creation(self):
        """Test creating a calendar connection"""
        connection = CalendarConnection.objects.create(
            name="Test Calendar",
            provider="apple",
            server_url="https://caldav.icloud.com",
            username="test@icloud.com",
            password="test-password"
        )
        
        self.assertEqual(connection.name, "Test Calendar")
        self.assertEqual(connection.provider, "apple")
        self.assertTrue(connection.is_active)
        
    def test_calendar_connection_str(self):
        """Test string representation of calendar connection"""
        connection = CalendarConnection.objects.create(
            name="My Apple Calendar",
            provider="apple",
            server_url="https://caldav.icloud.com",
            username="test@icloud.com",
            password="test-password"
        )
        
        self.assertEqual(str(connection), "My Apple Calendar (apple)")


class TimelineViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create test events
        now = timezone.now()
        self.event1 = Event.objects.create(
            title="Test Event 1",
            start_time=now,
            end_time=now + timedelta(hours=1),
            priority="high"
        )
        self.event2 = Event.objects.create(
            title="Test Event 2",
            start_time=now + timedelta(days=1),
            end_time=now + timedelta(days=1, hours=2),
            priority="medium"
        )
    
    def test_timeline_view_loads(self):
        """Test timeline view loads successfully"""
        response = self.client.get(reverse('timeline'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "JAgenda Timeline")
        self.assertContains(response, "Test Event 1")
        self.assertContains(response, "Test Event 2")
    
    def test_timeline_context_data(self):
        """Test timeline view context contains expected data"""
        response = self.client.get(reverse('timeline'))
        self.assertIn('events', response.context)
        self.assertIn('timeline_data', response.context)
        
        events = response.context['events']
        self.assertEqual(len(events), 2)


class CalendarConnectionViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        
    def test_calendar_connections_view_loads(self):
        """Test calendar connections view loads successfully"""
        response = self.client.get(reverse('calendar_connections'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Calendar Connections")
        self.assertContains(response, "Add New Connection")
    
    def test_add_calendar_connection_post(self):
        """Test adding a calendar connection via POST"""
        data = {
            'name': 'Test Calendar',
            'provider': 'apple',
            'server_url': 'https://caldav.icloud.com',
            'username': 'test@icloud.com',
            'password': 'test-password'
        }
        
        # This will fail connection test, but should handle gracefully
        response = self.client.post(reverse('add_calendar_connection'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after POST


class EventsApiTest(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create test events
        now = timezone.now()
        self.event = Event.objects.create(
            title="API Test Event",
            start_time=now,
            end_time=now + timedelta(hours=1),
            priority="high",
            status="pending"
        )
    
    def test_events_api_get(self):
        """Test events API returns JSON data"""
        response = self.client.get(reverse('events_api'))
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertIn('events', data)
        self.assertEqual(len(data['events']), 1)
        
        event_data = data['events'][0]
        self.assertEqual(event_data['title'], 'API Test Event')
        self.assertEqual(event_data['priority'], 'high')
        self.assertEqual(event_data['status'], 'pending')
    
    def test_create_event_api(self):
        """Test creating event via API"""
        now = timezone.now()
        data = {
            'title': 'New API Event',
            'description': 'Created via API',
            'start_time': now.isoformat(),
            'end_time': (now + timedelta(hours=1)).isoformat(),
            'priority': 'medium'
        }
        
        response = self.client.post(
            reverse('create_event'),
            json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        
        # Verify event was created
        self.assertEqual(Event.objects.filter(title='New API Event').count(), 1)


class CalendarServiceTest(TestCase):
    def test_calendar_service_initialization(self):
        """Test CalendarService initialization"""
        service = CalendarService()
        self.assertIsNone(service.connection)
    
    def test_calendar_service_with_invalid_connection(self):
        """Test CalendarService with invalid connection ID"""
        import uuid
        invalid_uuid = str(uuid.uuid4())  # Valid UUID format but doesn't exist
        with self.assertRaises(ValueError):
            CalendarService(invalid_uuid)


class NavigationTest(TestCase):
    def test_all_main_pages_accessible(self):
        """Test that all main pages are accessible"""
        client = Client()
        
        urls_to_test = [
            reverse('index'),
            reverse('agenda'),
            reverse('timeline'),
            reverse('calendar_connections'),
        ]
        
        for url in urls_to_test:
            response = client.get(url)
            self.assertEqual(response.status_code, 200, f"Failed to load {url}")
