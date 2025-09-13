from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from agenda.models import Event


class Command(BaseCommand):
    help = 'Create sample events for testing timeline functionality'

    def handle(self, *args, **options):
        # Clear existing events
        Event.objects.all().delete()
        
        # Create sample events for the next few days
        now = timezone.now()
        
        sample_events = [
            {
                'title': 'Team Meeting',
                'description': 'Weekly team sync and project updates',
                'start_time': now + timedelta(hours=2),
                'end_time': now + timedelta(hours=3),
                'priority': 'high',
                'status': 'pending'
            },
            {
                'title': 'Client Presentation',
                'description': 'Present project deliverables to client',
                'start_time': now + timedelta(days=1, hours=10),
                'end_time': now + timedelta(days=1, hours=11, minutes=30),
                'priority': 'urgent',
                'status': 'pending'
            },
            {
                'title': 'Code Review',
                'description': 'Review pull requests and discuss improvements',
                'start_time': now + timedelta(days=1, hours=14),
                'end_time': now + timedelta(days=1, hours=15),
                'priority': 'medium',
                'status': 'pending'
            },
            {
                'title': 'Project Planning',
                'description': 'Plan next sprint and allocate tasks',
                'start_time': now + timedelta(days=2, hours=9),
                'end_time': now + timedelta(days=2, hours=10, minutes=30),
                'priority': 'high',
                'status': 'pending'
            },
            {
                'title': 'Lunch Break',
                'description': 'Team lunch at the new restaurant',
                'start_time': now + timedelta(days=2, hours=12),
                'end_time': now + timedelta(days=2, hours=13),
                'priority': 'low',
                'status': 'pending'
            },
            {
                'title': 'Training Session',
                'description': 'Django best practices workshop',
                'start_time': now + timedelta(days=3, hours=15),
                'end_time': now + timedelta(days=3, hours=17),
                'priority': 'medium',
                'status': 'pending'
            },
            {
                'title': 'Bug Fix Session',
                'description': 'Fix critical bugs before release',
                'start_time': now + timedelta(days=4, hours=8),
                'end_time': now + timedelta(days=4, hours=10),
                'priority': 'urgent',
                'status': 'in_progress'
            },
            {
                'title': 'Documentation Review',
                'description': 'Update and review project documentation',
                'start_time': now + timedelta(days=5, hours=11),
                'end_time': now + timedelta(days=5, hours=12, minutes=30),
                'priority': 'low',
                'status': 'completed'
            },
        ]
        
        created_count = 0
        for event_data in sample_events:
            event = Event.objects.create(**event_data)
            created_count += 1
            self.stdout.write(f"Created event: {event.title}")
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} sample events')
        )