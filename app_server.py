
from flask import Flask, request, redirect, render_template_string, session, url_for, send_from_directory
import pyperclip
from datetime import datetime
import os
from PIL import Image, ImageGrab
# import base64
import qrcode
import socket
import sys
from dotenv import load_dotenv

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

load_dotenv(os.path.join(BASE_DIR, '.env'))

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
app.secret_key = os.getenv('SECRET_KEY', 'your_super_secret_key')
PASSWORD = os.getenv('PASSWORD', '123456')
try:
    MAX_HISTORY = int(os.getenv('MAX_HISTORY', 20))
except ValueError:
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
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>局域网剪贴板</title>
    <style>
        :root {
            --primary: #4ade80;
            --primary-hover: #22c55e;
            --bg: #f8fafc;
            --card-bg: #ffffff;
            --text-main: #1e293b;
            --text-muted: #64748b;
            --border: #e2e8f0;
        }
        body { 
            font-family: 'Segoe UI', system-ui, sans-serif; 
            max-width: 800px; 
            margin: 0 auto; 
            padding: 20px; 
            background: var(--bg);
            color: var(--text-main);
            line-height: 1.5;
        }
        h1, h3 { color: var(--text-main); }
        h1 { text-align: center; margin-bottom: 2rem; color: #0f172a; }
        .card {
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        }
        textarea { 
            width: 100%; 
            height: 120px; 
            font-size: 1rem; 
            padding: 10px;
            border: 1px solid var(--border);
            border-radius: 8px;
            box-sizing: border-box;
            resize: vertical;
            margin-bottom: 10px;
            font-family: inherit;
        }
        pre { 
            white-space: pre-wrap; 
            word-wrap: break-word;
            background: #f1f5f9; 
            padding: 15px; 
            border-radius: 8px;
            font-family: inherit;
            font-size: 0.95rem;
            margin: 0;
            min-height: 20px;
        }
        .content-box {
            position: relative;
        }
        .copy-btn {
            position: absolute;
            top: 10px;
            right: 10px;
            background: #e2e8f0;
            color: var(--text-main);
            border: none;
            padding: 6px 12px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.85rem;
            transition: all 0.2s;
        }
        .copy-btn:hover { background: #cbd5e1; }
        .history-item { 
            margin-bottom: 15px; 
            padding-bottom: 15px; 
            border-bottom: 1px dashed var(--border); 
        }
        .history-item:last-child { border-bottom: none; margin-bottom: 0; padding-bottom: 0; }
        .time { color: var(--text-muted); font-size: 0.85rem; margin-bottom: 5px; }
        button.primary-btn, input[type=submit] { 
            background: var(--primary); 
            color: white; 
            border: none; 
            padding: 10px 20px; 
            font-size: 1rem; 
            font-weight: 500;
            border-radius: 8px; 
            cursor: pointer; 
            transition: background 0.2s;
        }
        button.primary-btn:hover, input[type=submit]:hover { background: var(--primary-hover); }
        .image-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 15px; }
        .image-box img { max-width: 100%; height: auto; border-radius: 8px; border: 1px solid var(--border); transition: transform 0.2s; }
        .image-box img:hover { transform: scale(1.03); }
        ul.file-list { list-style: none; padding: 0; margin: 0; }
        ul.file-list li { margin-bottom: 10px; }
        ul.file-list a { 
            display: flex;
            align-items: center;
            background: #f1f5f9;
            padding: 12px 15px;
            border-radius: 8px;
            text-decoration: none;
            color: #2563eb;
            font-weight: 500;
            transition: background 0.2s;
        }
        ul.file-list a::before { content: '📄'; margin-right: 8px; }
        ul.file-list a:hover { background: #e2e8f0; }
        .upload-form { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
        input[type=file] { flex-grow: 1; padding: 5px; }
        @media (max-width: 600px) {
            body { padding: 10px; }
            .card { padding: 15px; }
            .upload-form { flex-direction: column; align-items: stretch; }
        }
    </style>
</head>
<body>
    <h1>📋 局域网剪贴板中心</h1>
    
    <div class="card">
        <h3>✨ 当前内容</h3>
        <div class="content-box">
            <pre id="current-content">{{ content }}</pre>
            <button class="copy-btn" onclick="copyText(this, 'current-content')">复制</button>
        </div>
    </div>

    <div class="card">
        <h3>✏️ 更新剪贴板</h3>
        <form method="post" action="/set_clipboard">
            <textarea name="content" placeholder="输入你想同步的文字内容...">{{ content }}</textarea>
            <input type="submit" value="提交更新">
        </form>
    </div>

    {% if image_list %}
    <div class="card">
        <h3>📷 最近图片 (点击查看大图)</h3>
        <div class="image-grid">
            {% for img in image_list %}
            <div class="image-box">
                <div class="time">{{ img.time }}</div>
                <a href="{{ img.src }}" target="_blank">
                    <img src="{{ img.src }}" loading="lazy" alt="clipboard image">
                </a>
            </div>
            {% endfor %}
        </div>
    </div>
    {% endif %}

    <div class="card">
        <h3>🕒 剪贴板历史</h3>
        {% for item in history %}
        <div class="history-item">
            <div class="time">{{ item[0] }}</div>
            <div class="content-box">
                <pre id="hist-{{ loop.index }}">{{ item[1] }}</pre>
                <button class="copy-btn" onclick="copyText(this, 'hist-{{ loop.index }}')">复制</button>
            </div>
        </div>
        {% else %}
        <div style="color:var(--text-muted)">暂无历史记录</div>
        {% endfor %}
    </div>

    <div class="card">
        <h3>📁 上传文件</h3>
        <form class="upload-form" action="/upload_file" method="post" enctype="multipart/form-data">
            <input type="file" name="file" required>
            <input type="submit" value="上传文件">
        </form>
    </div>

    <div class="card">
        <h3>📂 文件列表</h3>
        <ul class="file-list">
        {% for file in file_list %}
            <li><a href="{{ url_for('serve_file', filename=file) }}" target="_blank">{{ file }}</a></li>
        {% else %}
            <li style="color:var(--text-muted)">服务器暂无文件</li>
        {% endfor %}
        </ul>
    </div>

    <script>
        function copyText(buttonDOM, elementId) {
            const textToCopy = document.getElementById(elementId).innerText;
            if (navigator.clipboard) {
                navigator.clipboard.writeText(textToCopy).then(() => {
                    showSuccess(buttonDOM);
                }).catch(err => {
                    console.error('Failed to copy: ', err);
                    fallbackCopy(textToCopy, buttonDOM);
                });
            } else {
                fallbackCopy(textToCopy, buttonDOM);
            }
        }
        
        function fallbackCopy(text, buttonDOM) {
            const textArea = document.createElement("textarea");
            textArea.value = text;
            textArea.style.position = "fixed";
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            try {
                document.execCommand('copy');
                showSuccess(buttonDOM);
            } catch (err) {
                alert('复制失败，请手动复制');
            }
            document.body.removeChild(textArea);
        }

        function showSuccess(buttonDOM) {
            const originalText = buttonDOM.innerText;
            const originalBg = buttonDOM.style.background;
            const originalColor = buttonDOM.style.color;
            
            buttonDOM.innerText = '已复制!';
            buttonDOM.style.background = '#22c55e';
            buttonDOM.style.color = 'white';
            
            setTimeout(() => {
                buttonDOM.innerText = originalText;
                buttonDOM.style.background = originalBg;
                buttonDOM.style.color = originalColor;
            }, 2000);
        }
    </script>
</body>
</html>
"""

login_template = """<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>登录 - 局域网剪贴板</title>
    <style>
        body { font-family: 'Segoe UI', system-ui, sans-serif; background: #f8fafc; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }
        .card { background: white; padding: 2.5rem 2rem; border-radius: 16px; box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1); width: 100%; max-width: 340px; text-align: center; border: 1px solid #e2e8f0; }
        h2 { margin-top: 0; color: #1e293b; }
        input[type=password] { width: 100%; padding: 12px; margin: 15px 0; border: 1px solid #cbd5e1; border-radius: 8px; box-sizing: border-box; font-size: 1rem; outline: none; transition: border-color 0.2s; }
        input[type=password]:focus { border-color: #4ade80; box-shadow: 0 0 0 3px rgba(74, 222, 128, 0.2); }
        input[type=submit] { width: 100%; padding: 12px; background: #4ade80; color: white; border: none; border-radius: 8px; font-size: 1rem; font-weight: 600; cursor: pointer; transition: background 0.2s; }
        input[type=submit]:hover { background: #22c55e; }
        .error { color: #ef4444; margin-top: 15px; font-size: 0.9rem; background: #fef2f2; padding: 10px; border-radius: 6px; border: 1px solid #fecaca; }
    </style>
</head>
<body>
    <div class="card">
        <h2>🔐 验证身份</h2>
        <form method="post">
            <input type="password" name="password" placeholder="请输入访问密码" required autofocus>
            <input type="submit" value="登 录">
            {% if error %}<div class="error">{{ error }}</div>{% endif %}
        </form>
    </div>
</body>
</html>"""


def main():
    lan_ip = get_lan_ip()
    url = f"http://{lan_ip}:5000"
    print(f"📌 服务已启动，局域网访问地址: {url}")
    print_qr(url)
    app.run(host="0.0.0.0", port=5000)    

