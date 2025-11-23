#!/usr/bin/env bash
set -euo pipefail

ROOT="perspective-microservices"
ZIP_NAME="perspective-microservices-full-k8s.zip"
UPLOADED_PDF="/mnt/data/refer v1 code and add files there with code here....pdf"
PDF_DEST_NAME="refer_v1_code_and_add_files.pdf"

echo "Creating project structure in ./$ROOT ..."

# Remove existing if present
rm -rf "$ROOT" "$ZIP_NAME"

# Create directories
mkdir -p "$ROOT"/{db-proxy,perspective-service,columnstate-service,filtermodel-service,k8s/dev,k8s/uat,k8s/prod,.github/workflows}
cd "$ROOT"

########################################
# db-proxy
########################################
cat > db-proxy/app.py <<'PY'
import os, json
from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import DictCursor, register_uuid

register_uuid()
DB_NAME = os.getenv("DB_NAME", "skg023")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_SCHEMA = os.getenv("DB_SCHEMA", "recsui")

def get_conn_cursor():
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
    curr = conn.cursor(cursor_factory=DictCursor)
    curr.execute(f"SET search_path TO {DB_SCHEMA};")
    return conn, curr

app = Flask(__name__)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status":"ok"}), 200

@app.route("/perspectives", methods=["GET"])
def get_all_perspectives():
    try:
        conn, curr = get_conn_cursor()
        curr.execute("SELECT * FROM perspectives;")
        rows = curr.fetchall()
        results = []
        for r in rows:
            d = dict(r)
            for col in ("column_state", "sort_model", "filter_model"):
                if d.get(col) is None:
                    d[col] = []
                elif isinstance(d[col], (str, bytes)):
                    try:
                        d[col] = json.loads(d[col])
                    except Exception:
                        pass
            results.append(d)
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        try:
            curr.close()
            conn.close()
        except:
            pass

@app.route("/perspectives/<int:perspective_id>", methods=["GET"])
def get_perspective_by_id(perspective_id):
    try:
        conn, curr = get_conn_cursor()
        curr.execute("SELECT * FROM perspectives WHERE id = %s;", (perspective_id,))
        row = curr.fetchone()
        if not row:
            return jsonify({"message":"not found"}), 404
        d = dict(row)
        for col in ("column_state","sort_model","filter_model"):
            if d.get(col) is None:
                d[col]=[]
            elif isinstance(d[col], (str,bytes)):
                try:
                    d[col] = json.loads(d[col])
                except Exception:
                    pass
        return jsonify(d), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        try:
            curr.close()
            conn.close()
        except:
            pass

@app.route("/perspectives/user/<string:username>", methods=["GET"])
def get_perspective_by_username(username):
    try:
        conn, curr = get_conn_cursor()
        curr.execute("SELECT * FROM perspectives WHERE username = %s;", (username,))
        row = curr.fetchone()
        if not row:
            return jsonify({"message":"not found"}), 404
        d = dict(row)
        for col in ("column_state","sort_model","filter_model"):
            if d.get(col) is None:
                d[col]=[]
            elif isinstance(d[col], (str,bytes)):
                try:
                    d[col] = json.loads(d[col])
                except Exception:
                    pass
        return jsonify(d), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        try:
            curr.close()
            conn.close()
        except:
            pass

@app.route("/perspectives", methods=["POST"])
def create_perspective():
    payload = request.get_json()
    try:
        conn, curr = get_conn_cursor()
        curr.execute(
            "INSERT INTO perspectives (username, layout_name, updated_by, column_state, sort_model, filter_model) VALUES (%s, %s, %s, %s::jsonb, %s::jsonb, %s::jsonb) RETURNING *;",
            (payload["username"], payload["layout_name"], payload["updated_by"], json.dumps(payload.get("column_state", [])), json.dumps(payload.get("sort_model", [])), json.dumps(payload.get("filter_model", [])))
        )
        new = curr.fetchone()
        conn.commit()
        d = dict(new)
        for col in ("column_state","sort_model","filter_model"):
            if d.get(col) is None:
                d[col]=[]
            elif isinstance(d[col], (str,bytes)):
                try:
                    d[col] = json.loads(d[col])
                except Exception:
                    pass
        return jsonify(d), 201
    except Exception as e:
        try:
            conn.rollback()
        except:
            pass
        return jsonify({"error": str(e)}), 500
    finally:
        try:
            curr.close()
            conn.close()
        except:
            pass

