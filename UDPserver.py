import socket
import os
import sys

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 UDPserver.py <port>")
        return

    port = int(sys.argv[1])
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('', port))
    print(f"UDP server up and listening on port {port}")

    while True:
        data, address = server_socket.recvfrom(1024)
        filename = data.decode()
        print(f"Request received: {filename} from {address}")

        if os.path.exists(filename):
            with open(filename, 'rb') as f:
                file_data = f.read()
            server_socket.sendto(file_data, address)
            print(f"Sent: {filename} ({len(file_data)} bytes)")
        else:
            server_socket.sendto(b'FILE NOT FOUND', address)
            print(f"File not found: {filename}")

if __name__ == "__main__":
    main()