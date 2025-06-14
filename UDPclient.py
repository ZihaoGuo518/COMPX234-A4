import socket
import sys

def send_and_receive(sock, message, server_addr, timeout=2.0, retries=5):
    for i in range(retries):
        try:
            sock.sendto(message.encode(), server_addr)
            sock.settimeout(timeout * (i + 1))
            data, addr = sock.recvfrom(4096)
            return data.decode().strip()
        except socket.timeout:
            print(f"Timeout {i+1}, retrying...")
    return None

def main():
    if len(sys.argv) != 4:
        print("Usage: python3 UDPclient.py <hostname> <port> <filelist>")
        return

    host = sys.argv[1]
    port = int(sys.argv[2])
    filelist = sys.argv[3]

    with open(filelist) as f:
        files = [line.strip() for line in f]

    for filename in files:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_addr = (host, port)
        response = send_and_receive(client_socket, f"DOWNLOAD {filename}", server_addr)
        if not response:
            print(f"Failed to contact server for {filename}")
            continue
        if response.startswith("ERR"):
            print(f"Error: {response}")
            continue
        parts = response.split()
        size = int(parts[3])
        data_port = int(parts[5])
        receive_file(filename, host, data_port, size)