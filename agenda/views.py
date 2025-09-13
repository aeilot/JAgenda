import pdfplumber
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta
import openai
from openai import OpenAI
import markdown
import json
from .models import Event, CalendarConnection
from .calendar_service import CalendarService, get_apple_calendar_config

# Create your views here.
def index(request):
    return render(request, 'index.html')

# Instantiate OpenAI client once at module level
client = OpenAI(
    base_url="https://api.siliconflow.cn/v1",
    api_key="sk-pqlgknchwqqmkafxqsvdfiiryujimuemsasskrcsmcnyowtu"
)

def agenda(request):
    user_input = ""
    response_text = ""
    if request.method == "POST":
        user_input = request.POST.get('user_input', '')
        pdf_file = request.FILES.get('pdf_file')

        # If PDF uploaded, extract text
        if pdf_file:
            try:
                with pdfplumber.open(pdf_file) as pdf:
                    pdf_text = ""
                    for page in pdf.pages:
                        pdf_text += page.extract_text() or ""
                user_input = pdf_text.strip()
            except Exception as e:
                print(f"PDF parsing error: {e}")
                response_text = "无法识别该PDF内容，请上传文本型PDF或手动输入日程。"
        # Clean input: strip whitespace and remove unwanted characters
        user_input = user_input.strip()
        user_input = ''.join(c for c in user_input if c.isprintable())

        if user_input:
            completion = client.chat.completions.create(
                model="tencent/Hunyuan-MT-7B",
                messages=[
                    {"role": "system", "content": "User will give you his schedule. Give time management suggestions."},
                    {"role": "user", "content": user_input}
                ],
            )
            response_text = completion.choices[0].message.content
            html = markdown.markdown(response_text)
            response_text = html
            print(response_text)

    return render(request, 'agenda.html', {'response_text': response_text, 'user_input': user_input})


def timeline_view(request):
    """Display events in timeline/Gantt chart format"""
    # Get events from the next 30 days
    start_date = timezone.now().date()
    end_date = start_date + timedelta(days=30)
    
    events = Event.objects.filter(
        start_time__date__gte=start_date,
        start_time__date__lte=end_date
    ).order_by('start_time')
    
    # Prepare data for timeline visualization
    timeline_data = []
    for event in events:
        timeline_data.append({
            'id': str(event.id),
            'title': event.title,
            'start': event.start_time.isoformat(),
            'end': event.end_time.isoformat(),
            'priority': event.priority,
            'status': event.status,
            'description': event.description,
            'duration': event.duration,
        })
    
    context = {
        'events': events,
        'timeline_data': json.dumps(timeline_data),
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'timeline.html', context)


def calendar_connections(request):
    """Manage calendar connections"""
    connections = CalendarConnection.objects.all()
    apple_config = get_apple_calendar_config()
    
    context = {
        'connections': connections,
        'apple_config': apple_config,
    }
    
    return render(request, 'calendar_connections.html', context)


def add_calendar_connection(request):
    """Add a new calendar connection"""
    if request.method == 'POST':
        name = request.POST.get('name')
        provider = request.POST.get('provider')
        server_url = request.POST.get('server_url')
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Test connection first
        service = CalendarService()
        test_result = service.test_connection(server_url, username, password)
        
        if test_result['success']:
            # Create connection
            connection = CalendarConnection.objects.create(
                name=name,
                provider=provider,
                server_url=server_url,
                username=username,
                password=password,
            )
            messages.success(request, f'Calendar connection "{name}" added successfully!')
            return redirect('calendar_connections')
        else:
            messages.error(request, f'Connection failed: {test_result["error"]}')
    
    return redirect('calendar_connections')


def sync_calendar(request, connection_id):
    """Sync events from external calendar"""
    if request.method == 'POST':
        try:
            service = CalendarService(connection_id)
            result = service.sync_from_calendar()
            
            if result['success']:
                messages.success(request, f'Successfully imported {result["imported"]} events!')
            else:
                messages.error(request, f'Sync failed: {result["error"]}')
                
        except ValueError as e:
            messages.error(request, str(e))
    
    return redirect('calendar_connections')


def events_api(request):
    """API endpoint for getting events data"""
    start_date = request.GET.get('start', timezone.now().date().isoformat())
    end_date = request.GET.get('end', (timezone.now().date() + timedelta(days=30)).isoformat())
    
    try:
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)
    except ValueError:
        return JsonResponse({'error': 'Invalid date format'}, status=400)
    
    events = Event.objects.filter(
        start_time__date__gte=start_dt.date(),
        start_time__date__lte=end_dt.date()
    ).order_by('start_time')
    
    events_data = []
    for event in events:
        events_data.append({
            'id': str(event.id),
            'title': event.title,
            'start': event.start_time.isoformat(),
            'end': event.end_time.isoformat(),
            'priority': event.priority,
            'status': event.status,
            'description': event.description,
            'calendar_source': event.calendar_source,
            'duration': event.duration,
        })
    
    return JsonResponse({'events': events_data})


def create_event(request):
    """Create a new event"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            event = Event.objects.create(
                title=data['title'],
                description=data.get('description', ''),
                start_time=datetime.fromisoformat(data['start_time']),
                end_time=datetime.fromisoformat(data['end_time']),
                priority=data.get('priority', 'medium'),
                status=data.get('status', 'pending'),
            )
            
            return JsonResponse({
                'success': True,
                'event': {
                    'id': str(event.id),
                    'title': event.title,
                    'start': event.start_time.isoformat(),
                    'end': event.end_time.isoformat(),
                    'priority': event.priority,
                    'status': event.status,
                }
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)