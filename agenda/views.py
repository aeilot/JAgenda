from django.shortcuts import render
import openai
from openai import OpenAI

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
    if request.method == "GET":
        user_input = request.GET.get('user_input', '')  # Assumes a form field named 'user_input' in agenda.html
        print(f"DEBUG: request.GET = {request.GET}")
        print(f"DEBUG: user_input = '{user_input}'")


        if user_input:
            # Make OpenAI API request using the shared client
            completion = client.chat.completions.create(
                model="Qwen/QwQ-32B",
                messages=[
                    {"role": "system", "content": "User will give you his schedule. Give time management suggestions."},
                    {"role": "user", "content": user_input}
                ],
            )
            response_text = completion.choices[0].message.content

    return render(request, 'agenda.html', {'response_text': response_text, 'user_input': user_input})