# 使用輕量級的 Python 3.11 環境
FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 安裝所需套件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 把專案檔案全部複製進去
COPY . .

# 曝露 NiceGUI 預設的 8080 埠
EXPOSE 8080

# 啟動指令
CMD ["python", "war_room.py"]