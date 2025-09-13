# JAgenda

JAgenda is an AI-powered agenda and time management assistant built with Django. It helps users organize schedules, receive smart suggestions, and export their agenda to calendar formats. WeChat chat logs can also be input to extract and summarize key information.

## Features
- **AI Agent**: Get personalized time management suggestions based on your schedule.
- **Agenda Sorting**: Automatically sort and prioritize your daily tasks.
- **PDF Parsing**: Upload a PDF schedule and extract agenda items.
- **Calendar Integration**: Download your schedule as an `.ics` file for Google Calendar, Outlook, or Apple Calendar.
- **WeChat Chat Summarization**: Input WeChat chat logs to extract and summarize key information.
- **Modern UI**: Clean, responsive interface for easy interaction.

## Getting Started

### Prerequisites
- Python 3.12+
- Django 5+
- `openai`, `pdfplumber`, and other dependencies (see `requirements.txt`)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/aeilot/JAgenda.git
   cd JAgenda
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run migrations:
   ```bash
   python manage.py migrate
   ```
4. Start the development server:
   ```bash
   python manage.py runserver
   ```

## Usage
- Visit the homepage to enter or upload your schedule.
- Input your WeChat chats and get summarized information.
- Submit to receive AI-powered suggestions.
- Download your agenda as an `.ics` file for calendar import.

## File Structure
```
JAgenda/
├── agenda/
│   ├── templates/
│   │   └── agenda.html
│   ├── views.py
│   └── ...
├── jagenda/
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── static/
│   └── index.html
├── requirements.txt
├── README.md
└── manage.py
```

## Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## License
MIT

## Acknowledgements
- [Django](https://www.djangoproject.com/)
- [OpenAI](https://openai.com/)
- [PyPDF2](https://pypdf2.readthedocs.io/)
