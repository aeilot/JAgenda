from django.shortcuts import render
import openai
from openai import OpenAI

# Create your views here.
def index(request):
    return render(request, 'index.html')

def agenda(request):
    user_input = request.POST.get('user_input', '')  # Assumes a form field named 'user_input' in agenda.html

    response_text = ""
    if user_input:
        # Make OpenAI API request
        client = OpenAI(
            base_url="https://api.siliconflow.cn/v1",
            api_key="sk-pqlgknchwqqmkafxqsvdfiiryujimuemsasskrcsmcnyowtu"
        )
        completion = client.chat.completions.create(
            model="Qwen/QwQ-32B",
            messages=[
            {"role": "system", "content": "Talk like a pirate."},
            {"role": "user", "content": user_input}
            ],
        )
        response_text = completion.choices[0].message.content

    return render(request, 'agenda.html', {'response_text': response_text, 'user_input': user_input})