@app.route("/perspectives/<int:perspective_id>", methods=["PUT"])
def update_perspective(perspective_id):
    payload = request.get_json()
    try:
        conn, curr = get_conn_cursor()
        update_clauses = []
        params = []
        if "username" in payload:
            update_clauses.append("username=%s"); params.append(payload["username"])
        if "layout_name" in payload:
            update_clauses.append("layout_name=%s"); params.append(payload["layout_name"])
        if "updated_by" in payload:
            update_clauses.append("updated_by=%s"); params.append(payload["updated_by"])
        if "column_state" in payload:
            update_clauses.append("column_state=%s::jsonb"); params.append(json.dumps(payload["column_state"]))
        if "sort_model" in payload:
            update_clauses.append("sort_model=%s::jsonb"); params.append(json.dumps(payload["sort_model"]))
        if "filter_model" in payload:
            update_clauses.append("filter_model=%s::jsonb"); params.append(json.dumps(payload["filter_model"]))
        if not update_clauses:
            return jsonify({"message":"no changes"}), 200
        params.append(perspective_id)
        query = f"UPDATE perspectives SET {', '.join(update_clauses)} WHERE id = %s RETURNING *;"
        curr.execute(query, tuple(params))
        updated = curr.fetchone()
        conn.commit()
        if not updated:
            return jsonify({"message":"not found"}), 404
        d = dict(updated)
        for col in ("column_state","sort_model","filter_model"):
            if d.get(col) is None:
                d[col]=[]
            elif isinstance(d[col], (str,bytes)):
                try:
                    d[col] = json.loads(d[col])
                except Exception:
                    pass
        return jsonify(d), 200
    except Exception as e:
        try:
            conn.rollback()
        except:
            pass
        return jsonify({"error": str(e)}), 500
    finally:
        try:
            curr.close()
            conn.close()
        except:
            pass

@app.route("/perspectives/username/<string:username>", methods=["PUT"])
def update_perspective_by_username(username):
    payload = request.get_json()
    try:
        conn, curr = get_conn_cursor()
        update_clauses = []
        params = []
        if "username" in payload:
            update_clauses.append("username=%s"); params.append(payload["username"])
        if "layout_name" in payload:
            update_clauses.append("layout_name=%s"); params.append(payload["layout_name"])
        if "updated_by" in payload:
            update_clauses.append("updated_by=%s"); params.append(payload["updated_by"])
        if "column_state" in payload:
            update_clauses.append("column_state=%s::jsonb"); params.append(json.dumps(payload["column_state"]))
        if "sort_model" in payload:
            update_clauses.append("sort_model=%s::jsonb"); params.append(json.dumps(payload["sort_model"]))
        if "filter_model" in payload:
            update_clauses.append("filter_model=%s::jsonb"); params.append(json.dumps(payload["filter_model"]))
        if not update_clauses:
            curr.execute("SELECT * FROM perspectives WHERE username=%s;", (username,))
            row = curr.fetchone()
            if not row:
                return jsonify({"message":"not found"}), 404
            d = dict(row)
            for col in ("column_state","sort_model","filter_model"):
                if d.get(col) is None:
                    d[col]=[]
                elif isinstance(d[col], (str,bytes)):
                    try:
                        d[col] = json.loads(d[col])
                    except Exception:
                        pass
            return jsonify(d), 200
        params.append(username)
        query = f"UPDATE perspectives SET {', '.join(update_clauses)} WHERE username = %s RETURNING *;"
        curr.execute(query, tuple(params))
        updated = curr.fetchone()
        conn.commit()
        if not updated:
            return jsonify({"message":"not found"}), 404
        d = dict(updated)
        for col in ("column_state","sort_model","filter_model"):
            if d.get(col) is None:
                d[col]=[]
            elif isinstance(d[col], (str,bytes)):
                try:
                    d[col] = json.loads(d[col])
                except Exception:
                    pass
        return jsonify(d), 200
    except Exception as e:
        try:
            conn.rollback()
        except:
            pass
        return jsonify({"error": str(e)}), 500
    finally:
        try:
            curr.close()
            conn.close()
        except:
            pass

