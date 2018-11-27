import requests
import json
import re
import misc


pattern = r'/\w+'

def parse_text(text):
    crypto = re.search(pattern, text).group()
    return crypto[1:]
    
def get_price(crypto):
    crypto = parse_text(crypto)
    crypto = crypto.upper()
    print(crypto)
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol={}'.format(crypto)
    print(url)
    try:
        r = requests.get(url, headers=misc.headers).json()
        price = r['data'][crypto]['quote']['USD']['price']
        return 'Курс ' + crypto + ' = ' + str(price) + ' $'
    except:
        return "Такой криптовалюты нет. Введите символ криптовалюты"