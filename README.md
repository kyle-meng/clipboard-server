# 局域网剪贴板

一个基于 Flask 的局域网剪贴板同步工具，支持文本、图片和文件传输。

## 功能

- 实时同步剪贴板内容
- 历史记录查看
- 图片上传与查看
- 文件上传与下载
- 桌面端托盘图标
- 访问二维码展示

## 运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行服务

```bash
python tray.py
```

### 3. 访问

打开浏览器访问 `http://[IP_ADDRESS]:5000`

## 打包

```bash
python -m PyInstaller --noconfirm --onefile --windowed --icon="static/favicon.ico" tray.py
```
