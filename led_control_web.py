from flask import Flask, render_template_string
import requests

ESP32_IP = "192.168.249.205"
url = f"http://{ESP32_IP}"

app = Flask(__name__)

HTML = """
<html>
  <body style="text-align:center;padding-top:50px;">
    <h1>ESP32 LED Control</h1>
    <a href="/on"><button style="font-size:24px;padding:20px;">ON</button></a>
    <a href="/off"><button style="font-size:24px;padding:20px;">OFF</button></a>
  </body>
</html>
"""

@app.route("/")
def index():
    return HTML

@app.route("/on")
def turn_on():
    requests.get(f"{url}/on")
    return HTML

@app.route("/off")
def turn_off():
    requests.get(f"{url}/off")
    return HTML

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
