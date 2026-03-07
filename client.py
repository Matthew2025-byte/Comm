from email.mime import message
import argparse, socket, ipaddress, json
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

def append_chat(user, message):
    global msg_history
    msg_history.insert(0, {"user": user, "content": message})
def get_message(sock):
    try:
        data = sock.recv(1024)
        if not data:
            return None
        buffer = data.decode()
        for msg in buffer.split("\r\n\r\n"):
            try:
                message = json.loads(msg)
                append_chat(message["user"], message["content"])
            except json.JSONDecodeError:
                print(f"Failed to decode message: {msg}")


    except BlockingIOError:
        return None
def send_message(sock, message):
    global USERNAME
    try:
        sock.sendall(json.dumps({"type": "message", "user": USERNAME, "content": message}).encode())
        return True
    except (ConnectionAbortedError, ConnectionError):
        return False

def draw_message_history(history, win: curses.window, w:int, h:int):
    win.clear()
    v_offset = h - len(history)
    for i, msg in enumerate(history):
        user:str = msg["user"]
        content:str = msg["content"]
        if user == USERNAME:
            offset = w - len(content) - 4
            win.addstr(v_offset - i, offset, msg['content'])
        else:
            message_offset = len(user) + 1
            if user.lower() == "system":
                win.addstr(v_offset - i, 1, user, curses.color_pair(1))
            else:
                win.addstr(v_offset - i, 1, user, curses.color_pair(2))
            win.addstr(v_offset - i, message_offset, ": "+ content)
    
    # Top border
    win.hline(0, 0, curses.ACS_HLINE, w)

    # Left + right borders
    win.vline(0, 0, curses.ACS_VLINE, h)
    win.vline(0, w-1, curses.ACS_VLINE, h)

    # Corners
    win.addch(0, 0, curses.ACS_ULCORNER)
    win.addch(0, w-1, curses.ACS_URCORNER)
    win.noutrefresh()
def draw_input_window(input_buffer, cursor_x, win:curses.window, w:int, h:int):
    max_text_width = w - 4
    win.erase()
    win.addstr(1, 1, "> " + input_buffer[:max_text_width])
    cursor_x = min(cursor_x, max_text_width)
    

    # Top border
    win.hline(0, 0, curses.ACS_HLINE, w)
    # Bottom border
    win.hline(h-1, 0, curses.ACS_HLINE, w)

    # Left border
    win.vline(0, 0, curses.ACS_VLINE, h)
    # Right border
    win.vline(0, w-1, curses.ACS_VLINE, h)

    # Top left corner
    win.addch(0, 0, curses.ACS_LTEE)
    # Top right corner
    win.addch(0, w-1, curses.ACS_RTEE)

    # Bottom corners
    win.addch(h-1, 0, curses.ACS_LLCORNER)
    win.insch(h-1, w-1, curses.ACS_LRCORNER)

    win.move(1, cursor_x + 3)  # Move cursor to the correct position
    win.noutrefresh()




parser = argparse.ArgumentParser(description='')
parser.add_argument('address', type=ipv4_or_localhost)
parser.add_argument('--username', '-u', type=str, default="Anonymous", help='Username to use when connecting to the server')

args = parser.parse_args()

USERNAME = args.username

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(args.address)
sock.setblocking(False)

sock.sendall(json.dumps({"type": "system", "request": "auth", "user": USERNAME, "pass": ""}).encode())



try:
    stdscr = curses.initscr()
    curses.start_color()
    curses.echo(False)
    curses.curs_set(1)
    height, width = stdscr.getmaxyx()

    # Gold on black for system messages
    curses.init_color(1, 1000, 860, 0)
    curses.init_pair(1, 1, curses.COLOR_BLACK)

    # Blue on black for user messages
    curses.init_color(2, 548, 828, 960)
    curses.init_pair(2, 2, curses.COLOR_BLACK)

    
    msg_history:list[dict] = []
    append_chat("System", f"Connected to {args.address[0]}:{args.address[1]}")
    append_chat("System", "Press Ctrl-X to exit")

    msg_win = curses.newwin(height - 3, width, 0, 0)
    input_win = curses.newwin(3, width, height - 3, 0)
    input_win.keypad(True)
    input_win.nodelay(True)  # Make getch non-blocking
    input_buffer = ""
    cursor_x = 0

    while True:
        # Get new messages from the server
        new_msg = get_message(sock)
        if new_msg is not None:
            msg_history.append(new_msg)
        # Redraw the windows
        draw_message_history(msg_history, msg_win, width, height - 3)
        draw_input_window(input_buffer, cursor_x, input_win, width, 3)
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
                if not send_message(sock, input_buffer):
                    append_chat("System", "Failed to send message")
                append_chat(USERNAME, input_buffer)
                input_buffer = ""
                cursor_x = 0
            # Add letters to input buffer
            elif key >= 32 and key <= 126:
                if len(input_buffer) < width - 4:
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