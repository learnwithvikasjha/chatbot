from django.db import models
from django.contrib.auth.models import User  # Import the User model if you're using Django's built-in authentication


class ChatbotData(models.Model):
    bot_token = models.CharField(max_length=100)
    question = models.CharField(max_length=255)
    answer = models.CharField(max_length=255)

class UserBotData(models.Model):
    user = models.CharField(max_length=100, null=True)  # Assuming each bot token is associated with a user
    bot_token = models.CharField(max_length=100)


class Product(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    updated_date = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='product_images/')  # Assumes you'll upload images to a 'product_images' directory
    redirect_link = models.CharField(
        blank=True,
        null=True,
        max_length=100,
        choices=[
            ('/chatbot', 'Chatbot Page'),
            ('/other_page', 'Other Page'),
            # Add more pages as needed
        ]
    )

    def __str__(self):
        return self.title
    
class BotOptions(models.Model):
    user = models.CharField(max_length=100, null=True)  # Assuming each bot token is associated with a user
    bot_token = models.CharField(max_length=255, blank=True, null=True)
    bot_status = models.CharField(max_length=100, blank=True, null=True)
    welcome_message = models.CharField(max_length=255, blank=True, null=True)
    enable_auto_reply_one_to_one = models.BooleanField(default=False)
    enable_auto_reply_groups = models.BooleanField(default=False)
    enable_urls = models.TextField(blank=True, null=True)
    delete_messages = models.TextField(blank=True, null=True)
    enable_banning_user = models.BooleanField(default=False)
    max_warn_count = models.IntegerField(blank=True, null=True)
    updated_time = models.DateTimeField(auto_now=True)  # Updated time

    # New field to track updates for each bot_token
    update_count = models.IntegerField(default=0)

