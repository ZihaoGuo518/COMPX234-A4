import base64
import time

def start_file_thread(filename, port, client_address):
    with open(filename, 'rb') as f:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.bind(('', port))
        print(f"Started file thread on port {port} for {filename}")

        file_data = f.read()
        CHUNK_SIZE = 1000
        total_size = len(file_data)
        offset = 0

        while offset < total_size:
            end = min(offset + CHUNK_SIZE - 1, total_size - 1)
            chunk = file_data[offset:end+1]
            encoded = base64.b64encode(chunk).decode()
            header = f"FILE {filename} OK START {offset} END {end} DATA {encoded}"
            received = False
            for attempt in range(5):
                server_socket.sendto(header.encode(), client_address)
                server_socket.settimeout(1.5 * (attempt + 1))
                try:
                    req, _ = server_socket.recvfrom(4096)
                    if req.decode().startswith(f"FILE {filename} GET START {offset}"):
                        received = True
                        break
                except socket.timeout:
                    print(f"Timeout waiting for GET, retrying {attempt + 1}/5...")
            if not received:
                print("Giving up on chunk transfer")
                return
            offset = end + 1

        # 等待 CLOSE 消息
        while True:
            try:
                message, _ = server_socket.recvfrom(4096)
                if message.decode().strip() == f"FILE {filename} CLOSE":
                    server_socket.sendto(f"FILE {filename} CLOSE_OK".encode(), client_address)
                    break
            except:
                pass
        server_socket.close()