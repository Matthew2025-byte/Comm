import argparse, socket, ipaddress
from curses import wrapper
import curses

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

#sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#sock.connect(args.address)

try:
    stdscr = curses.initscr()
    stdscr.nodelay(True)
    stdscr.keypad(True)
    height, width = stdscr.getmaxyx()

    msgHistory_win = curses.newwin(height - 3, width, 0, 0)
    input_win = curses.newwin(3, width, height - 3, 0)

    while True:
        key = stdscr.getch()
        if key != -1:
            # display the size of the terminal (debug purposes)
            if key == curses.KEY_RESIZE:
                height, width = stdscr.getmaxyx()

                msgHistory_win.resize(height - 3, width)
                msgHistory_win.mvwin(0, 0)
                input_win.resize(3, width)
                input_win.mvwin(height - 3, 0)

                msgHistory_win.clear()
                msgHistory_win.addstr(0, 0, f"{width}x{height}")
                msgHistory_win.refresh()
            if key == ord('q'):
                break
finally:
    stdscr.keypad(False)
    curses.endwin()