@app.route("/perspectives/<int:perspective_id>", methods=["DELETE"])
def delete_perspective(perspective_id):
    try:
        conn, curr = get_conn_cursor()
        curr.execute("DELETE FROM perspectives WHERE id=%s RETURNING id;", (perspective_id,))
        deleted = curr.fetchone()
        if deleted:
            conn.commit()
            return jsonify({"deleted": True}), 200
        conn.rollback()
        return jsonify({"deleted": False}), 404
    except Exception as e:
        try:
            conn.rollback()
        except:
            pass
        return jsonify({"error": str(e)}), 500
    finally:
        try:
            curr.close()
            conn.close()
        except:
            pass

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
PY

cat > db-proxy/requirements.txt <<'REQ'
Flask==2.3.3
psycopg2-binary==2.9.7
REQ

cat > db-proxy/Dockerfile <<'DOCK'
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
ENV PYTHONUNBUFFERED=1
CMD ["python", "app.py"]
DOCK

########################################
# perspective-service
########################################
cat > perspective-service/app.py <<'PY'
import os
import requests
from flask import Flask, request, jsonify

DB_PROXY_HOST = os.getenv("DB_PROXY_HOST", "db-proxy")
DB_PROXY_PORT = os.getenv("DB_PROXY_PORT", "5000")
DB_PROXY_BASE = f"http://{DB_PROXY_HOST}:{DB_PROXY_PORT}"

app = Flask(__name__)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status":"ok"}), 200

@app.route("/api/v1/perspectives", methods=["GET"])
def get_all_perspectives():
    try:
        r = requests.get(f"{DB_PROXY_BASE}/perspectives", timeout=10)
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/v1/perspectives/<int:pid>", methods=["GET"])
def get_by_id(pid):
    try:
        r = requests.get(f"{DB_PROXY_BASE}/perspectives/{pid}", timeout=10)
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/v1/perspectives/user/<string:username>", methods=["GET"])
def get_by_user(username):
    try:
        r = requests.get(f"{DB_PROXY_BASE}/perspectives/user/{username}", timeout=10)
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/v1/perspectives", methods=["POST"])
def create_perspective():
    payload = request.get_json()
    try:
        r = requests.post(f"{DB_PROXY_BASE}/perspectives", json=payload, timeout=10)
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/v1/perspectives/<int:pid>", methods=["PUT"])
def update_perspective(pid):
    payload = request.get_json()
    try:
        r = requests.put(f"{DB_PROXY_BASE}/perspectives/{pid}", json=payload, timeout=10)
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/v1/perspectives/username/<string:username>", methods=["PUT"])
def update_perspective_by_username(username):
    payload = request.get_json()
    try:
        r = requests.put(f"{DB_PROXY_BASE}/perspectives/username/{username}", json=payload, timeout=10)
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/v1/perspectives/<int:pid>", methods=["DELETE"])
def delete_perspective(pid):
    try:
        r = requests.delete(f"{DB_PROXY_BASE}/perspectives/{pid}", timeout=10)
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5001)))
PY

cat > perspective-service/requirements.txt <<'REQ'
Flask==2.3.3
requests==2.31.0
REQ

cat > perspective-service/Dockerfile <<'DOCK'
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
ENV PYTHONUNBUFFERED=1
CMD ["python", "app.py"]
DOCK

