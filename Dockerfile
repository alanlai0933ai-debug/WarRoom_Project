FROM python:3.11-slim

WORKDIR /app

# 🌟 新增：預先建立 /data 目錄並確保權限開放
RUN mkdir -p /data && chmod 777 /data

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["python", "war_room.py"]