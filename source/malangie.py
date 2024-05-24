import requests
import json
from bs4 import BeautifulSoup


class Malangie:
    def __init__(self):
        self.running = True
        self.url = 'https://api.telegram.org/bot6766400298:AAHttzF1j9Jjx5dk5g8ptT2guJsCxQy2F70'
        self.page_url = 'https://lolchess.gg/meta'
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        self.headers = headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'}
        self.get_meta_and_link()

    def get_meta_and_link(self):
        r = requests.get(self.page_url, headers=self.headers)
        r.raise_for_status()

        soup = BeautifulSoup(r.text, 'lxml')
        self.meta = []
        for e in soup.select('[class^="css-1xsl2fm"]'):
            self.meta.append(e.text)
        self.meta.pop(0)
        self.link = []
        for e in soup.select('[class ^="css-1jardaz"] a'):
            self.link.append(e.text)
            print(e['href'])
        self.link.pop(0)

        self.meta_and_link = dict()
        for i in range(len(self.meta)):
            self.meta_and_link.setdefault(self.meta[i], self.link[i])


    def check_update(self, u):
        if 'message' in u:
            msg = u['message']
            chat_id = msg['chat']['id']
            if 'text' in msg:
                text = msg['text']
                self.check_order(text, chat_id)
            else:
                print(json.dumps(msg, indent=2, ensure_ascii=False))


    def check_order(self, text, chat_id):
        if text == '명령어':
            pass
        elif text == '메타':
            send_text = ''
            for t in self.meta_and_link.keys():
                send_text += f'{t}\n'
            self.send_message(chat_id, send_text)
        elif text == '종료':
            self.running = False

    def send_message(self, chat_id, text):
        r = requests.get(f'{self.url}/sendMessage', params={'chat_id': chat_id, 'text': text})
        if r.ok:
            print(json.dumps(r.json()['result'], indent=2, ensure_ascii=False))
        else:
            print(f'FAIL:{r.json()}')