########################################
# columnstate-service
########################################
cat > columnstate-service/app.py <<'PY'
import os
import requests
from flask import Flask, request, jsonify

DB_PROXY_HOST = os.getenv("DB_PROXY_HOST", "db-proxy")
DB_PROXY_PORT = os.getenv("DB_PROXY_PORT", "5000")
DB_PROXY_BASE = f"http://{DB_PROXY_HOST}:{DB_PROXY_PORT}"

app = Flask(__name__)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status":"ok"}), 200

@app.route("/api/v1/column_state/save", methods=["POST"])
def save_column_state():
    payload = request.get_json()
    username = payload.get("username")
    if not username:
        return jsonify({"error":"username required"}), 400
    try:
        r = requests.get(f"{DB_PROXY_BASE}/perspectives/user/{username}", timeout=10)
        if r.status_code == 200:
            resp = requests.put(f"{DB_PROXY_BASE}/perspectives/username/{username}", json=payload, timeout=10)
            return jsonify(resp.json()), resp.status_code
        elif r.status_code == 404:
            resp = requests.post(f"{DB_PROXY_BASE}/perspectives", json=payload, timeout=10)
            return jsonify(resp.json()), resp.status_code
        else:
            return jsonify({"error": "db-proxy fetch error", "detail": r.text}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/v1/column_state/save_single", methods=["POST"])
def save_single():
    payload = request.get_json()
    username = payload.get("username")
    if not username:
        return jsonify({"error":"username required"}), 400
    try:
        r = requests.get(f"{DB_PROXY_BASE}/perspectives/user/{username}", timeout=10)
        if r.status_code == 200:
            existing = r.json()
            incoming = payload.get("column_state")
            if incoming is None:
                return jsonify({"error":"column_state required"}), 400
            incoming_list = incoming if isinstance(incoming, list) else [incoming]
            existing_column_state = existing.get("column_state", [])
            by_name = {c["name"]: c for c in existing_column_state}
            for item in incoming_list:
                name = item["name"]
                item["defaultColumns"] = list(set(item.get("defaultColumns", [])))
                if item.get("default"):
                    for v in by_name.values():
                        v["default"] = False
                if name in by_name:
                    by_name[name].update({
                        "view": item.get("view"),
                        "defaultColumns": item.get("defaultColumns"),
                        "default": item.get("default", False)
                    })
                else:
                    by_name[name] = item
            final_list = list(by_name.values())
            update_payload = {"column_state": final_list}
            if "layout_name" in payload:
                update_payload["layout_name"] = payload["layout_name"]
            if "updated_by" in payload:
                update_payload["updated_by"] = payload["updated_by"]
            resp = requests.put(f"{DB_PROXY_BASE}/perspectives/username/{username}", json=update_payload, timeout=10)
            return jsonify(resp.json()), resp.status_code
        elif r.status_code == 404:
            if not payload.get("layout_name") or not payload.get("updated_by"):
                return jsonify({"error":"layout_name and updated_by required for new perspective"}), 400
            resp = requests.post(f"{DB_PROXY_BASE}/perspectives", json=payload, timeout=10)
            return jsonify(resp.json()), resp.status_code
        else:
            return jsonify({"error": "db-proxy fetch error", "detail": r.text}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/v1/column_state/delete_single", methods=["DELETE"])
def delete_single():
    payload = request.get_json()
    username = payload.get("username")
    name_to_delete = payload.get("column_state_name")
    if not username or not name_to_delete:
        return jsonify({"error":"username and column_state_name required"}), 400
    try:
        r = requests.get(f"{DB_PROXY_BASE}/perspectives/user/{username}", timeout=10)
        if r.status_code != 200:
            return jsonify({"error":"perspective not found"}), 404
        existing = r.json()
        original = existing.get("column_state", [])
        updated = [c for c in original if c.get("name") != name_to_delete]
        if len(updated) == len(original):
            return jsonify({"message":"not found"}), 404
        update_payload = {"column_state": updated}
        resp = requests.put(f"{DB_PROXY_BASE}/perspectives/username/{username}", json=update_payload, timeout=10)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5002)))
