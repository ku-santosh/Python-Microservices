import os, time, logging, threading
from concurrent import futures
import grpc
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import DictCursor, register_uuid
from flask import Flask, jsonify
# import generated proto modules (must be generated before running)
try:
    import proto.db_service_pb2 as pb2
    import proto.db_service_pb2_grpc as pb2_grpc
except Exception as e:
    pb2 = pb2_grpc = None
    print('Proto modules not found. Please generate them with grpc_tools.protoc. Error:', e)

stage = os.environ.get('STAGE', 'dev')
load_dotenv(dotenv_path=f'.env.{stage}', override=True)

DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = os.environ.get('DB_PORT', '5432')
DB_SCHEMA = os.environ.get('DB_SCHEMA', 'recsui')

GRPC_PORT = int(os.environ.get('DB_SERVICE_PORT', 50051))
HTTP_PORT = int(os.environ.get('DB_SERVICE_HTTP_PORT', 50052))

register_uuid()
logging.basicConfig(level=logging.INFO)

def get_conn_cursor():
    try:
        conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
        cur = conn.cursor(cursor_factory=DictCursor)
        cur.execute(f"SET search_path TO {DB_SCHEMA};")
        print("Successfully connected to the database.")
        return conn, cur
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        raise

class DBServiceServicer(pb2_grpc.DBServiceServicer if pb2_grpc else object):
    def __init__(self):
        # test initial connection
        try:
            conn, cur = get_conn_cursor()
            cur.close(); conn.close()
        except Exception as e:
            logging.error('Initial DB check failed: %s', e)

    def Ping(self, request, context):
        return pb2.Pong(message='pong')

    def CreateUser(self, request, context):
        try:
            conn, cur = get_conn_cursor()
            cur.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s) RETURNING id;", (request.username, request.password_hash))
            conn.commit()
            row = cur.fetchone()
            cur.close(); conn.close()
            return pb2.CreateUserResponse(id=row['id'])
        except Exception as e:
            print(f"Error connecting to the database: {e}")
            return pb2.CreateUserResponse(id=0, error=str(e))

    def GetUserByUsername(self, request, context):
        try:
            conn, cur = get_conn_cursor()
            cur.execute("SELECT id, username, password_hash FROM users WHERE username = %s;", (request.username,))
            row = cur.fetchone()
            cur.close(); conn.close()
            if not row:
                return pb2.GetUserResponse(error='not_found')
            return pb2.GetUserResponse(id=row['id'], username=row['username'], password_hash=row['password_hash'])
        except Exception as e:
            print(f"Error connecting to the database: {e}")
            return pb2.GetUserResponse(error=str(e))

    def CreateProduct(self, request, context):
        try:
            conn, cur = get_conn_cursor()
            cur.execute("INSERT INTO products (name, price) VALUES (%s, %s) RETURNING id;", (request.name, request.price))
            conn.commit()
            row = cur.fetchone()
            cur.close(); conn.close()
            return pb2.CreateProductResponse(id=row['id'])
        except Exception as e:
            print(f"Error connecting to the database: {e}")
            return pb2.CreateProductResponse(id=0, error=str(e))

    def ListProducts(self, request, context):
        try:
            conn, cur = get_conn_cursor()
            cur.execute("SELECT id, name, price FROM products ORDER BY id;")
            rows = cur.fetchall()
            cur.close(); conn.close()
            products = [pb2.Product(id=r['id'], name=r['name'], price=float(r['price'])) for r in rows]
            return pb2.ListProductsResponse(products=products)
        except Exception as e:
            print(f"Error connecting to the database: {e}")
            context.set_details(str(e)); context.set_code(grpc.StatusCode.INTERNAL)
            return pb2.ListProductsResponse()

    def CreateOrder(self, request, context):
        try:
            conn, cur = get_conn_cursor()
            cur.execute("INSERT INTO orders (user_id, product_id, quantity, status) VALUES (%s, %s, %s, %s) RETURNING id;", (request.user_id, request.product_id, request.quantity, 'created'))
            conn.commit()
            row = cur.fetchone()
            cur.close(); conn.close()
            return pb2.CreateOrderResponse(id=row['id'])
        except Exception as e:
            print(f"Error connecting to the database: {e}")
            return pb2.CreateOrderResponse(id=0, error=str(e))

    def ListOrders(self, request, context):
        try:
            conn, cur = get_conn_cursor()
            cur.execute("SELECT id, user_id, product_id, quantity, status FROM orders WHERE user_id = %s ORDER BY id;", (request.user_id,))
            rows = cur.fetchall()
            cur.close(); conn.close()
            orders = [pb2.Order(id=r['id'], user_id=r['user_id'], product_id=r['product_id'], quantity=int(r['quantity']), status=r['status']) for r in rows]
            return pb2.ListOrdersResponse(orders=orders)
        except Exception as e:
            print(f"Error connecting to the database: {e}")
            context.set_details(str(e)); context.set_code(grpc.StatusCode.INTERNAL)
            return pb2.ListOrdersResponse()

def serve_grpc():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    if pb2_grpc:
        pb2_grpc.add_DBServiceServicer_to_server(DBServiceServicer(), server)
    port = f'[::]:{GRPC_PORT}'
    server.add_insecure_port(port)
    server.start()
    print(f'gRPC DB service listening on {GRPC_PORT}')
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

# small HTTP health server for quick checks
flask_app = Flask(__name__)
@flask_app.route('/health', methods=['GET'])
def health():
    try:
        conn, cur = get_conn_cursor()
        cur.close(); conn.close()
        return jsonify({'ok': True, 'message': 'Successfully connected to the database.'}), 200
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

if __name__ == '__main__':
    # start grpc in thread and http in main thread
    t = threading.Thread(target=serve_grpc, daemon=True)
    t.start()
    print(f'HTTP health endpoint listening on {HTTP_PORT}')
    flask_app.run(host='0.0.0.0', port=HTTP_PORT)
