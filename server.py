from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
import json
import sqlite3

BASE_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = (BASE_DIR / "scripts").resolve()

FORM_HTML = BASE_DIR / "form.html"
FORM_JS = SCRIPTS_DIR / "form.js"
VIEW_HTML = BASE_DIR / "view.html"
VIEW_JS = SCRIPTS_DIR / "view.js"
MANAGE_HTML = BASE_DIR / "manage.html"
MANAGE_JS = SCRIPTS_DIR / "manage.js"

DB_PATH = BASE_DIR / "expenses.db"


def init_db() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                date TEXT NOT NULL,
                amount INTEGER NOT NULL
            )
            """
        )
        conn.commit()


def get_all_expenses() -> list[dict]:
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT id, content, date, amount FROM expenses ORDER BY date DESC, id DESC"
        ).fetchall()
        return [dict(row) for row in rows]


def create_expense(content: str, date: str, amount: int) -> dict:
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            "INSERT INTO expenses (content, date, amount) VALUES (?, ?, ?)",
            (content, date, amount),
        )
        conn.commit()
        row = conn.execute(
            "SELECT id, content, date, amount FROM expenses WHERE id = ?",
            (cursor.lastrowid,),
        ).fetchone()
        return dict(row)


def delete_expense(expense_id: int) -> bool:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        conn.commit()
        return cursor.rowcount > 0


class ExpenseHandler(BaseHTTPRequestHandler):
    def send_json(self, status_code: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_file(self, file_path: Path, content_type: str, allowed_root: Path) -> None:
        resolved = file_path.resolve()
        if not resolved.is_relative_to(allowed_root) or not resolved.is_file():
            self.send_error(404, f"{file_path.name} not found")
            return
        data = resolved.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def read_json_body(self) -> dict | None:
        try:
            length = int(self.headers.get("Content-Length", 0))
        except ValueError:
            return None
        if length <= 0:
            return None
        raw = self.rfile.read(length).decode("utf-8")
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            return None
        return parsed if isinstance(parsed, dict) else None

    def do_GET(self) -> None:
        path = urlparse(self.path).path

        if path == "/form":
            self.send_file(FORM_HTML, "text/html; charset=utf-8", BASE_DIR)

        elif path == "/scripts/form.js":
            self.send_file(FORM_JS, "application/javascript; charset=utf-8", SCRIPTS_DIR)

        elif path == "/view":
            self.send_file(VIEW_HTML, "text/html; charset=utf-8", BASE_DIR)

        elif path == "/scripts/view.js":
            self.send_file(VIEW_JS, "application/javascript; charset=utf-8", SCRIPTS_DIR)

        elif path == "/manage":
            self.send_file(MANAGE_HTML, "text/html; charset=utf-8", BASE_DIR)

        elif path == "/scripts/manage.js":
            self.send_file(MANAGE_JS, "application/javascript; charset=utf-8", SCRIPTS_DIR)

        elif path == "/api/expenses":
            expenses = get_all_expenses()
            self.send_json(200, {"expenses": expenses})

        else:
            self.send_error(404, "Not Found")

    def do_POST(self) -> None:
        path = urlparse(self.path).path

        if path == "/api/expenses":
            body = self.read_json_body()
            if body is None:
                self.send_json(400, {"error": "不正なJSONです"})
                return

            content = str(body.get("content", "")).strip()
            date = str(body.get("date", "")).strip()
            raw_amount = body.get("amount")

            if not content or not date:
                self.send_json(400, {"error": "内容と日時は必須です"})
                return

            if isinstance(raw_amount, bool) or not isinstance(raw_amount, (int, float)):
                self.send_json(400, {"error": "金額は数値で指定してください"})
                return

            amount = int(raw_amount)
            if amount <= 0:
                self.send_json(400, {"error": "金額は1以上で指定してください"})
                return

            created = create_expense(content, date, amount)
            self.send_json(201, {"status": "ok", "expense": created})

        else:
            self.send_error(404, "Not Found")

    def do_DELETE(self) -> None:
        path = urlparse(self.path).path
        prefix = "/api/expenses/"

        if path.startswith(prefix):
            id_part = path[len(prefix):]
            if not id_part.isdigit():
                self.send_json(400, {"error": "IDは整数で指定してください"})
                return

            expense_id = int(id_part)
            deleted = delete_expense(expense_id)
            if not deleted:
                self.send_json(404, {"error": "対象の精算データが見つかりません"})
                return

            self.send_json(200, {"status": "ok", "deleted_id": expense_id})

        else:
            self.send_error(404, "Not Found")


if __name__ == "__main__":
    init_db()
    server = ThreadingHTTPServer(("127.0.0.1", 8000), ExpenseHandler)
    print("サーバー起動: http://127.0.0.1:8000/form")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nサーバーを停止しました")
    finally:
        server.server_close()