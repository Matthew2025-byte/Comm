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
    curses.echo(False)
    curses.curs_set(1)
    height, width = stdscr.getmaxyx()

    msg_win = curses.newwin(height - 3, width, 0, 0)
    msg_history = []
    

    input_win = curses.newwin(3, width, height - 3, 0)
    input_win.keypad(True)
    input_win.nodelay(True)  # Make getch non-blocking
    input_buffer = ""
    cursor_x = 0

    while True:
        # Update message history window
        msg_win.erase()
        for i, msg in enumerate(msg_history):
            msg_win.addstr(1 + i, 1, msg + "\n")
        msg_win.box()
        msg_win.noutrefresh()

        # Update input window
        input_win.erase()
        input_win.box()
        input_win.addstr(1, 1, "> " + input_buffer)
        input_win.move(1, 3 + cursor_x)
        input_win.noutrefresh()
        curses.doupdate()
        

        key = input_win.getch()
        if key != -1: # Check if a key was pressed
            if key == 24: # Ctrl-X to exit
                break
            if key == curses.KEY_BACKSPACE or key == 8 or key == 127:
                input_buffer = input_buffer[:-1]
                cursor_x = max(0, cursor_x - 1)
            # send message
            elif key == curses.KEY_ENTER or key == 10:
                #sock.sendall(input_buffer.encode())
                msg_history.append(input_buffer)
                input_buffer = ""
                cursor_x = 0
            # Add letters to input buffer
            elif key >= 32 and key <= 126:
                input_buffer += chr(key)
                cursor_x += 1
            # Move cursor within input buffer
            elif key == curses.KEY_LEFT:
                cursor_x = max(0, cursor_x - 1)
            elif key == curses.KEY_RIGHT:
                cursor_x = min(len(input_buffer), cursor_x + 1)
            # handle resizing
            elif key == curses.KEY_RESIZE:
                height, width = stdscr.getmaxyx()

                msg_win.resize(height - 3, width)
                msg_win.mvwin(0, 0)
                
                input_win.resize(3, width)
                input_win.mvwin(height - 3, 0)
            else:  # Log unhandled keys
                msg_win.clear()
                msg_win.addstr(f"Unknown key: {key}\n")
                msg_win.refresh()
          
finally:
    stdscr.keypad(False)
    curses.endwin()