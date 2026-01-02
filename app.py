from flask import Flask, render_template, jsonify, request
import requests
import time
import urllib3
import json
from datetime import datetime, timedelta

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

OFFLINE_DATA = {
    'bitcoin': [
        [1709251200000, 61500], [1709337600000, 62400], [1709424000000, 63800], 
        [1709510400000, 65200], [1709596800000, 66500], [1709683200000, 67200], 
        [1709769600000, 68500], [1709856000000, 69000], [1709942400000, 68200],
        [1710028800000, 70000], [1710115200000, 71500], [1710201600000, 72000]
    ],
    'ethereum': [
        [1709251200000, 3400], [1709337600000, 3450], [1709424000000, 3500], 
        [1709510400000, 3600], [1709596800000, 3700], [1709683200000, 3800], 
        [1709769600000, 3900], [1709856000000, 3950], [1709942400000, 3920],
        [1710028800000, 4000], [1710115200000, 4050], [1710201600000, 4080]
    ],
    'solana': [
        [1709251200000, 110], [1709337600000, 115], [1709424000000, 120], 
        [1709510400000, 128], [1709596800000, 132], [1709683200000, 135], 
        [1709769600000, 140], [1709856000000, 145], [1709942400000, 142],
        [1710028800000, 148], [1710115200000, 150], [1710201600000, 152]
    ]
}

