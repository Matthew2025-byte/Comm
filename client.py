import argparse, socket, ipaddress



def ipv4_or_localhost(value):
    """Validates that the address given by the user is a valid IPv4 address"""

    # Raises argparse.ArgumentError if value is not a string
    if not isinstance(value, str):
        raise argparse.ArgumentError(f"Address must be in host:port format, not {type(value).__name__}")
    parts = value.split(':')

    # Raises argparse.ArgumentError if not host:port format
    if len(parts) != 2:
        raise argparse.ArgumentError("Address must be host:port format")
    host, port = parts

    # Validate that port is an integer
    try:
        port = int(port)
    except ValueError:
        raise argparse.ArgumentError("Port must an integer")
    
    if host.lower() == 'localhost':
        return (host, port)
    
    try:
        ip = ipaddress.IPv4Address(host)
    except ipaddress.AddressValueError:
        raise argparse.ArgumentError("Host must be a valid IPv4 address")
    
    return (str(ip), port)
            

parser = argparse.ArgumentParser(description='')
parser.add_argument('address', type=ipv4_or_localhost)

args = parser.parse_args()

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(args.address)

client.sendall(input("message: ").encode())
data = client.recv(1024)
print(data.decode())
client.close()