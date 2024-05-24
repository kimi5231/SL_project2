import requests
import json
import re
from bs4 import BeautifulSoup


class Malangie:
    def __init__(self):
        self.running = True
        self.last_commend = ''
        self.p = re.compile(r'\d')
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
            self.last_commend = 'commend'
            send_text = """
1. 메타: 현 시즌 추천 메타 목록을 보여줍니다.
2. 종료: 프로그램을 종료합니다.
            """
            self.send_message(chat_id, send_text)
        elif text == '메타':
            self.process_meta_commend(chat_id)
        elif text in self.meta_and_link.keys():
            self.process_meta_name_commend(chat_id)
        elif self.p.search(text):
            if self.last_commend == 'commend':
                if text == '1':
                    self.process_meta_commend(chat_id)
                elif text == '2':
                    self.running = False
            elif self.last_commend == 'meta':
                if 0 < int(text) < len(self.meta) + 1:
                    self.process_meta_name_commend(chat_id)
        elif text == '종료':
            self.running = False

    def process_meta_commend(self, chat_id):
        self.last_commend = 'meta'
        send_text = ''
        i = 1
        for t in self.meta_and_link.keys():
            send_text += f'{i}. {t}\n'
            i += 1
        send_text += '\n\n정보를 알고 싶은 메타의 이름을 입력해주세요.'
        self.send_message(chat_id, send_text)

    def process_meta_name_commend(self, chat_id):
        self.last_commend = 'meta name'
        send_text = """
1. 배치표: 추천 메타의 레벨별 배치표를 보여줍니다.
2. 증강체: 추천 메타에 맞는 증강체를 등급별로 보여줍니다.
3. 렙업: 스테이지별 렙업 추천을 보여줍니다. 
4. 챔피언: 추천 메타에 포함되는 챔피언의 목록을 보여줍니다.
5. 주요 아이템: 추천 메타의 주요 아이템과 아이템을 끼는 챔피언의 목룍을 보여줍니다.
6. 챔피언 이름: 해당 챔피언이 아이템을 끼는 챔피언일 경우 주요 아이템 목룍을 보여줍니다.
                                """
        self.send_message(chat_id, send_text)

    def send_message(self, chat_id, text):
        r = requests.get(f'{self.url}/sendMessage', params={'chat_id': chat_id, 'text': text})
        if r.ok:
            print(json.dumps(r.json()['result'], indent=2, ensure_ascii=False))
        else:
            print(f'FAIL:{r.json()}')