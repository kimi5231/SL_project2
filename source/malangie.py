import requests
import json
import re
import time
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from PIL import ImageGrab


class Malangie:
    def __init__(self):
        self.running = True
        self.last_commend = ''
        self.p = re.compile(r'\d')
        self.url = 'https://api.telegram.org/bot6766400298:AAHttzF1j9Jjx5dk5g8ptT2guJsCxQy2F70'
        self.main_page_url = 'https://lolchess.gg/meta'
        self.current_page_url = ''
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        self.headers = headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'}
        self.get_meta_and_link()

    def get_meta_and_link(self):
        r = requests.get(self.main_page_url, headers=self.headers)
        r.raise_for_status()

        soup = BeautifulSoup(r.text, 'lxml')
        self.meta = []
        for e in soup.select('[class^="css-1xsl2fm"]'):
            self.meta.append(e.text)
        self.meta.pop(0)
        self.meta.pop(-1)
        self.link = []
        for e in soup.select('[class ^="css-1jardaz"] a'):
            self.link.append(e['href'])
        self.link.pop(0)
        self.link.pop(-1)

        self.meta_and_link = dict()
        for i in range(len(self.meta)):
            self.meta_and_link.setdefault(self.meta[i], self.link[i])

    def get_champion_list(self):
        p = sync_playwright().start()
        browser = p.chromium.launch(headless=False).new_context(
            user_agent=self.user_agent,
            viewport={'width': 800, 'height': 800}
        )
        page = browser.new_page()
        page.goto(f'https://lolchess.gg{self.current_page_url}')
        time.sleep(1)
        elms = page.locator('[class^="TabNavItem"]').all()
        elms[5].click()
        time.sleep(1)
        elms = page.locator('[class^="css-wgmjlp"]').all()
        self.current_champion_list = []
        for e in elms:
            self.current_champion_list.append(e.text_content())
        browser.close()
        p.stop()

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
            self.current_page_url = self.meta_and_link[text]
            self.get_champion_list()
        elif text == '배치표' and self.current_page_url != '':
            self.process_batch_commend(chat_id)
        elif text == '증강체' and self.current_page_url != '':
            self.process_reinforce_commend(chat_id)
        elif text == '렙업' and self.current_page_url != '':
            self.process_level_up_commend(chat_id)
        elif text == '챔피언':
            self.process_need_champion_commend(chat_id)
        elif text == '주요 아이템' and self.current_page_url != '':
            self.process_main_item_commend(chat_id)
        elif self.p.search(text):
            if self.last_commend == 'commend':
                if text == '1':
                    self.process_meta_commend(chat_id)
                elif text == '2':
                    self.running = False
            elif self.last_commend == 'meta':
                if 0 < int(text) < len(self.meta) + 1:
                    self.process_meta_name_commend(chat_id)
                    self.current_page_url = self.meta_and_link[self.meta[int(text) - 1]]
                    self.get_champion_list()
            elif self.last_commend == 'meta name':
                if text == '1':
                    self.process_batch_commend(chat_id)
                elif text == '2':
                    self.process_reinforce_commend(chat_id)
                elif text == '3':
                    self.process_level_up_commend(chat_id)
                elif text == '4':
                    self.process_need_champion_commend(chat_id)
                elif text == '5':
                    self.process_main_item_commend(chat_id)
                elif text == '6':
                    self.process_champion_name_commend(chat_id)
            elif self.last_commend == 'batch':
                self.process_level_commend(chat_id, text)
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
5. 주요 아이템: 추천 메타의 주요 아이템과 아이템을 끼는 챔피언의 목록을 보여줍니다.
6. 챔피언 이름: 해당 챔피언이 아이템을 끼는 챔피언일 경우 주요 아이템 목록을 보여줍니다.
                                """
        self.send_message(chat_id, send_text)

    def process_batch_commend(self, chat_id):
        self.last_commend = 'batch'
        send_text = '현재 레벨을 입력해주세요.'
        self.send_message(chat_id, send_text)

    def process_level_commend(self, chat_id, text):
        if 0 < int(text) < 11:
            p = sync_playwright().start()
            browser = p.chromium.launch(headless=False).new_context(
                user_agent=self.user_agent,
                viewport={'width': 800, 'height': 800}
            )
            page = browser.new_page()
            page.goto(f'https://lolchess.gg{self.current_page_url}')
            time.sleep(1)
            page.evaluate('window.scrollTo(0, 700)')
            time.sleep(1)
            elms = page.locator('[class^="TabNavItem"]').all()
            if 0 < int(text) < 6:
                elms[0].click()
            elif int(text) == 6:
                elms[1].click()
            elif int(text) == 7:
                elms[2].click()
            elif int(text) == 8:
                elms[3].click()
            elif int(text) == 9:
                elms[4].click()
            elif int(text) == 10:
                elms[5].click()
            time.sleep(1)
            screenshot = ImageGrab.grab()
            screenshot.save("screenshot.png")
            browser.close()
            p.stop()
            self.send_photo(chat_id)
            self.process_meta_name_commend(chat_id)

    def process_reinforce_commend(self, chat_id):
        r = requests.get(f'https://lolchess.gg{self.current_page_url}', headers=self.headers)
        r.raise_for_status()

        soup = BeautifulSoup(r.text, 'lxml')
        elms = soup.select('[class^="challenger-comment"]')
        send_text = "\n".join(elms[1].get_text(separator='\n').splitlines())
        self.send_message(chat_id, send_text)
        self.process_meta_name_commend(chat_id)

    def process_level_up_commend(self, chat_id):
        r = requests.get(f'https://lolchess.gg{self.current_page_url}', headers=self.headers)
        r.raise_for_status()

        soup = BeautifulSoup(r.text, 'lxml')
        elms = soup.select('[class^="challenger-comment"]')
        text = elms[0].get_text(separator='\n').splitlines()
        for i in range(len(text)):
            if text[i] == '스테이지별 레벨업 추천':
                send_text = '\n'.join(text[i+1:])
        self.send_message(chat_id, send_text)
        self.process_meta_name_commend(chat_id)

    def process_need_champion_commend(self, chat_id):
        send_text = ''
        for i in range(len(self.current_champion_list)):
            send_text += f'{self.current_champion_list[i]}\n'
        self.send_message(chat_id, send_text)
        self.process_meta_name_commend(chat_id)

    def process_main_item_commend(self, chat_id):
        p = sync_playwright().start()
        browser = p.chromium.launch(headless=False).new_context(
            user_agent=self.user_agent,
            viewport={'width': 800, 'height': 800}
        )
        page = browser.new_page()
        page.goto(f'https://lolchess.gg{self.current_page_url}')
        time.sleep(1)
        page.evaluate('window.scrollTo(0, 1300)')
        time.sleep(1)
        screenshot = ImageGrab.grab()
        screenshot.save("screenshot.png")
        self.send_photo(chat_id)
        if self.current_champion_list == None:
            elms = page.locator('[class^="TabNavItem"]').all()
            elms[5].click()
            time.sleep(1)
            elms = page.locator('[class^="css-wgmjlp"]').all()
            self.current_champion_list = []
            for e in elms:
                self.current_champion_list.append(e.text_content())
        browser.close()
        p.stop()

        r = requests.get(f'https://lolchess.gg{self.current_page_url}', headers=self.headers)
        r.raise_for_status()

        soup = BeautifulSoup(r.text, 'lxml')
        elms = soup.select('[class^="challenger-comment"]')
        text = elms[0].get_text(separator='\n').splitlines()
        send_text = ''
        for i in range(len(text)):
            for champ in self.current_champion_list:
                p = re.compile(champ)
                if p.search(text[i]) and not p.search(send_text):
                    send_text += f'{champ}\n'
        self.send_message(chat_id, send_text)
        self.process_meta_name_commend(chat_id)

    def process_champion_name_commend(self, chat_id, champ):
        if self.current_champion_list == None:
            p = sync_playwright().start()
            browser = p.chromium.launch(headless=False).new_context(
                user_agent=self.user_agent,
                viewport={'width': 800, 'height': 800}
            )
            page = browser.new_page()
            page.goto(f'https://lolchess.gg{self.current_page_url}')
            time.sleep(1)
            elms = page.locator('[class^="TabNavItem"]').all()
            elms[5].click()
            time.sleep(1)
            elms = page.locator('[class^="css-wgmjlp"]').all()
            send_text = ''
            self.current_champion_list = []
            for e in elms:
                send_text += f'{e.text_content()}\n'
                self.current_champion_list.append(e.text_content())
            browser.close()
            p.stop()
        if champ in self.current_champion_list:
            r = requests.get(f'https://lolchess.gg{self.current_page_url}', headers=self.headers)
            r.raise_for_status()

            soup = BeautifulSoup(r.text, 'lxml')
            elms = soup.select('[class^="challenger-comment"]')
            text = elms[0].get_text(separator='\n').splitlines()
            for i in range(len(text)):
                p = re.compile(champ)
                if p.search(text[i]):
                    break
                else:
                    return

            for i in range(len(text)):
                if text[i] == '활용 아이템':
                    start = i+1
                if text[i] == '스테이지별 레벨업 추천':
                    end = i

            item_list = text[start:end]

            for i in range(len(item_list)):
                p = re.compile(champ)
                if p.search(item_list[i]):
                    j = i
                    while item_list[j] == '주요 아이템':
                        j += 1
                    send_text = '\n'.join(item_list[i:j])

            self.send_message(chat_id, send_text)
            self.process_meta_name_commend(chat_id)

    def send_message(self, chat_id, text):
        r = requests.get(f'{self.url}/sendMessage', params={'chat_id': chat_id, 'text': text})
        if r.ok:
            print(json.dumps(r.json()['result'], indent=2, ensure_ascii=False))
        else:
            print(f'FAIL:{r.json()}')

    def send_photo(self, chat_id):
        with open('screenshot.png', 'rb') as photo:
            r = requests.post(f'{self.url}/sendPhoto', data={'chat_id': chat_id}, files={'photo': photo})
            if r.ok:
                print(json.dumps(r.json()['result'], indent=2, ensure_ascii=False))
            else:
                print(f'FAIL:{r.json()}')