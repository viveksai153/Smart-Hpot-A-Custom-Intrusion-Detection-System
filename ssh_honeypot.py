import paramiko
import socket
import threading
from database import log_ssh_attempt

class SSHServer(paramiko.ServerInterface):
    def __init__(self, client_ip):
        self.client_ip = client_ip
        self.username = None
        self.password = None
        self.session_open = False  # Track session status

    def check_auth_password(self, username, password):
        self.username = username
        self.password = password
        log_ssh_attempt(self.client_ip, username, password, "LOGIN ATTEMPT")

        if username == "admin" and password == "password12":
            self.session_open = True
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED  # Reject all other credentials

    def check_channel_request(self, kind, chanid):
        if kind == "session" and self.session_open:
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

def handle_ssh_connection(client, addr):
    client_ip = addr[0]
    transport = paramiko.Transport(client)
    host_key = paramiko.RSAKey(filename="ssh_host_key")  # Load the persistent key
    transport.add_server_key(host_key)
    server = SSHServer(client_ip)

    try:
        transport.start_server(server=server)
        chan = transport.accept(20)
        if chan is None:
            return

        if server.session_open:
            chan.send("Welcome to SSH Honeypot!\n")
            while True:
                chan.send("$ ")
                cmd = chan.recv(1024).decode().strip()
                if cmd.lower() == "exit":
                    break
                log_ssh_attempt(client_ip, server.username, server.password, cmd)
                chan.send(f"Command '{cmd}' executed.\n")
        else:
            chan.send("Access Denied.\n")
            chan.close()
    except Exception as e:
        print(f"SSH Connection Error: {e}")
    finally:
        transport.close()

def start_ssh_server(port=2222):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", port))
    server_socket.listen(5)
    print(f"SSH Honeypot running on port {port}")
    while True:
        client, addr = server_socket.accept()
        threading.Thread(target=handle_ssh_connection, args=(client, addr)).start()
