from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path('chatbot/', views.chatbot_page, name='chatbot'),
    path('telegram_webhook_endpoint/<str:bot_token>', views.dynamic_telegram_webhook, name='dynamic_telegram_webhook'),

]