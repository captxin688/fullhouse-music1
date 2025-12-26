from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "I'm alive! The bot is running."

def run():
  # Render จะส่ง Port มาให้ทาง Environment Variable หรือใช้ Default 8080
  app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()