PY

cat > columnstate-service/requirements.txt <<'REQ'
Flask==2.3.3
requests==2.31.0
REQ

cat > columnstate-service/Dockerfile <<'DOCK'
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
ENV PYTHONUNBUFFERED=1
CMD ["python", "app.py"]
DOCK

########################################
# filtermodel-service
########################################
cat > filtermodel-service/app.py <<'PY'
import os
import requests
from flask import Flask, request, jsonify

DB_PROXY_HOST = os.getenv("DB_PROXY_HOST", "db-proxy")
DB_PROXY_PORT = os.getenv("DB_PROXY_PORT", "5000")
DB_PROXY_BASE = f"http://{DB_PROXY_HOST}:{DB_PROXY_PORT}"

app = Flask(__name__)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status":"ok"}), 200

@app.route("/api/v1/filter_model/save_single_filter", methods=["POST"])
def save_single_filter():
    payload = request.get_json()
    username = payload.get("username")
    if not username:
        return jsonify({"error":"username required"}), 400
    filters = payload.get("filter_model")
    if filters is None:
        return jsonify({"error":"filter_model required"}), 400
    try:
        r = requests.get(f"{DB_PROXY_BASE}/perspectives/user/{username}", timeout=10)
        if r.status_code == 200:
            existing = r.json()
            existing_filter_model = existing.get("filter_model", [])
            incoming_list = filters if isinstance(filters, list) else [filters]
            by_key = {(f["name"], f["view"]): f for f in existing_filter_model}
            for incoming in incoming_list:
                key = (incoming["name"], incoming["view"])
                if key in by_key:
                    by_key[key]["filters"] = incoming["filters"]
                    by_key[key]["default"] = incoming["default"]
                else:
                    by_key[key] = incoming
            final_list = list(by_key.values())
            update_payload = {"filter_model": final_list}
            if "layout_name" in payload:
                update_payload["layout_name"] = payload["layout_name"]
            if "updated_by" in payload:
                update_payload["updated_by"] = payload["updated_by"]
            resp = requests.put(f"{DB_PROXY_BASE}/perspectives/username/{username}", json=update_payload, timeout=10)
            return jsonify(resp.json()), resp.status_code
        elif r.status_code == 404:
            if not payload.get("layout_name") or not payload.get("updated_by"):
                return jsonify({"error":"layout_name and updated_by required for new perspective"}), 400
            resp = requests.post(f"{DB_PROXY_BASE}/perspectives", json=payload, timeout=10)
            return jsonify(resp.json()), resp.status_code
        else:
            return jsonify({"error": "db-proxy fetch error", "detail": r.text}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5003)))
PY

cat > filtermodel-service/requirements.txt <<'REQ'
Flask==2.3.3
requests==2.31.0
REQ

cat > filtermodel-service/Dockerfile <<'DOCK'
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
ENV PYTHONUNBUFFERED=1
CMD ["python", "app.py"]
DOCK

########################################
# docker-compose
########################################
cat > docker-compose.yml <<'YAML'
version: "3.9"

