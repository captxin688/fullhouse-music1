# ใช้ Python เวอร์ชัน 3.10 แบบตัวเล็ก (Slim) เพื่อความเบา
FROM python:3.10-slim

# ตั้งค่าโฟลเดอร์ทำงาน
WORKDIR /app

# อัปเดตและติดตั้งโปรแกรมระบบที่จำเป็น (รวมถึง FFmpeg ด้วย!)
# libffi-dev, libnacl-dev จำเป็นสำหรับการเข้ารหัสเสียงใน Discord
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ffmpeg \
    gcc \
    libffi-dev \
    libnacl-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# ก๊อปปี้ไฟล์ requirements.txt เข้าไปก่อน เพื่อลง Library
COPY requirements.txt .

# ลง Library Python
RUN pip install --no-cache-dir -r requirements.txt

# ก๊อปปี้ไฟล์โค้ดทั้งหมดที่เหลือเข้าไป
COPY . .

# คำสั่งรันบอท (ถ้าไฟล์หลักคุณชื่ออื่น ให้แก้ตรง main.py)
CMD ["python", "main.py"]