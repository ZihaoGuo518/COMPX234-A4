import base64
import os

def receive_file(filename, host, data_port, size):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(3)
    sock.sendto(f"HELLO FROM CLIENT".encode(), (host, data_port))

    received_chunks = {}
    total_received = 0

    while total_received < size:
        try:
            message, addr = sock.recvfrom(65536)
            msg = message.decode()
            if msg.startswith(f"FILE {filename} OK"):
                parts = msg.split("DATA ")
                header = parts[0].strip().split()
                start = int(header[5])
                end = int(header[7])
                chunk_data = base64.b64decode(parts[1].encode())
                received_chunks[start] = chunk_data
                total_received += len(chunk_data)

                ack = f"FILE {filename} GET START {start} END {end}"
                sock.sendto(ack.encode(), addr)
        except socket.timeout:
            print(f"Timeout during receiving {filename}")
            break

    # 发送 CLOSE
    for _ in range(5):
        sock.sendto(f"FILE {filename} CLOSE".encode(), (host, data_port))
        try:
            msg, _ = sock.recvfrom(4096)
            if msg.decode().strip() == f"FILE {filename} CLOSE_OK":
                break
        except:
            continue

    # 写入文件
    with open(filename, 'wb') as f:
        for offset in sorted(received_chunks.keys()):
            f.write(received_chunks[offset])
    sock.close()
    print(f"Finished downloading {filename}")