import threading
from ssh_honeypot import start_ssh_server
from http_honeypot import start_http_server
from database import init_db

if __name__ == "__main__":
    init_db()  # Initialize Database
    threading.Thread(target=start_ssh_server, daemon=True).start()
    start_http_server()
