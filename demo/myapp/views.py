from django.shortcuts import render, HttpResponse
from .models import ChatbotData, Product
from django.shortcuts import get_object_or_404

from django.shortcuts import render
from django.core.exceptions import ValidationError
from django.core.files import File
import os
from .forms import ChatbotForm
import pandas as pd
import requests
import json
import redis
from django.views.decorators.csrf import csrf_exempt

from myapp.cache import add_chatbot_data_to_redis  # Import your cache logic function


REDIS_HOST = '192.168.1.19'
REDIS_PORT = 6379
REDIS_PASSWORD = 'password'
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD)

# home page function
def home(request):
    products = Product.objects.all()
    return render(request, 'home.html', {'products': products})

def delete_telegram_webhook(bot_token):
    telegram_api_url = f'https://api.telegram.org/bot{bot_token}/deleteWebhook'
    response = requests.post(telegram_api_url)
    return response.json()

def create_telegram_webhook(bot_token, request):
    # current_domain = request.META['HTTP_HOST']
    current_domain = "https://rnyfa-103-144-175-252.a.free.pinggy.link"
        # Delete existing webhook first
    delete_response = delete_telegram_webhook(bot_token)
    print(delete_response)

    webhook_url = f'{current_domain}/telegram_webhook_endpoint/{bot_token}'
    telegram_api_url = f'https://api.telegram.org/bot{bot_token}/setWebhook?url={webhook_url}'
    print(telegram_api_url)
    response = requests.post(telegram_api_url)
    return response.json()

def process_uploaded_file(uploaded_file, bot_token):
    df = pd.read_excel(uploaded_file)
    total_records = df.shape
    for index, row in df.iterrows():
        question = row['question']
        answer = row['answer']
        ChatbotData.objects.create(bot_token=bot_token, question=question, answer=answer)
        r.hset(f"qna:{bot_token}", question, answer)
    return total_records

def chatbot_page(request):
    if request.method == 'POST':
        form = ChatbotForm(request.POST, request.FILES)

        if form.is_valid():
            bot_token = form.cleaned_data['bot_token']
            uploaded_file = form.cleaned_data['excel_file']
            
            total_records = process_uploaded_file(uploaded_file, bot_token)
            print(f"Total Records are: {total_records}")
                        # Pass the request object to retrieve the current domain
            webhook_response = create_telegram_webhook(bot_token, request)
            result = {'bot_token': bot_token, "total_records" : total_records ,"webhook_response" : webhook_response}
            print(result)
            return render(request, 'success.html', result )

    else:
        form = ChatbotForm()

    return render(request, 'chatbot.html', {'form': form})

def auto_reply(data, bot_token):
    chat_id = data.get("message", {}).get("chat", {}).get("id")
    message_id = data.get("message",{}).get("message_id",{})
    user_id = data.get("message", {}).get("from",{}).get("id",{})
    first_name = data.get("message", {}).get("from",{}).get("first_name", user_id)
    user_name = data.get("message", {}).get("from",{}).get("username",first_name)
    message = data.get("message", {}).get("text", {})
    reply_msg = r.hget(f"qna:{bot_token}", message)
    if reply_msg:
        reply_msg = reply_msg.decode("utf-8")
        to_url = 'https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}&reply_to_message_id={}&parse_mode=HTML'.format(bot_token, chat_id, reply_msg, message_id)
        resp = requests.get(to_url)
    else:
    # Perform a query to get the answer based on the token and question
        try:
            print("checking if answer is available in database.")
            chatbot_data = get_object_or_404(ChatbotData, bot_token=bot_token, question=message)
            reply_msg = chatbot_data.answer
            to_url = 'https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}&reply_to_message_id={}&parse_mode=HTML'.format(bot_token, chat_id, reply_msg, message_id)
            resp = requests.get(to_url)
        except Exception as e:
            print(e)



@csrf_exempt
def dynamic_telegram_webhook(request, bot_token):
    print(type(request.body))
    if request.method == 'POST':
        if request.body is not dict:
            data = json.loads(request.body)
            print(data)
        else:
            data = request.body
        auto_reply(data,bot_token)
        return HttpResponse(status=200)
    return HttpResponse("OK")
