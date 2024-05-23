import requests
import json


def check_update(u):
    if 'message' in u:
        msg = u['message']
        chat_id = msg['chat']['id']
        if 'text' in msg:
            text = msg['text']
            if text == 'test':
                send_message(chat_id, '테스트')
            elif text == '종료':
                global running
                running = False
        else:
            print(json.dumps(msg, indent=2, ensure_ascii=False))


def send_message(chat_id, text):
    r = requests.get(f'{telegram_url}/sendMessage', params={'chat_id': chat_id, 'text': text})
    if r.ok:
        print(json.dumps(r.json()['result'], indent=2, ensure_ascii=False))
    else:
        print(f'FAIL:{r.json()}')


telegram_url = 'https://api.telegram.org/bot6766400298:AAHttzF1j9Jjx5dk5g8ptT2guJsCxQy2F70'

running = True
while(running):
    with open('status.json') as f:
        status = json.load(f)

    r = requests.get(f'{telegram_url}/getUpdates', params={'offset': status['last_update_id'] + 1})

    if r.ok:
        assert r.headers['content-type'] == 'application/json'

        updates = r.json()['result']
        if updates:
            for u in updates:
                check_update(u)
            status['last_update_id'] = updates[-1]['update_id']
            with open('status.json', 'w') as f:
                json.dump(status, f)
    else:
        print(f'FAIL{r.status_code}')



# url = f'https://lolchess.gg/meta'
#
# headers = {
#     'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
# }
#
# r = requests.get(url, headers=headers)
# r.raise_for_status()