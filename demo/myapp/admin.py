from django.contrib import admin
from .models import ChatbotData , Product, BotOptions, UserBotData

# Register your models here.

admin.site.register(ChatbotData)
admin.site.register(Product)
admin.site.register(BotOptions)
admin.site.register(UserBotData)
