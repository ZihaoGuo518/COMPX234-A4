import socket
import threading
import base64
import os
import random
import sys

BUFFER_SIZE = 4096
PORT_RANGE = (50000, 51000)
CHUNK_SIZE = 1000  # bytes

def handle_client(filename, client_addr, control_socket):
    # 选择一个空闲端口用于数据传输
    data_port = random.randint(*PORT_RANGE)
    data_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data_socket.bind(('', data_port))
    
    try:
        if not os.path.exists(filename):
            msg = f"ERR {filename} NOT_FOUND"
            control_socket.sendto(msg.encode(), client_addr)
            return
        
        file_size = os.path.getsize(filename)
        msg = f"OK {filename} SIZE {file_size} PORT {data_port}"
        control_socket.sendto(msg.encode(), client_addr)

        with open(filename, 'rb') as f:
            while True:
                try:
                    data_socket.settimeout(10)
                    packet, client = data_socket.recvfrom(BUFFER_SIZE)
                    text = packet.decode()
                    if text.startswith("FILE") and "GET" in text:
                        parts = text.strip().split()
                        start = int(parts[4])
                        end = int(parts[6])
                        f.seek(start)
                        data = f.read(end - start + 1)
                        encoded = base64.b64encode(data).decode()
                        response = f"FILE {filename} OK START {start} END {end} DATA {encoded}"
                        data_socket.sendto(response.encode(), client)

                    elif text.startswith("FILE") and "CLOSE" in text:
                        response = f"FILE {filename} CLOSE_OK"
                        data_socket.sendto(response.encode(), client)
                        break
                except socket.timeout:
                    break
    finally:
        data_socket.close()

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 UDPserver.py <port>")
        return

    server_port = int(sys.argv[1])
    control_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    control_socket.bind(('', server_port))

    print(f"Server listening on port {server_port}...")

    while True:
        msg, client_addr = control_socket.recvfrom(BUFFER_SIZE)
        text = msg.decode()
        if text.startswith("DOWNLOAD"):
            filename = text.strip().split()[1]
            thread = threading.Thread(target=handle_client, args=(filename, client_addr, control_socket))
            thread.start()

if __name__ == "__main__":
    main()