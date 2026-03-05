import argparse, socket

parser = argparse.ArgumentParser(description='')
parser.add_argument('host', type=str)
parser.add_argument('port', type=int)

args = parser.parse_args()

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((args.host, args.port))


data = client.recv(1024)
print(data.decode())
client.close()