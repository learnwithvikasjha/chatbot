from django.db import models

class ChatbotData(models.Model):
    bot_token = models.CharField(max_length=100)
    question = models.CharField(max_length=255)
    answer = models.CharField(max_length=255)

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