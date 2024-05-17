import bs4
import requests

url = f'https://lolchess.gg/meta'

headers = {
    'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
}

r = requests.get(url, headers=headers)
r.raise_for_status()