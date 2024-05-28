import requests
import json
from malangie import Malangie


def pull_update():
    with open('status.json') as f:
        status = json.load(f)

    r = requests.get(f'{malangie_bot.url}/getUpdates', params={'offset': status['last_update_id'] + 1})

    if r.ok:
        assert r.headers['content-type'] == 'application/json'

        updates = r.json()['result']
        if updates:
            for u in updates:
                malangie_bot.check_update(u)
            status['last_update_id'] = updates[-1]['update_id']
            with open('status.json', 'w') as f:
                json.dump(status, f)
    else:
        print(f'FAIL{r.status_code}')


malangie_bot = Malangie()

while malangie_bot.running:
    pull_update()