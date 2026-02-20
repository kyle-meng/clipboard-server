import threading
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageTk
# import subprocess
import sys
import os
import socket
import qrcode
import tkinter as tk
from app_server import main
def start_server():
    # subprocess.Popen([sys.executable, "app_server.py"])
    main()


def exit_app(icon, item):
    icon.stop()
    os._exit(0)

def get_lan_ip():
    """获取局域网 IP 地址"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def show_qr():
    """在弹窗显示二维码"""
    lan_ip = get_lan_ip()
    url = f"http://{lan_ip}:5000"

    # 生成二维码
    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # 弹窗显示
    window = tk.Tk()
    window.title("访问二维码")
    window.resizable(False, False)
    img_tk = ImageTk.PhotoImage(img)
    label = tk.Label(window, image=img_tk)
    label.pack(padx=10, pady=10)
    tk.Label(window, text=url, fg="blue").pack()
    window.mainloop()

def tray():
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    
    icon_path = os.path.join(base_dir, "static", "favicon.png")
    
    try:
        image = Image.open(icon_path)
    except FileNotFoundError:
        # Fallback if image not found to avoid crash
        image = Image.new('RGB', (64, 64), color=(73, 109, 137))

    menu = Menu(
        MenuItem("展示访问二维码", show_qr),
        MenuItem("退出服务", exit_app)
    )

    icon = Icon("Clipboard Server", image, "局域网剪贴板", menu)
    threading.Thread(target=start_server, daemon=True).start()
    icon.run()

if __name__ == "__main__":
    show_qr()
    tray()
