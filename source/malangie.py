import requests
import json


class Malangie:
    def __init__(self):
        self.running = True
        self.url = 'https://api.telegram.org/bot6766400298:AAHttzF1j9Jjx5dk5g8ptT2guJsCxQy2F70'

    def check_update(self, u):
        if 'message' in u:
            msg = u['message']
            chat_id = msg['chat']['id']
            if 'text' in msg:
                text = msg['text']
                if text == 'test':
                    self.send_message(chat_id, '테스트')
                elif text == '종료':
                    self.running = False
            else:
                print(json.dumps(msg, indent=2, ensure_ascii=False))

    def send_message(self, chat_id, text):
        r = requests.get(f'{self.url}/sendMessage', params={'chat_id': chat_id, 'text': text})
        if r.ok:
            print(json.dumps(r.json()['result'], indent=2, ensure_ascii=False))
        else:
            print(f'FAIL:{r.json()}')