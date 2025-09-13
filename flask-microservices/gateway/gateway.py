from flask import Flask, request, Response
import requests
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

SERVICES = {
    'products': 'http://products:5000',
    'orders': 'http://orders:5000',
    'auth': 'http://auth:5000'
}

@app.route('/<service>/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy(service, path):
    base = SERVICES.get(service)
    if not base:
        return {'error': 'Unknown service'}, 404
    url = f"{base}/{path}"
    resp = requests.request(
        method=request.method,
        url=url,
        headers={key: value for key, value in request.headers if key != 'Host'},
        json=request.get_json(silent=True),
        params=request.args
    )
    return Response(resp.content, status=resp.status_code, headers=dict(resp.headers))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=Config.PORT)
