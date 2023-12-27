from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path('login/', views.login, name='login'),
    path('chatbot/', views.chatbot_page, name='chatbot'),
    path('telegram_webhook_endpoint/<str:bot_token>', views.dynamic_telegram_webhook, name='dynamic_telegram_webhook'),
    path('bot-options/', views.bot_options_view, name='bot_options'),


]