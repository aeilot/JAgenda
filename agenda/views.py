import pdfplumber
from django.shortcuts import render
import openai
from openai import OpenAI
import markdown

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