class CryptoDataManager:
    def __init__(self):
        self.cache = {}
        self.cache_timeout = 60
        
        self.fallback_coins = [
            {'id': 'bitcoin', 'name': 'Bitcoin', 'symbol': 'btc', 'current_price': 67500, 'price_change_percentage_24h': 1.2, 'image': 'https://assets.coingecko.com/coins/images/1/large/bitcoin.png'},
            {'id': 'ethereum', 'name': 'Ethereum', 'symbol': 'eth', 'current_price': 3250, 'price_change_percentage_24h': -0.5, 'image': 'https://assets.coingecko.com/coins/images/279/large/ethereum.png'},
            {'id': 'tether', 'name': 'Tether', 'symbol': 'usdt', 'current_price': 1.0, 'price_change_percentage_24h': 0.0, 'image': 'https://assets.coingecko.com/coins/images/325/large/Tether.png'},
            {'id': 'binancecoin', 'name': 'BNB', 'symbol': 'bnb', 'current_price': 590, 'price_change_percentage_24h': 0.8, 'image': 'https://assets.coingecko.com/coins/images/825/large/bnb-icon2_2x.png'},
            {'id': 'solana', 'name': 'Solana', 'symbol': 'sol', 'current_price': 148, 'price_change_percentage_24h': 3.5, 'image': 'https://assets.coingecko.com/coins/images/4128/large/solana.png'},
            {'id': 'usd-coin', 'name': 'USDC', 'symbol': 'usdc', 'current_price': 1.0, 'price_change_percentage_24h': 0.0, 'image': 'https://assets.coingecko.com/coins/images/6319/large/USD_Coin_icon.png'},
            {'id': 'ripple', 'name': 'XRP', 'symbol': 'xrp', 'current_price': 0.62, 'price_change_percentage_24h': -1.1, 'image': 'https://assets.coingecko.com/coins/images/44/large/xrp-symbol-white-128.png'},
            {'id': 'toncoin', 'name': 'Toncoin', 'symbol': 'ton', 'current_price': 6.8, 'price_change_percentage_24h': 2.1, 'image': 'https://assets.coingecko.com/coins/images/17980/large/ton_symbol.png'},
            {'id': 'dogecoin', 'name': 'Dogecoin', 'symbol': 'doge', 'current_price': 0.16, 'price_change_percentage_24h': 4.2, 'image': 'https://assets.coingecko.com/coins/images/5/large/dogecoin.png'},
            {'id': 'cardano', 'name': 'Cardano', 'symbol': 'ada', 'current_price': 0.45, 'price_change_percentage_24h': -0.8, 'image': 'https://assets.coingecko.com/coins/images/975/large/cardano.png'},
            {'id': 'shiba-inu', 'name': 'Shiba Inu', 'symbol': 'shib', 'current_price': 0.000025, 'price_change_percentage_24h': 1.5, 'image': 'https://assets.coingecko.com/coins/images/11939/large/shiba.png'},
            {'id': 'avalanche-2', 'name': 'Avalanche', 'symbol': 'avax', 'current_price': 35.5, 'price_change_percentage_24h': -2.3, 'image': 'https://assets.coingecko.com/coins/images/12559/large/Avalanche_Circle_RedWhite_Trans.png'},
            {'id': 'tron', 'name': 'TRON', 'symbol': 'trx', 'current_price': 0.12, 'price_change_percentage_24h': 0.5, 'image': 'https://assets.coingecko.com/coins/images/1094/large/tron-logo.png'},
            {'id': 'polkadot', 'name': 'Polkadot', 'symbol': 'dot', 'current_price': 7.2, 'price_change_percentage_24h': -1.5, 'image': 'https://assets.coingecko.com/coins/images/12171/large/polkadot.png'},
            {'id': 'bitcoin-cash', 'name': 'Bitcoin Cash', 'symbol': 'bch', 'current_price': 480, 'price_change_percentage_24h': 1.1, 'image': 'https://assets.coingecko.com/coins/images/780/large/bitcoin-cash-circle.png'},
            {'id': 'chainlink', 'name': 'Chainlink', 'symbol': 'link', 'current_price': 14.5, 'price_change_percentage_24h': 2.8, 'image': 'https://assets.coingecko.com/coins/images/877/large/chainlink-new-logo.png'},
            {'id': 'near', 'name': 'NEAR Protocol', 'symbol': 'near', 'current_price': 6.5, 'price_change_percentage_24h': 3.2, 'image': 'https://assets.coingecko.com/coins/images/10365/large/near.png'},
            {'id': 'matic-network', 'name': 'Polygon', 'symbol': 'matic', 'current_price': 0.72, 'price_change_percentage_24h': -0.4, 'image': 'https://assets.coingecko.com/coins/images/4713/large/matic-token-icon.png'},
            {'id': 'litecoin', 'name': 'Litecoin', 'symbol': 'ltc', 'current_price': 85, 'price_change_percentage_24h': 0.2, 'image': 'https://assets.coingecko.com/coins/images/2/large/litecoin.png'},
            {'id': 'dai', 'name': 'Dai', 'symbol': 'dai', 'current_price': 1.0, 'price_change_percentage_24h': 0.0, 'image': 'https://assets.coingecko.com/coins/images/9956/large/4943.png'},
        ]

    def _get_headers(self):
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate'
        }

    def _map_symbol(self, coin_id):
        mapping = {
            'bitcoin': 'BTC', 'ethereum': 'ETH', 'solana': 'SOL', 'tether': 'USDT',
            'binancecoin': 'BNB', 'ripple': 'XRP', 'dogecoin': 'DOGE', 'cardano': 'ADA',
            'avalanche-2': 'AVAX', 'shiba-inu': 'SHIB', 'polkadot': 'DOT', 'usd-coin': 'USDC',
            'toncoin': 'TON', 'tron': 'TRX', 'bitcoin-cash': 'BCH', 'chainlink': 'LINK',
            'near': 'NEAR', 'matic-network': 'MATIC', 'litecoin': 'LTC', 'dai': 'DAI'
        }
        return mapping.get(coin_id, 'BTC')

    def _fetch_coingecko_chart(self, coin_id, days):
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
        params = {'vs_currency': 'usd', 'days': days}
        try:
            print(f"🌐 1. Trying CoinGecko: {coin_id}...")
            response = requests.get(url, params=params, headers=self._get_headers(), timeout=3, verify=False)
            if response.status_code == 200:
                data = response.json()
                prices = data.get('prices', [])
                if prices: return prices
        except: pass
        return None

    def _fetch_coincap_chart(self, coin_id, days):
        map_id = coin_id
        if coin_id == 'binancecoin': map_id = 'binance-coin'
        
        end_time = int(time.time() * 1000)
        start_time = int((datetime.now() - timedelta(days=int(days))).timestamp() * 1000)
        url = f"https://api.coincap.io/v2/assets/{map_id}/history"
        params = {'interval': 'h1' if days == '1' else 'd1', 'start': start_time, 'end': end_time}
        
        try:
            print(f"🛡️ 2. Trying CoinCap: {map_id}...")
            response = requests.get(url, params=params, headers=self._get_headers(), timeout=3, verify=False)
            if response.status_code == 200:
                data = response.json().get('data', [])
                if data: return [[item['time'], float(item['priceUsd'])] for item in data]
        except: pass
        return None

    def _get_offline_data(self, coin_id, days):
        print(f"💾 Using OFFLINE DATA for {coin_id}")
        
        if coin_id in OFFLINE_DATA:
            return OFFLINE_DATA[coin_id]
        
        base_price = 100
        for c in self.fallback_coins:
            if c['id'] == coin_id:
                base_price = c['current_price']
                break
        
        import math
        end_time = int(time.time() * 1000)
        points = 24 if days == '1' else 30
        interval = 3600 * 1000 if days == '1' else 24 * 3600 * 1000
        
        data = []
        for i in range(points):
            t = end_time - ((points - 1 - i) * interval)
            fluctuation = math.sin(i * 0.5) * 0.02 
            price = base_price * (1 + fluctuation)
            data.append([t, price])
            
        return data

    def get_market_coins(self):
        cache_key = "market_list"
        if self._is_cache_valid(cache_key): return self.cache[cache_key]['data']

        try:
            url = "https://api.coingecko.com/api/v3/coins/markets"
            params = {'vs_currency': 'usd', 'order': 'market_cap_desc', 'per_page': 20, 'page': 1, 'sparkline': 'false'}
            response = requests.get(url, params=params, headers=self._get_headers(), timeout=3, verify=False)
            if response.status_code == 200:
                data = response.json()
                self._save_to_cache(cache_key, data)
                return data
        except: pass
        
        return self.fallback_coins

    def get_coin_chart(self, coin_id, days):
        cache_key = f"chart_{coin_id}_{days}"
        if self._is_cache_valid(cache_key): return self._process_chart_data(self.cache[cache_key]['data'], days)

        prices = self._fetch_coingecko_chart(coin_id, days)
        
        if not prices:
            prices = self._fetch_coincap_chart(coin_id, days)
            
        if not prices:
            prices = self._get_offline_data(coin_id, days)
            
        if prices:
            self._save_to_cache(cache_key, prices)
            return self._process_chart_data(prices, days)
            
        return {'error': 'Critical Failure', 'labels': [], 'prices': []}

    def _is_cache_valid(self, key):
        if key in self.cache:
            if time.time() - self.cache[key]['timestamp'] < self.cache_timeout:
                return True
        return False

    def _save_to_cache(self, key, data):
        self.cache[key] = {'timestamp': time.time(), 'data': data}

    def _process_chart_data(self, prices, days):
        labels = []
        values = []
        for timestamp, price in prices:
            date = datetime.fromtimestamp(timestamp / 1000)
            if days == '1':
                labels.append(date.strftime('%H:%M'))
            else:
                labels.append(date.strftime('%d %b %H:%M'))
            values.append(price)
        return {'labels': labels, 'prices': values}

data_manager = CryptoDataManager()

@app.route('/')
def index():
    coins = data_manager.get_market_coins()
    return render_template('index.html', coins=coins)

@app.route('/get-coin-data')
def get_coin_data():
    coin_id = request.args.get('coin')
    days = request.args.get('days', '7')
    chart_data = data_manager.get_coin_chart(coin_id, days)
    return jsonify(chart_data)

if __name__ == '__main__':
    app.run(debug=True)
