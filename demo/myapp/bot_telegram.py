import redis
import re
import requests
import json

class BotFunctionality:
    def __init__(self, token):
        self.token = token
        self.base_url = f'https://api.telegram.org/bot{token}'
        self.r = redis.Redis(
            host='192.168.1.19',
            port=6379,
            password='password'
        )
        self.allowed_urls_list = ["grafana.com", "bmc.com"]
        print("bot funcationality class initiated.")

    def get_me(self):
        resp = requests.get(f"{self.base_url}/getMe")
        self.bot_id = resp.json()['result']['id']

    def get_user_setting(self,token):
        pass

    def allow_individual_reply(self):
        self.r.sadd(f'approved_chat_ids:{self.token}', str(self.bot_id))


    def call_logger(self, reply_msg):
        to_url = f'{self.base_url}/sendMessage?chat_id={self.bot_id}&text={reply_msg}&parse_mode=HTML'
        resp = requests.get(to_url)

    def find_urls(self, text):
        pattern = r'\b(?:(?:https?|ftp)://|www\.)?[A-Za-z0-9.-]+\.[A-Za-z]{2,}(?:/\S*)?\b'
        return re.findall(pattern, text)

    def user_status(self, chat_id, user_id):
        base_url = f'{self.base_url}/getChatMember'
        data = {"chat_id": chat_id, "user_id": user_id}
        resp = requests.post(base_url, data=data)
        data = resp.json()
        return data["result"]["status"]

    def delete_msg(self, message_id, chat_id):
        data = {"message_id": message_id, "chat_id": chat_id}
        to_url = f'{self.base_url}/deleteMessage'
        resp = requests.post(to_url, data=data)

    def auto_response(self, message):
        return self.r.hget(f"qna:{self.token}", message.lower())

    def reply(self, chat_id, reply_msg, message_id):
        self.call_logger("Inside reply function now...")
        print("inside reply function now")
        if reply_msg:
            reply_msg = reply_msg.decode("utf-8")
            to_url = f'{self.base_url}/sendMessage?chat_id={chat_id}&text={reply_msg}&reply_to_message_id={message_id}&parse_mode=HTML'
            print(to_url)
            resp = requests.get(to_url)
            print(resp)
        self.call_logger("reply function executed successfully")

    def ban_user(self, chat_id, user_id):
        try:
            self.r.hincrby("ban", user_id, 1)
            warn_count = int(self.r.hget("ban", user_id).decode())
            if warn_count >= 5:
                data = {"chat_id": chat_id, "user_id": user_id}
                to_url = f'{self.base_url}/banChatMember'
                resp = requests.post(to_url, data=data)
            return warn_count
        except Exception as e:
            print(e)

    def welcome_new_member(self, item):
        try:
            chat_id = item["chat"]["id"]
            user_id = item["new_chat_member"]["id"]
            message_id = item.get("message", {}).get("message_id", {})
            user_name = item["new_chat_member"].get("first_name", str(user_id))
            title = item["chat"].get("title", "title not available")
            if "vikasjha001_bot" in user_name:
                self.r.hset(f"botaddedin:{self.token}", f"{chat_id}_{user_id}", "{}".format(title))
            else:
                welcome_msg = '''<a href="tg://user?id={}">@{}</a> %0a Thank You for Joining the Group. Please read pinned message and group description before asking anything. '''.format(user_id, user_name)
                to_url = f'{self.base_url}/sendMessage?chat_id={chat_id}&text={welcome_msg}&parse_mode=HTML'
                resp = requests.get(to_url)
            print("finished welcome msg")
            del_message_id = self.r.hget("welcome_user", chat_id)
            self.delete_msg(del_message_id, chat_id)
            self.r.hset("welcome_user", chat_id, message_id)
        except Exception as e:
            self.call_logger(dict)
            self.call_logger(e)
            print(f"error from welcome_new_member function: {e}")

    def update_bot_addedin(self, item):
        try:
            chat_id = item["chat"]["id"]
            user_id = item["from"]["id"]
            user_name = item["from"].get("first_name", str(user_id))
            title = item["chat"].get("title", "title not available")
            self.r.hset(f"botaddedin:{self.token}", f"{chat_id}_{user_id}", "{}".format(title))
        except Exception as e:
            self.call_logger(dict)
            self.call_logger(e)
            print(f"error from welcome_new_member function: {e}")

    def process_bot_added_event(self, data):
        try:
            if 'message' in data and 'new_chat_members' in data['message'] and 'from' in data['message']:
                new_chat_members = data['message']['new_chat_members']
                from_user_id = data['message']['from']['id']
                chat_id = data['message']['chat']['id']
                for member in new_chat_members:
                    if member.get('is_bot') and from_user_id == 350907917:
                        self.r.sadd(f'approved_chat_ids:{self.token}', str(chat_id))
                        print(f"Added chat ID {chat_id} to the approved list in Redis.")
            print("Not a bot added by the specified user ID.")
        except Exception as e:
            print(f"Error processing the event: {e}")

    def leave_unapproved_groups(self, chat_id):
        if self.r.sismember(f'approved_chat_ids:{self.token}', chat_id):
            return 1
        else:
            leave_chat_url = f'{self.base_url}/leaveChat?chat_id={chat_id}'
            leave_response = requests.get(leave_chat_url)
            return 0

    def handle_message(self, data):
        self.get_me()
        # self.allow_individual_reply()
        try:
            if "my_chat_member" in data:
                self.update_bot_addedin(data["my_chat_member"])
            elif "new_chat_member" in data["message"]:
                print("condition is true")
                self.welcome_new_member(data["message"])
                self.process_bot_added_event(data)
            else:
                chat_id = data.get("message", {}).get("chat", {}).get("id")
                message_id = data.get("message", {}).get("message_id", {})
                user_id = data.get("message", {}).get("from", {}).get("id", {})
                first_name = data.get("message", {}).get("from", {}).get("first_name", user_id)
                user_name = data.get("message", {}).get("from", {}).get("username", first_name)
                message = data.get("message", {}).get("text", {})
                print(f"chat_id: {chat_id}, message_id: {message_id}, user_id: {user_id}, first_name: {first_name}, user_name: {user_name}")
                urls = self.find_urls(message)
                has_urls = 1 if len(urls) > 0 else 0
                print("message contains urls") if has_urls == 1 else None
                print("message doesn't contain urls.")
                user_type = self.user_status(chat_id, user_id)
                reply_msg = ""
                if has_urls == 1 and user_type in ("creator", "administrator"):
                    reply_msg = message
                elif has_urls == 1:
                    self.delete_msg(message_id, chat_id)
                    self.ban_user(chat_id, user_id)
                else:
                    reply_msg = self.auto_response(message)
                approved = self.leave_unapproved_groups(chat_id)
                if approved == 1:
                    self.reply(chat_id, reply_msg, message_id)
            return {'statusCode': 200, 'message': 'Received and processed message successfully'}
        except Exception as e:
            self.call_logger(f"error is: {e}")
            print(f"error is:{e}")
            return {'statusCode': 200, 'message': f'{e}'}

