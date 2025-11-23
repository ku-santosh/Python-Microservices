import os
import json
from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import DictCursor, register_uuid

register_uuid()

DB_NAME = os.getenv("DB_NAME", "skg023")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_SCHEMA = os.getenv("DB_SCHEMA", "recsui")

def get_conn_cursor():
    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
    )
    curr = conn.cursor(cursor_factory=DictCursor)
    curr.execute(f"SET search_path TO {DB_SCHEMA};")
    return conn, curr

app = Flask(__name__)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

@app.route("/perspectives", methods=["GET"])
def get_all_perspectives():
    conn, curr = None, None
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
        if curr: curr.close()
        if conn: conn.close()

@app.route("/perspectives/<int:perspective_id>", methods=["GET"])
def get_perspective_by_id(perspective_id):
    conn, curr = None, None
    try:
        conn, curr = get_conn_cursor()
        curr.execute("SELECT * FROM perspectives WHERE id = %s;", (perspective_id,))
        row = curr.fetchone()
        if not row:
            return jsonify({"message": "not found"}), 404
        d = dict(row)
        for col in ("column_state", "sort_model", "filter_model"):
            if d.get(col) is None:
                d[col] = []
            elif isinstance(d[col], (str, bytes)):
                try:
                    d[col] = json.loads(d[col])
                except Exception:
                    pass
        return jsonify(d), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if curr: curr.close()
        if conn: conn.close()

@app.route("/perspectives/user/<string:username>", methods=["GET"])
def get_perspective_by_username(username):
    conn, curr = None, None
    try:
        conn, curr = get_conn_cursor()
        curr.execute("SELECT * FROM perspectives WHERE username = %s;", (username,))
        row = curr.fetchone()
        if not row:
            return jsonify({"message": "not found"}), 404
        d = dict(row)
        for col in ("column_state", "sort_model", "filter_model"):
            if d.get(col) is None:
                d[col] = []
            elif isinstance(d[col], (str, bytes)):
                try:
                    d[col] = json.loads(d[col])
                except Exception:
                    pass
        return jsonify(d), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if curr: curr.close()
        if conn: conn.close()

@app.route("/perspectives", methods=["POST"])
def create_perspective():
    payload = request.get_json()
    conn, curr = None, None
    try:
        conn, curr = get_conn_cursor()
        column_state_json = json.dumps(payload.get("column_state", []))
        sort_model_json = json.dumps(payload.get("sort_model", []))
        filter_model_json = json.dumps(payload.get("filter_model", []))
        curr.execute(
            "INSERT INTO perspectives (username, layout_name, updated_by, column_state, sort_model, filter_model) VALUES (%s, %s, %s, %s::jsonb, %s::jsonb, %s::jsonb) RETURNING *;",
            (
                payload["username"],
                payload["layout_name"],
                payload["updated_by"],
                column_state_json,
                sort_model_json,
                filter_model_json,
            ),
        )
        new = curr.fetchone()
        conn.commit()
        d = dict(new)
        for col in ("column_state", "sort_model", "filter_model"):
            if d.get(col) is None:
                d[col] = []
            elif isinstance(d[col], (str, bytes)):
                try:
                    d[col] = json.loads(d[col])
                except Exception:
                    pass
        return jsonify(d), 201
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        if curr: curr.close()
        if conn: conn.close()

@app.route("/perspectives/<int:perspective_id>", methods=["PUT"])
def update_perspective(perspective_id):
    payload = request.get_json()
    conn, curr = None, None
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
            return jsonify({"message": "no changes"}), 200
        params.append(perspective_id)
        query = f"UPDATE perspectives SET {', '.join(update_clauses)} WHERE id = %s RETURNING *;"
        curr.execute(query, tuple(params))
        updated = curr.fetchone()
        conn.commit()
        if not updated:
            return jsonify({"message": "not found"}), 404
        d = dict(updated)
        for col in ("column_state", "sort_model", "filter_model"):
            if d.get(col) is None:
                d[col] = []
            elif isinstance(d[col], (str, bytes)):
                try:
                    d[col] = json.loads(d[col])
                except Exception:
                    pass
        return jsonify(d), 200
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        if curr: curr.close()
        if conn: conn.close()

@app.route("/perspectives/username/<string:username>", methods=["PUT"])
def update_perspective_by_username(username):
    payload = request.get_json()
    conn, curr = None, None
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
            return jsonify({"message": "not found"}), 404
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
        if conn:
            conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        if curr: curr.close()
        if conn: conn.close()

@app.route("/perspectives/<int:perspective_id>", methods=["DELETE"])
def delete_perspective(perspective_id):
    conn, curr = None, None
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
        if conn:
            conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        if curr: curr.close()
        if conn: conn.close()

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 5000))
    app.run(host=host, port=port)
