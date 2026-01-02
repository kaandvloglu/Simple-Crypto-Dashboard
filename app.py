from flask import Flask, render_template, jsonify, request
import requests
import time
from datetime import datetime

app = Flask(__name__)

# --- OOP: Data Management Class ---
class CryptoDataManager:
    def __init__(self):
        """Initializes settings and cache upon class instantiation."""
        self.base_url = "https://api.coingecko.com/api/v3"
        self.cache = {}
        self.cache_timeout = 60 # 60 seconds cache duration
        
        # Fallback Data (Private attribute)
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

    def _fetch_from_api(self, endpoint, params):
        """
        Helper method to make API requests (Internal Method).
        """
        try:
            print(f"🌐 API Request: {endpoint}")
            response = requests.get(f"{self.base_url}{endpoint}", params=params, timeout=5)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                print("⚠️ API Rate Limit (429) Error")
                return None
            else:
                print(f"❌ API Error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Connection Error: {e}")
            return None

    def get_cached_data(self, endpoint, params):
        """
        Main method managing the caching mechanism.
        Checks memory first, otherwise calls API.
        """
        cache_key = f"{endpoint}_{str(params)}"
        current_time = time.time()

        # 1. Cache Check
        if cache_key in self.cache:
            last_update = self.cache[cache_key]['timestamp']
            if current_time - last_update < self.cache_timeout:
                print(f"⚡ Using Cache: {endpoint}")
                return self.cache[cache_key]['data']

        # 2. If no data or expired, fetch from API
        data = self._fetch_from_api(endpoint, params)
        
        if data:
            # Save new data to cache
            self.cache[cache_key] = {'timestamp': current_time, 'data': data}
            return data
        
        # 3. In case of error, use old cache if available
        if cache_key in self.cache:
            print("♻️ Using old cache due to API error.")
            return self.cache[cache_key]['data']
            
        return None

    def get_market_coins(self):
        """Fetches coin list for the main page."""
        data = self.get_cached_data('/coins/markets', params={
            'vs_currency': 'usd', 
            'order': 'market_cap_desc', 
            'per_page': 20, 
            'page': 1, 
            'sparkline': 'false'
        })
        
        # Return fallback list if data cannot be fetched
        return data if data else self.fallback_coins

    def get_coin_chart(self, coin_id, days):
        """Prepares chart data for a specific coin."""
        data = self.get_cached_data(f'/coins/{coin_id}/market_chart', params={
            'vs_currency': 'usd',
            'days': days
        })
        
        if not data:
            return {'error': 'No Data', 'labels': [], 'prices': []}

        # Transform data for Frontend format (Business Logic)
        prices = data.get('prices', [])
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


# --- FLASK APPLICATION ---

# Create an instance of the Manager Class
data_manager = CryptoDataManager()

@app.route('/')
def index():
    # Fetch data using class method
    coins = data_manager.get_market_coins()
    return render_template('index.html', coins=coins)

@app.route('/get-coin-data')
def get_coin_data():
    coin_id = request.args.get('coin')
    days = request.args.get('days', '7')
    
    # Fetch processed chart data using class method
    chart_data = data_manager.get_coin_chart(coin_id, days)
    return jsonify(chart_data)

if __name__ == '__main__':
    app.run(debug=True)