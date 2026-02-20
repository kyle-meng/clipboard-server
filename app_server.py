
from flask import Flask, request, redirect, render_template_string, session, url_for, send_from_directory
import pyperclip
from datetime import datetime
import os
from PIL import Image, ImageGrab
# import base64
import qrcode
import socket
import sys

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

DATA_DIR = os.path.join(BASE_DIR, "clipboard_data")
FILES_DIR = os.path.join(DATA_DIR, "files")
IMAGES_DIR = os.path.join(DATA_DIR, "images")

os.makedirs(FILES_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

def get_lan_ip():
    """获取局域网 IP 地址"""
    try:
        # 连接一个外网地址但不发送数据，用于获取本机 LAN IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def print_qr(url):
    qr = qrcode.QRCode(box_size=2, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    qr.print_ascii()  # 终端显示


app = Flask(__name__)
app.secret_key = 'your_super_secret_key'
PASSWORD = '123211'
MAX_HISTORY = 20

clipboard_content = ""
clipboard_history = []

def save_clipboard_image():
    try:
        image = ImageGrab.grabclipboard()
        if isinstance(image, Image.Image):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"img_{timestamp}.png"
            filepath = os.path.join(IMAGES_DIR, filename)
            image.save(filepath, "PNG")
            return filename
    except Exception as e:
        print("未检测到剪贴板图像或读取失败:", e)
    return None

def get_image_history():
    if not os.path.exists(IMAGES_DIR):
        return []
    files = sorted(os.listdir(IMAGES_DIR))[-5:]
    return [{'time': f, 'src': url_for('serve_image', filename=f)} for f in files]

def get_file_list():
    if not os.path.exists(FILES_DIR):
        return []
    return sorted(os.listdir(FILES_DIR))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ''
    if request.method == 'POST':
        if request.form.get('password') == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            error = '密码错误'
    return render_template_string(login_template, error=error)

@app.before_request
def require_login():
    if request.endpoint not in ('login', 'static', 'serve_image', 'serve_file', 'get_clipboard', 'api_set_clipboard'):
        if not session.get('logged_in'):
            return redirect(url_for('login'))

@app.route("/", methods=["GET"])
def index():
    image_list = get_image_history()
    file_list = get_file_list()
    return render_template_string(html_template,
        content=clipboard_content,
        history=clipboard_history[::-1],
        image_list=image_list,
        file_list=file_list
    )

@app.route("/set_clipboard", methods=["POST"])
def set_clipboard():
    global clipboard_content
    content = request.form.get("content", "")
    if content:
        clipboard_content = content
        pyperclip.copy(content)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        clipboard_history.append((timestamp, content))
        if len(clipboard_history) > MAX_HISTORY:
            clipboard_history.pop(0)
    save_clipboard_image()
    return redirect(url_for('index'))

@app.route("/get_clipboard", methods=["GET"])
def get_clipboard():
    return clipboard_content

@app.route("/api/set_clipboard", methods=["POST"])
def api_set_clipboard():
    global clipboard_content
    content = request.form.get("content", "")
    if content:
        clipboard_content = content
        pyperclip.copy(content)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        clipboard_history.append((timestamp, content))
        if len(clipboard_history) > MAX_HISTORY:
            clipboard_history.pop(0)
        save_clipboard_image()
        return "OK"
    return "No content", 400

@app.route("/upload_file", methods=["POST"])
def upload_file():
    uploaded_file = request.files.get("file")
    if uploaded_file and uploaded_file.filename != '':
        filename = uploaded_file.filename.replace('\\', '/').split('/')[-1]
        save_path = os.path.join(FILES_DIR, filename)
        uploaded_file.save(save_path)
    return redirect(url_for('index'))

@app.route('/files/<filename>')
def serve_file(filename):
    return send_from_directory(FILES_DIR, filename)

@app.route('/images/<filename>')
def serve_image(filename):
    return send_from_directory(IMAGES_DIR, filename)

html_template = """<!doctype html>
<html><head><meta charset="utf-8"><title>局域网剪贴板</title>
<style>
body { font-family: sans-serif; max-width: 800px; margin: auto; padding: 2rem; background: #f9f9f9; }
textarea { width: 100%; height: 150px; font-size: 1em; }
pre { white-space: pre-wrap; border: 1px solid #ccc; background: #fff; padding: 1rem; }
.history { background: #eee; padding: 1rem; border-radius: 5px; margin-top: 2rem; }
.history-item { margin-bottom: 1rem; padding-bottom: 1rem; border-bottom: 1px dashed #bbb; }
.time { color: #888; font-size: 0.9em; }
input[type=submit] { padding: 0.5rem 1rem; font-size: 1em; margin-top: 0.5rem; }
</style></head><body>
<h1>📋 局域网剪贴板中心</h1>
<h3>当前内容：</h3><pre>{{ content }}</pre>
<h3>更新剪贴板：</h3>
<form method="post" action="/set_clipboard"><textarea name="content">{{ content }}</textarea><br>
<input type="submit" value="更新"></form>

{% if image_list %}
<h3>📷 最近图片</h3>
{% for img in image_list %}
<div class="image-box">
<div class="time">{{ img.time }}</div>
<img src="{{ img.src }}" style="max-width: 200px;"><br></div>
{% endfor %}
{% endif %}

<div class="history"><h3>🕒 剪贴板历史：</h3>
{% for item in history %}
<div class="history-item"><div class="time">{{ item[0] }}</div><div><pre>{{ item[1] }}</pre></div></div>
{% endfor %}
</div>

<h3>📁 上传文件</h3>
<form action="/upload_file" method="post" enctype="multipart/form-data">
<input type="file" name="file">
<input type="submit" value="上传"></form>

<h3>📂 文件列表</h3>
<ul>
{% for file in file_list %}
<li><a href="{{ url_for('serve_file', filename=file) }}">{{ file }}</a></li>
{% endfor %}
</ul>

</body></html>"""

login_template = """<!doctype html>
<html><head><meta charset="utf-8"><title>登录</title></head>
<body><h2>🔐 登录</h2>
<form method="post">
<input type="password" name="password" placeholder="输入密码">
<input type="submit" value="登录">
{% if error %}<div style="color:red;">{{ error }}</div>{% endif %}
</form></body></html>"""

# if __name__ == "__main__":
#     print("启动 Flask 服务中…")
#     app.run(host="localhost", port=6000)
def main():
    lan_ip = get_lan_ip()
    url = f"http://{lan_ip}:5000"
    print(f"📌 服务已启动，局域网访问地址: {url}")
    print_qr(url)
    app.run(host="0.0.0.0", port=5000)    
# if __name__ == "__main__":
#     lan_ip = get_lan_ip()
#     url = f"http://{lan_ip}:5000"
#     print(f"📌 服务已启动，局域网访问地址: {url}")
#     print_qr(url)
#     app.run(host="0.0.0.0", port=5000)

# main()
