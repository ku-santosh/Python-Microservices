from flask import Flask, jsonify, request
import requests
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

@app.route('/')
def home():
    return 'Products service'

@app.route('/products', methods=['GET'])
def get_products():
    try:
        r = requests.get(f"{Config.EXTERNAL_BASE}/products")
        r.raise_for_status()
    except requests.RequestException as exc:
        return jsonify({'error': str(exc)}), 502
    payload = r.json()
    products = [
        {
            'id': p['id'],
            'title': p.get('title'),
            'brand': p.get('brand'),
            'price': p.get('price'),
            'description': p.get('description')
        }
        for p in payload.get('products', [])
    ]
    return jsonify({'data': products}), (200 if products else 204)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=Config.PORT)
