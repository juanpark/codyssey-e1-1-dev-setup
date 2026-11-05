from flask import Flask, request, redirect
from html import escape
import os
import redis

app = Flask(__name__)

# --- configuration from environment (설정과 코드 분리) ---
MODE = os.environ.get("APP_MODE", "dev")       # 화면에 표시할 모드
PORT = int(os.environ.get("PORT", "5000"))     # 서버 포트
REDIS_HOST = os.environ.get("REDIS_HOST", "redis")  # redis 서비스 이름

r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

STYLE = """<style>
  body{font-family:system-ui,-apple-system,sans-serif;max-width:40em;margin:3em auto;padding:0 1em;color:#1c1b22}
  h1{color:#2b50c8}
  .mode{font-size:.8em;color:#888}
  form{display:flex;gap:.5em;margin:1.2em 0}
  input{flex:1;font-size:1em;padding:.5em}
  button{font-size:1em;padding:.5em 1em;cursor:pointer}
  li{margin:.25em 0}
</style>"""


@app.route("/")
def index():
    names = r.lrange("names", 0, -1)                       # read the list from redis
    items = "".join(f"<li>{escape(n)}</li>" for n in names) or "<li><em>아직 없음</em></li>"
    return f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Codyssey E1-1 체크인</title>
{STYLE}
</head><body>
  <h1>🥊 Codyssey E1-1 체크인</h1>
  <p class="mode">MODE: {escape(MODE)}</p>
  <form method="post" action="/add">
    <input name="name" placeholder="이름을 입력하세요" required autofocus>
    <button>저장</button>
  </form>
  <h2>저장된 이름 ({len(names)})</h2>
  <ul>{items}</ul>
</body></html>"""


@app.route("/add", methods=["POST"])
def add():
    name = request.form.get("name", "").strip()
    if name:
        r.rpush("names", name)                             # push into redis
    return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
