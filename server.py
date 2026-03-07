import argparse, socket, json


def accept_conn(conn):
    global connections, message_history
    print(f"New connection from {conn.getpeername()}")
    connections[conn] = {"authenticated": True}
def get_history(conn):
    global message_history
    for msg in message_history:
        conn.sendall((json.dumps({"type": "message", "user": msg["user"], "content": msg["content"]})+"\r\n\r\n").encode())
def authenticate_conn(conn, data):
    global connections, message_history
    user = data["user"]
    password = data["pass"]

    connections[conn] = {"authenticated": True}
    get_history(conn)


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
print(f"Server listening on port {args.port} {'(public)' if args.public else '(localhost)'}")

sockets:dict[int, socket.socket] = {}
connections: dict[socket.socket, dict] = {}
# Structure
# connections = {
#     conn: {
#         "authenticated": bool,
#     },
# }
message_history:list[dict] = []
# Structure
# message_history = [
#     {
#         "user": str,
#         "content": str,
#     },
# ]


server.setblocking(False)
while True:
    try:
        conn, addr = server.accept()
        accept_conn(conn)
    except BlockingIOError:
        pass
    for conn in list(connections.keys()):
        try:
            data = conn.recv(1024)
        except BlockingIOError: continue # No data to read, skip

        # Handle disconnections
        except ConnectionError:
            print(f"{conn.getpeername()} disconnected")
            del connections[conn]
            continue
        if not data:
            print(f"{conn.getpeername()} disconnected")
            del connections[conn]


        else:
            data = json.loads(data.decode())
            if data["type"] == "message" and connections[conn]["authenticated"]:
                message_history.append({"user": data["user"], "content": data["content"]})
                print(f"{data['user']}: {data['content']}")
                for _key, _value in connections.items():
                    if _key != conn and _value["authenticated"]:
                        _key.sendall(json.dumps(data).encode())
            if data["type"] == "system":
                if data["request"] == "auth":
                    authenticate_conn(conn, data)
                if data["request"] == "get-history":
                    get_history(conn)
            else:
                print(f"Received data from {conn.getpeername()}: {data}")
        