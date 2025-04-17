from flask import Flask, request
from database import log_http_request

app = Flask(__name__)

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def capture_http_request(path):
    ip = request.remote_addr
    user_agent = request.headers.get("User-Agent", "Unknown")
    method = request.method
    log_http_request(ip, user_agent, path, method)
    return "This is a public web server!", 200

def start_http_server(port=8080):
    print(f"HTTP Honeypot running on port {port}")
    app.run(host="0.0.0.0", port=port)
