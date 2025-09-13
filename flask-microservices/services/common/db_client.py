import os, socket, time
from dotenv import load_dotenv

stage = os.environ.get('STAGE', 'dev')
load_dotenv(dotenv_path=f'.env.{stage}', override=True)

DB_SERVICE_HOST = os.environ.get('DB_SERVICE_HOST', 'db_service')
DB_SERVICE_PORT = int(os.environ.get('DB_SERVICE_PORT', 50051))

def wait_for_db_service(timeout=10):
    host = DB_SERVICE_HOST
    port = DB_SERVICE_PORT
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection((host, port), timeout=2):
                print('Successfully connected to the database service (gRPC host:port).')
                return True
        except Exception as e:
            last = e
            time.sleep(0.5)
    print(f'Error connecting to the database: {last}')
    return False

def get_stub():
    # call wait_for_db_service to print status, stub creation requires generated proto files
    wait_for_db_service()
    try:
        import grpc
        import proto.db_service_pb2_grpc as pb2_grpc
    except Exception as e:
        raise RuntimeError('Proto stubs not generated. Please run protoc to generate proto/db_service_pb2.py and proto/db_service_pb2_grpc.py') from e
    channel = grpc.insecure_channel(f"{DB_SERVICE_HOST}:{DB_SERVICE_PORT}")
    stub = pb2_grpc.DBServiceStub(channel)
    return stub
