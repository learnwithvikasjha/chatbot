from django.shortcuts import render, HttpResponse
from .models import ChatbotData, Product, UserBotData
from django.shortcuts import get_object_or_404

from django.shortcuts import render
from django.core.exceptions import ValidationError
from django.core.files import File
import os
from .forms import ChatbotForm, BotOptionsForm
import pandas as pd
import requests
import json
import redis
from django.views.decorators.csrf import csrf_exempt

from myapp.cache import add_chatbot_data_to_redis  # Import your cache logic function
from .bot_telegram import BotFunctionality

def bot_options_view(request):
    if request.method == 'POST':
        form = BotOptionsForm(request.POST)
        if form.is_valid():
            form.save()  # Save form data to the database
            # Redirect to a success page or perform other actions
    else:
        form = BotOptionsForm()

    return render(request, 'bot_options.html', {'form': form})

# home page function
def home(request):
    products = Product.objects.all()
    stats = [{"number" : 150, "description" : "Bots Registered", "color": "bg-info"},
             {"number" : 1234150, "description" : "Auto Replied", "color": "bg-success"},
             {"number" : ".1 S", "description" : "Average Reply Duration", "color": "bg-warning"},
             {"number" : 1234150, "description" : "Auto Replied", "color": "bg-success"}
             
             ]
    return render(request, 'home.html', {'products': products, "stats": stats})

# Login page function
def login(request):
    return render(request, 'login.html', {'message': "successfully loaded login page"})

def delete_telegram_webhook(bot_token):
    telegram_api_url = f'https://api.telegram.org/bot{bot_token}/deleteWebhook'
    response = requests.post(telegram_api_url)
    return response.json()

def create_telegram_webhook(bot_token, request):
    # current_domain = request.META['HTTP_HOST']
    current_domain = "https://rnumr-103-144-175-252.a.free.pinggy.link"
        # Delete existing webhook first
    delete_response = delete_telegram_webhook(bot_token)
    print(delete_response)

    webhook_url = f'{current_domain}/telegram_webhook_endpoint/{bot_token}'
    telegram_api_url = f'https://api.telegram.org/bot{bot_token}/setWebhook?url={webhook_url}'
    print(telegram_api_url)
    response = requests.post(telegram_api_url)
    return response.json()

def process_uploaded_file(uploaded_file, user, bot_token):
    r = redis.StrictRedis(host='192.168.1.19', port=6379, db=0, password="password")
    df = pd.read_excel(uploaded_file)
    total_records = df.shape
    UserBotData.objects.create(user=user, bot_token=bot_token)
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
            user = form.cleaned_data['user']
            bot_token = form.cleaned_data['bot_token']
            uploaded_file = form.cleaned_data['excel_file']
            
            total_records = process_uploaded_file(uploaded_file, user, bot_token)
            print(f"Total Records are: {total_records}")
                        # Pass the request object to retrieve the current domain
            webhook_response = create_telegram_webhook(bot_token, request)
            result = {'bot_token': bot_token, "total_records" : total_records ,"webhook_response" : webhook_response}
            print(result)
            return render(request, 'success.html', result )

    else:
        form = ChatbotForm()

    return render(request, 'chatbot.html', {'form': form})

@csrf_exempt
def dynamic_telegram_webhook(request, bot_token):
    print(type(request.body))
    if request.method == 'POST':
        if request.body is not dict:
            data = json.loads(request.body)
            print(data)
        else:
            data = request.body
        bot = BotFunctionality(bot_token)
        bot.handle_message(data)
        return HttpResponse(status=200)
    return HttpResponse("OK")
