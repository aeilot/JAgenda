"""
URL configuration for jagenda project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from agenda.views import (
    index, agenda, timeline_view, calendar_connections, 
    add_calendar_connection, sync_calendar, events_api, create_event
)

urlpatterns = [
    path('', index, name='index'),
    path('agenda/', agenda, name='agenda'),
    path('timeline/', timeline_view, name='timeline'),
    path('calendar/', calendar_connections, name='calendar_connections'),
    path('calendar/add/', add_calendar_connection, name='add_calendar_connection'),
    path('calendar/sync/<uuid:connection_id>/', sync_calendar, name='sync_calendar'),
    path('api/events/', events_api, name='events_api'),
    path('api/events/create/', create_event, name='create_event'),
    path('admin/', admin.site.urls),
]
