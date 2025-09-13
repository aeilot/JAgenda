from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

# Create your models here.

class Event(models.Model):
    """Model for storing calendar events and agenda items"""
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Calendar integration fields
    external_id = models.CharField(max_length=255, blank=True, null=True, help_text="External calendar event ID")
    calendar_source = models.CharField(max_length=50, blank=True, null=True, help_text="Source calendar (apple, google, etc.)")
    
    class Meta:
        ordering = ['start_time']
        
    def __str__(self):
        return f"{self.title} ({self.start_time.strftime('%Y-%m-%d %H:%M')})"
    
    @property
    def duration(self):
        """Return event duration in minutes"""
        return int((self.end_time - self.start_time).total_seconds() / 60)
    
    @property
    def is_past(self):
        """Check if event is in the past"""
        return self.end_time < timezone.now()


class CalendarConnection(models.Model):
    """Model for storing calendar connection settings"""
    PROVIDER_CHOICES = [
        ('apple', 'Apple Calendar (iCloud)'),
        ('google', 'Google Calendar'),
        ('outlook', 'Outlook Calendar'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, help_text="Connection name")
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    server_url = models.URLField(help_text="CalDAV server URL")
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255, help_text="App-specific password or token")
    is_active = models.BooleanField(default=True)
    last_sync = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
        
    def __str__(self):
        return f"{self.name} ({self.provider})"
