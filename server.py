import argparse
import select, socket


parser = argparse.ArgumentParser(description='Socket Server')
parser.add_argument('port', type=int, help='port number')
parser.add_argument('--public', action='store_true', help='public server')
args = parser.parse_args()


# Create a socket object
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
if args.public:
    server.bind(('0.0.0.0', args.port))
else:
    server.bind(('localhost', args.port))
server.listen()
server.setblocking(False)

connections = [server]

while True:
    readable, _, _ = select.select(connections, [], [])

    for sock in readable:
        if sock is server:
            conn, addr = server.accept()
            print(f"{addr} connected")
            connections.append(conn)
        else:
            data = sock.recv(1024)
            if not data:
                print("client disconnected")
                connections.remove(sock)
                sock.close()
                continue
            print(data.decode())
            for client in connections:
                if client not in (server, sock):
                    client.sendall(data)