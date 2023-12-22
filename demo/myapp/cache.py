from myapp.models import ChatbotData  # Replace 'myapp' with your app name
import redis

def add_chatbot_data_to_redis():
    r = redis.StrictRedis(host='192.168.1.19', port=6379, db=0, password="password")  # Modify these details according to your Redis configuration

    # Get unique bot_tokens from ChatbotData
    unique_bot_tokens = ChatbotData.objects.values_list('bot_token', flat=True).distinct()


    for bot_token in unique_bot_tokens:
        chatbot_data_dict = {}

        # Get ChatbotData for the current bot_token
        chatbot_data_queryset = ChatbotData.objects.filter(bot_token=bot_token)

        # Construct dictionary for current bot_token
        for data in chatbot_data_queryset:
            chatbot_data_dict[data.question] = data.answer

        # Add dictionary data to Redis hash
        hash_key = f'qna:{bot_token}'
        r.hmset(hash_key, chatbot_data_dict)
        print(f"redis loaded: {chatbot_data_dict}")

        # Optionally, set an expiry time for the hash key if needed
        # r.expire(hash_key, 3600)  # Set expiry time in seconds (e.g., 1 hour)
