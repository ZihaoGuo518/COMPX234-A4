import socket
import base64
import sys
import time

BUFFER_SIZE = 8192
MAX_RETRIES = 5
INITIAL_TIMEOUT = 1  # seconds

def send_and_receive(sock, msg, server, timeout=1.0):
    retries = 0
    while retries < MAX_RETRIES:
        sock.sendto(msg.encode(), server)
        sock.settimeout(timeout)
        try:
            data, addr = sock.recvfrom(BUFFER_SIZE)
            return data.decode(), addr
        except socket.timeout:
            retries += 1
            timeout *= 2
            print(f"Retry {retries}: {msg}")
    return None, None

def download_file(filename, server_addr, control_port):
    control_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server = (server_addr, control_port)
    response, _ = send_and_receive(control_socket, f"DOWNLOAD {filename}", server)
    if not response:
        print(f"ERROR: No response for file {filename}")
        return

    if response.startswith("ERR"):
        print(response)
        return

    parts = response.split()
    size = int(parts[3])
    data_port = int(parts[5])

    data_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    with open(filename, 'wb') as f:
        start = 0
        while start < size:
            end = min(start + 999, size - 1)
            request = f"FILE {filename} GET START {start} END {end}"
            resp, _ = send_and_receive(data_socket, request, (server_addr, data_port))
            if resp is None:
                print("Failed to get data block")
                return

            if resp.startswith("FILE") and "OK" in resp:
                encoded_data = resp.split("DATA", 1)[1].strip()
                block = base64.b64decode(encoded_data)
                f.write(block)
                print("*", end="", flush=True)
                start = end + 1
        print()

    # Send CLOSE
    close_msg = f"FILE {filename} CLOSE"
    send_and_receive(data_socket, close_msg, (server_addr, data_port))

def main():
    if len(sys.argv) != 4:
        print("Usage: python3 UDPclient.py <host> <port> <files.txt>")
        return

    host = sys.argv[1]
    port = int(sys.argv[2])
    filelist = sys.argv[3]

    with open(filelist, 'r') as f:
        files = [line.strip() for line in f.readlines()]

    for file in files:
        print(f"Downloading: {file}")
        download_file(file, host, port)

if __name__ == "__main__":
    main()