services:
  postgres:
    image: postgres:15
    container_name: postgres
    restart: always
    environment:
      POSTGRES_USER: your_db_user
      POSTGRES_PASSWORD: your_db_password
      POSTGRES_DB: skg023
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - appnet

  db-proxy:
    build: ./db-proxy
    container_name: db-proxy
    restart: always
    environment:
      DB_NAME: skg023
      DB_SCHEMA: recsui
      DB_HOST: postgres
      DB_PORT: 5432
      DB_USER: your_db_user
      DB_PASSWORD: your_db_password
    ports:
      - "5000:5000"
    depends_on:
      - postgres
    networks:
      - appnet

  perspective-service:
    build: ./perspective-service
    container_name: perspective-service
    restart: always
    environment:
      DB_PROXY_HOST: db-proxy
      DB_PROXY_PORT: 5000
    ports:
      - "5001:5001"
    depends_on:
      - db-proxy
    networks:
      - appnet

  columnstate-service:
    build: ./columnstate-service
    container_name: columnstate-service
    restart: always
    environment:
      DB_PROXY_HOST: db-proxy
      DB_PROXY_PORT: 5000
    ports:
      - "5002:5002"
    depends_on:
      - db-proxy
    networks:
      - appnet

  filtermodel-service:
    build: ./filtermodel-service
    container_name: filtermodel-service
    restart: always
    environment:
      DB_PROXY_HOST: db-proxy
      DB_PROXY_PORT: 5000
    ports:
      - "5003:5003"
    depends_on:
      - db-proxy
    networks:
      - appnet

volumes:
  pgdata:

networks:
  appnet:
    driver: bridge
YAML

########################################
# init.sql
########################################
cat > init.sql <<'SQL'
-- Create schema if not exists
CREATE SCHEMA IF NOT EXISTS recsui;

-- Create table perspectives
CREATE TABLE IF NOT EXISTS recsui.perspectives (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    layout_name VARCHAR(255) NOT NULL,
    updated_by VARCHAR(255) NOT NULL,
    column_state JSONB DEFAULT '[]',
    sort_model JSONB DEFAULT '[]',
    filter_model JSONB DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_perspectives_username
    ON recsui.perspectives (username);

CREATE INDEX IF NOT EXISTS idx_perspectives_layout
    ON recsui.perspectives (layout_name);

-- Trigger to auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = NOW();
   RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_perspectives_updated_at ON recsui.perspectives;

CREATE TRIGGER update_perspectives_updated_at
BEFORE UPDATE ON recsui.perspectives
FOR EACH ROW
EXECUTE PROCEDURE update_updated_at_column();

-- Seed Data
INSERT INTO recsui.perspectives (username, layout_name, updated_by, column_state, sort_model, filter_model)
VALUES 
(
    'demo_user',
    'reconciliationsView',
    'admin@demo.com',
    '[{
        "name": "Default001",
        "view": "customerMode",
        "defaultColumns": ["riskEventType", "priority", "businessUnit"],
        "default": true
    }]',
    '[{
        "colId": "priority",
        "sort": "asc"
    }]',
    '[{
        "name": "Filter001",
        "view": "customerMode",
        "filters": {
            "riskEventType": {"type": "contains", "filter": "High"}
        },
        "default": true
    }]'
);

INSERT INTO recsui.perspectives (username, layout_name, updated_by, column_state, sort_model, filter_model)
VALUES 
(
    'test_user',
    'analyticsView',
    'qa@demo.com',
    '[{
        "name": "Analytics001",
        "view": "analyticsMode",
        "defaultColumns": ["cif", "reAmount", "reAmountCurrency"],
        "default": true
    }]',
    '[{
        "colId": "reAmount",
        "sort": "desc"
    }]',
    '[{
        "name": "Filter002",
        "view": "analyticsMode",
        "filters": {
            "reAmount": {"type": "greaterThan", "filter": 10000}
        },
        "default": false
    }]'
);
SQL

########################################
# k8s manifests (dev minimal; uat/prod similar)
########################################
cat > k8s/dev/namespace.yaml <<'YAML'
apiVersion: v1
kind: Namespace
metadata:
  name: dev
YAML

cat > k8s/dev/postgres-deployment.yaml <<'YAML'
apiVersion: v1
kind: Secret
metadata:
  name: postgres-secret
  namespace: dev
