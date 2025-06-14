# 在 main 函数或 if __name__ == "__main__" 块中添加如下逻辑
import socket
import threading
import random
import os

def handle_client_request(filename, client_address):
    # 在此线程中处理 file 传输逻辑（后面步骤会实现）
    pass

def main():
    import sys
    if len(sys.argv) != 2:
        print("Usage: python3 UDPserver.py <port>")
        return

    port = int(sys.argv[1])
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('', port))
    print(f"Server listening on port {port}")

    while True:
        message, client_address = server_socket.recvfrom(4096)
        decoded = message.decode().strip()
        print(f"Received from {client_address}: {decoded}")
        if decoded.startswith("DOWNLOAD "):
            filename = decoded.split()[1]
            file_path = os.path.join(".", filename)
            if not os.path.isfile(file_path):
                response = f"ERR {filename} NOT_FOUND"
                server_socket.sendto(response.encode(), client_address)
                continue
            file_size = os.path.getsize(file_path)
            data_port = random.randint(50000, 51000)
            response = f"OK {filename} SIZE {file_size} PORT {data_port}"
            server_socket.sendto(response.encode(), client_address)
            threading.Thread(target=start_file_thread,
                             args=(filename, data_port, client_address)).start()

def start_file_thread(filename, data_port, client_address):
    # 占位：后续步骤中具体实现
    pass

if __name__ == "__main__":
    main()