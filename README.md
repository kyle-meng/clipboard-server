<div align="center">
  <img src="static/favicon.png" alt="Logo" width="100"/>
  <h1>🔗 局域网剪贴板 (LAN Clipboard Server)</h1>

  <p>一个极其轻量、基于 Flask 打造的现代化局域网剪贴板同步工具。在同一工作网络下实现手机、平板、电脑间文本、图片和文件的无缝传输。</p>

  ![Python Badge](https://img.shields.io/badge/Python-3.8+-blue?logo=python&logoColor=white)
  ![Flask Badge](https://img.shields.io/badge/Flask-Web_Framework-green?logo=flask)
  ![Windows Badge](https://img.shields.io/badge/Supported-Windows-00a2ed?logo=windows)
</div>

<hr/>

## ✨ 核心特性 / Features

🚀 **多端实时同步：** 支持一键获取和推送文本剪贴板内容，附带多达 20 条带时间戳的历史记录查看功能。  
📷 **极速图像抓取：** 直接从系统的剪贴板读取位图，并在页面端自动建立历史微缩图图库并支持点击无损放大。  
📁 **文件极速互传：** 打破硬件界限，所有连接至同局域网的设备均可畅快高速上传与下载各类文件格式。  
🎨 **现代 UI 及体验：** 全新适配的卡片式美学响应式页面配合一键 “点击复制 (Click-to-Copy)” 机制。  
🔒 **基础安全防护：** 拥有独立的访问二次验证界面（通过 `.env` 分离管理配置）。  
🖥️ **原生系统集成：** 启动后静默挂载于 Windows 系统右下角托盘（Tray），支持菜单弹出局域网访问专属连接二维码图。

---

## ⚙️ 环境与开发配置 / Development

### 1. 基础依赖环境安装
请确保本地已配置好 Python 基础环境，然后在命令行项目根路径下执行：
```bash
pip install -r requirements.txt
```

### 2. 核心私密配置 (.env)
系统启动会依赖 `.env` 配置文件来配置关键项。如果不存在，将会读取默认值。
你可以在项目根目录下创建 `.env`，内容格式如下：
```env
SECRET_KEY=your_super_secret_key
PASSWORD=123456
MAX_HISTORY=20
```

### 3. 本地运行调试
开发或日常运行服务（直接调起图形化托盘图标）：
```bash
python tray.py
```
> 服务将在后台静默运行，并于右下角托盘常驻。右键点击托盘图标即可打开并扫码访问网页（http://[本机IP]:5000）。

---

## 📦 独立单文件打包部署 / Build

若希望分享给未安装 Python 的其他 Windows 电脑运行，可以依靠 `PyInstaller` 将整个带图形资源的项目打包成单个独立的 `.exe` 可执行文件。

> 注：为了能完美处理局域网访问和静默无控制台环境，请务必使用以下带有 `--windowed` 并且包含资源的完整指令打包。

```bash
python -m PyInstaller --noconfirm --onefile --windowed --add-data "static;static" --icon="static/favicon.ico" tray.py
```
> 🗂️ 运行完成后，你能够在此根目录的 `dist/` 文件夹下找到新鲜生成的 **`tray.exe`** 文件。双击即可在任何机器上一键直接享受服务啦！

---

## 👨‍💻 交互端预览 / Preview Snapshot
一切部署完成后，在电脑或手机的浏览器输入被控制台（或二维码显示）分配的 **局域网IP与端口（如 `http://192.168.x.x:5000`）**：
1. **身份认证：** 在首页输入默认安全密令 `123456`（可于 `.env` 自定义）。
2. **操作面板：** 尽情使用最新的 `Current Content` 进行多端文字拷贝，上传你的照片，在 `File Area` 下载各类工程资料。