type: Opaque
stringData:
  POSTGRES_USER: your_db_user
  POSTGRES_PASSWORD: your_db_password
  POSTGRES_DB: skg023

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: dev
spec:
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15
        env:
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: POSTGRES_USER
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: POSTGRES_PASSWORD
        - name: POSTGRES_DB
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: POSTGRES_DB
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: pgdata
          mountPath: /var/lib/postgresql/data
      volumes:
      - name: pgdata
        emptyDir: {} # dev only; use PVC in prod
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: dev
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
    protocol: TCP
YAML

cat > k8s/dev/db-proxy-deployment.yaml <<'YAML'
apiVersion: v1
kind: ConfigMap
metadata:
  name: db-proxy-config
  namespace: dev
data:
  DB_NAME: skg023
  DB_HOST: postgres
  DB_PORT: "5432"
  DB_SCHEMA: recsui
---
apiVersion: v1
kind: Secret
metadata:
  name: db-proxy-secret
  namespace: dev
type: Opaque
stringData:
  DB_USER: your_db_user
  DB_PASSWORD: your_db_password
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: db-proxy
  namespace: dev
spec:
  replicas: 1
  selector:
    matchLabels:
      app: db-proxy
  template:
    metadata:
      labels:
        app: db-proxy
    spec:
      containers:
      - name: db-proxy
        image: <ACR_NAME>.azurecr.io/db-proxy:dev
        ports:
        - containerPort: 5000
        envFrom:
        - configMapRef:
            name: db-proxy-config
        - secretRef:
            name: db-proxy-secret
---
apiVersion: v1
kind: Service
metadata:
  name: db-proxy
  namespace: dev
spec:
  selector:
    app: db-proxy
  ports:
  - port: 5000
    targetPort: 5000
    protocol: TCP
YAML

cat > k8s/dev/perspective-deployment.yaml <<'YAML'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: perspective-service
  namespace: dev
spec:
  replicas: 1
  selector:
    matchLabels:
      app: perspective-service
  template:
    metadata:
      labels:
        app: perspective-service
    spec:
      containers:
      - name: perspective-service
        image: <ACR_NAME>.azurecr.io/perspective-service:dev
        env:
        - name: DB_PROXY_HOST
          value: db-proxy
        - name: DB_PROXY_PORT
          value: "5000"
        ports:
        - containerPort: 5001
---
apiVersion: v1
kind: Service
metadata:
  name: perspective-service
  namespace: dev
spec:
  selector:
    app: perspective-service
  ports:
  - port: 5001
    targetPort: 5001
    protocol: TCP
YAML

cat > k8s/dev/columnstate-deployment.yaml <<'YAML'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: columnstate-service
  namespace: dev
spec:
  replicas: 1
  selector:
    matchLabels:
      app: columnstate-service
  template:
    metadata:
      labels:
        app: columnstate-service
    spec:
      containers:
      - name: columnstate-service
        image: <ACR_NAME>.azurecr.io/columnstate-service:dev
        env:
        - name: DB_PROXY_HOST
          value: db-proxy
        - name: DB_PROXY_PORT
          value: "5000"
        ports:
        - containerPort: 5002
---
apiVersion: v1
kind: Service
metadata:
  name: columnstate-service
  namespace: dev
spec:
  selector:
    app: columnstate-service
  ports:
  - port: 5002
    targetPort: 5002
    protocol: TCP
YAML

cat > k8s/dev/filtermodel-deployment.yaml <<'YAML'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: filtermodel-service
  namespace: dev
spec:
  replicas: 1
  selector:
    matchLabels:
      app: filtermodel-service
  template:
    metadata:
      labels:
        app: filtermodel-service
    spec:
      containers:
      - name: filtermodel-service
        image: <ACR_NAME>.azurecr.io/filtermodel-service:dev
        env:
        - name: DB_PROXY_HOST
          value: db-proxy
        - name: DB_PROXY_PORT
          value: "5000"
        ports:
        - containerPort: 5003
---
apiVersion: v1
kind: Service
metadata:
  name: filtermodel-service
  namespace: dev
spec:
  selector:
    app: filtermodel-service
  ports:
  - port: 5003
    targetPort: 5003
    protocol: TCP
