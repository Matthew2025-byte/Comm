import argparse, socket, sys

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

parser = argparse.ArgumentParser(description='Socket Server')
parser.add_argument('port', type=int, help='port number')
parser.add_argument('--public', action='store_true', help='public server')

args = parser.parse_args()

if args.public:
    server.bind(('0.0.0.0', args.port))
else:
    server.bind(('localhost', args.port))

server.listen(10)

try:
    while True:
        conn, addr = server.accept()
        conn.sendall('Hello, world!'.encode())
        conn.close()


except KeyboardInterrupt:
    sys.exit()