from django.http import HttpResponse
import pdfplumber
from django.shortcuts import render
from openai import OpenAI

import markdown
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings

# Create your views here.
def index(request):
    return render(request, 'index.html')

# Instantiate OpenAI client once at module level
client = OpenAI(
    base_url="https://api.siliconflow.cn/v1",
    api_key="sk-pqlgknchwqqmkafxqsvdfiiryujimuemsasskrcsmcnyowtu"
)

def agenda(request):
    output = False
    user_input = ""
    response_text = ""
    if request.method == "POST":
        user_input = request.POST.get('user_input', '')
        pdf_file = request.FILES.get('pdf_file')

        # If PDF uploaded, extract text
        if pdf_file:
            try:
                with pdfplumber.open(pdf_file) as pdf:
                    pdf_text = []
                    for page in pdf.pages:
                        pdf_text += page.extract_table()
                user_input = str(pdf_text)
            except Exception as e:
                print(f"PDF parsing error: {e}")
                response_text = "无法识别该PDF内容，请上传文本型PDF或手动输入日程。"
            return render(request, 'agenda.html', {'response_text': response_text, 'user_input': user_input})
        # Clean input: strip whitespace and remove unwanted characters
        user_input = user_input.strip()
        user_input = ''.join(c for c in user_input if c.isprintable())

        if user_input:
            completion = client.chat.completions.create(
                model="Pro/deepseek-ai/DeepSeek-V3.1",
                messages=[
                    {"role": "system", "content": """你是一位专业的学习与时间管理顾问。
任务:
根据我提供的日程安排信息，完成以下两项任务：
提供一份详细、具体、可执行的周度时间管理与学习建议。
生成一份标准的 iCalendar (.ics) 格式的日程文本，以便我能直接导入到日历应用中。
输出格式要求:
时间管理建议: 直接开始分析和建议，无需任何开场白。建议应包括：
识别出关键的空闲时间段。
针对每门课程，建议固定的预习和复习时间。
规划三餐和休息时间。
建议运动和放松的时间安排。
点出日程中的关键繁忙时段，并提出应对策略。
每一行后都需要输出 <br>
分隔符: 输出一个 ---。
iCal 日程: 输出完整的 iCalendar 格式文本，确保可以被正确解析。
                     
补充信息，星期那一栏为 None 说明同上一个；对于上海交通大学
第一节8:00-8:45
第二节8:55-9:40
第三节10:00-10:45
第四节10:55-11:40
第五节12:00-12:45
第六节12:55-13:40
第七节14:00-14:45
第八节14:55-15:40
第九节16:00-16:45
第十节16:55-17:40
第十一节18:00-18:45
第十二节18:55-19:40
第十一、十二、十三节晚上3节连上 18:00-20:20
                     
请严格按照此结构输出，不要添加任何额外的介绍性或总结性文字。现在，请等待我输入我的日程安排。
"""},
                    {"role": "user", "content": user_input}
                ],
            )
            response_text = completion.choices[0].message.content
            print(response_text)
            if "---" in response_text:
                # Split response_text at the separator
                before_sep, after_sep = response_text.split("---", 1)
                ical_content = after_sep.strip()

                # Save ical content to a file
                ical_filename = "agenda.ics"
                ical_path = os.path.join("ical_files", ical_filename)
                full_ical_path = os.path.join(settings.MEDIA_ROOT, ical_path)
                os.makedirs(os.path.dirname(full_ical_path), exist_ok=True)
                with open(full_ical_path, "w", encoding="utf-8") as f:
                    f.write(ical_content)

                # Provide download link as HTML
                download_link = settings.MEDIA_URL + ical_path
                html = markdown.markdown(before_sep)
                response_text = html
                response_text += f'<br><a href="{download_link}" download>下载日程文件 (.ics)</a>'
            else:
                download_link = None
                html = markdown.markdown(response_text)
                response_text = html
            print(response_text)
            output = True

    return render(request, 'agenda.html', {'response_text': response_text, 'user_input': user_input, 'output': output})

def wechat(request):
    user_input = ""
    response_text = ""
    output = False
    if request.method == "POST":
        user_input = request.POST.get('user_input', '')
        user_input = user_input.strip()
        user_input = ''.join(c for c in user_input if c.isprintable())

        if user_input:
            completion = client.chat.completions.create(
                model="Pro/deepseek-ai/DeepSeek-V3.1",
                messages=[
                    {"role": "system", "content": """
**角色:**
你是一位经验丰富、注重细节的专业行政助理。

**任务:**
从我接下来提供的一段杂乱的微信聊天记录中，精准地识别、过滤并整理出所有有效信息。你的目标是生成一份清晰、简洁、可执行的摘要报告。

**处理要求:**
1.  **信息过滤:** 你需要自动忽略所有的闲聊、客套话、表情符号、无关的插科-打诨以及重复性内容。
2.  **信息归类:** 将提取出的有效信息归入以下三个类别：【核心信息摘要】、【待办事项 (Action Items)】和【日程安排】。
3.  **客观准确:** 所有输出内容必须严格基于原文，不得添加任何主观推断或原文未提及的信息。

**输出格式:**
请严格按照以下格式输出，如果某个类别下没有信息，则省略该类别标题。类别标题之后都需要换行，使用<br>。

**【核心信息摘要】**
* 按行，总结所有重要的决定、结论、关键数据（如电话、地址、链接）和通知。每一行后输出<br>换行，每一行首不要输出*
    示例：项目 A 的最终方案已确定为方案二。
    示例：本次活动的负责人是张三（电话：13812345678）。

**【待-办事项 (Action Items)】**
* 按行，列出所有需要执行的具体任务，并明确负责人和截止日期（如果提到）。每一行后输出<br>换行，每一行首不要输出*
    格式: `负责人/相关人: 具体任务内容 (截止日期: YYYY-MM-DD)`
    示例: `@李四: 完成市场调研报告初稿 (截止日期: 2025-09-20)`
    示例: `@所有人: 下班前提交上周工作总结`

**【日程安排】**
* 以标准化的格式，列出所有确定的会议、活动或约会。每一行后输出<br>换行
    格式:
        **活动名称:** [具体活动]
        **日期:** YYYY-MM-DD (星期X)
        **时间:** HH:MM - HH:MM
        **地点:** [地点信息，线上或线下]
        **参与人:** [相关人员]
    示例:
        **活动名称:** 第三季度项目复盘会
        **日期:** 2025-09-18 (星期四)
        **时间:** 14:30 - 16:00
        **地点:** 公司三号会议室
        **参与人:** 项目部全体成员

"""},
                    {"role": "user", "content": user_input}
                ],
            )
            response_text = completion.choices[0].message.content
            html = markdown.markdown(response_text)
            response_text = html
            output = True
            print(response_text)

    return render(request, 'wechat.html', {'response_text': response_text, 'user_input': user_input, 'output': output})