YAML

cat > k8s/dev/ingress.yaml <<'YAML'
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: microservices-ingress
  namespace: dev
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /$1
spec:
  rules:
  - host: api.dev.myapp.com
    http:
      paths:
      - path: /perspectives/?(.*)
        pathType: Prefix
        backend:
          service:
            name: perspective-service
            port:
              number: 5001
      - path: /columnstate/?(.*)
        pathType: Prefix
        backend:
          service:
            name: columnstate-service
            port:
              number: 5002
      - path: /filtermodel/?(.*)
        pathType: Prefix
        backend:
          service:
            name: filtermodel-service
            port:
              number: 5003
YAML

# copy dev manifests to uat/prod as starting point (you can edit replicas & image tags)
cp k8s/dev/* k8s/uat/
cp k8s/dev/* k8s/prod/

########################################
# CICD skeleton
########################################
cat > .github/workflows/cicd.yml <<'YAML'
name: CI/CD

on:
  push:
    branches: [ main ]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Build & push images (placeholder)
        run: |
          echo "Build & push your images to ACR here (use azure/login action and az acr build/push)."

      - name: Deploy to AKS
        run: |
          echo "kubectl apply -f k8s/\${{ github.ref == 'refs/heads/main' && 'prod' || 'dev' }}"
YAML

########################################
# deploy.sh + README.md
########################################
cat > deploy.sh <<'SH'
#!/bin/bash
set -e

ACR_NAME="youracrname"
AKS_RESOURCE_GROUP="your-rg"
AKS_CLUSTER_NAME="your-aks"
NAMESPACE="${NAMESPACE:-dev}"
TAG="${NAMESPACE}"

echo "🚀 Building Docker images..."
docker build -t $ACR_NAME.azurecr.io/db-proxy:$TAG ./db-proxy
docker build -t $ACR_NAME.azurecr.io/perspective-service:$TAG ./perspective-service
docker build -t $ACR_NAME.azurecr.io/columnstate-service:$TAG ./columnstate-service
docker build -t $ACR_NAME.azurecr.io/filtermodel-service:$TAG ./filtermodel-service

echo "📦 Pushing images to ACR..."
az acr login --name $ACR_NAME
docker push $ACR_NAME.azurecr.io/db-proxy:$TAG
docker push $ACR_NAME.azurecr.io/perspective-service:$TAG
docker push $ACR_NAME.azurecr.io/columnstate-service:$TAG
docker push $ACR_NAME.azurecr.io/filtermodel-service:$TAG

echo "🔑 Connecting to AKS cluster..."
az aks get-credentials --resource-group $AKS_RESOURCE_GROUP --name $AKS_CLUSTER_NAME

echo "☸️ Deploying manifests to $NAMESPACE..."
kubectl apply -f k8s/$NAMESPACE/

echo "✅ Deployment complete. Checking pods and services..."
kubectl get pods -n $NAMESPACE
kubectl get svc -n $NAMESPACE
SH
chmod +x deploy.sh

cat > README.md <<'MD'
# Perspective Microservices Project

This project implements a microservices architecture in Python (Flask) with Postgres.
Services:
- db-proxy
- perspective-service
- columnstate-service
- filtermodel-service

Use docker-compose for local dev. Deploy to AKS using k8s manifests.
MD

########################################
# Copy uploaded PDF (if exists)
########################################
if [ -f "$UPLOADED_PDF" ]; then
  echo "Copying uploaded PDF to project root..."
  # sanitize name & copy
  cp "$UPLOADED_PDF" "./$PDF_DEST_NAME"
else
  echo "No uploaded PDF found at $UPLOADED_PDF, skipping copy."
fi

########################################
# Finalize: go back and zip
########################################
cd ..
echo "Creating ZIP $ZIP_NAME ..."
zip -r "$ZIP_NAME" "$ROOT" >/dev/null
echo "Done. Created $ZIP_NAME in $(pwd)"
