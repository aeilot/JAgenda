from django.contrib import admin
from .models import Event, CalendarConnection

# Register your models here.

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'start_time', 'end_time', 'priority', 'status', 'calendar_source']
    list_filter = ['priority', 'status', 'calendar_source', 'created_at']
    search_fields = ['title', 'description']
    ordering = ['start_time']
    readonly_fields = ['id', 'created_at', 'updated_at']

@admin.register(CalendarConnection)
class CalendarConnectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'provider', 'is_active', 'last_sync', 'created_at']
    list_filter = ['provider', 'is_active']
    search_fields = ['name', 'username']
    readonly_fields = ['id', 'last_sync', 'created_at']
