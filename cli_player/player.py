import socket
import libb
from pynput import keyboard
import concurrent.futures

SERVER_IP = "10.0.0.24"  # Our server will run on same computer as client
SERVER_PORT = 5000
game_num = None


def build_and_send_message(conn, cmd, data):
    msg = libb.encrypt_message(cmd, data)
    conn.send(msg.encode())


def recv_message_and_parse(conn):
    full_msg = conn.recv(1024).decode()
    cmd, data = libb.decrypt_message(full_msg)
    # print(f'server says:\n\tcmd: {cmd} \n\tdata:{data}')
    return cmd, data


def build_send_recv_parse(conn, cmd, data):
    build_and_send_message(conn, cmd, data)
    command, msg = recv_message_and_parse(conn)
    return command, msg


def connect(server_ip, server_port):
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.connect((server_ip, server_port))
    return my_socket


def error_and_exit(error_msg):
    print(error_msg)
    exit(6)


def login(conn):
    while True:
        username = input("Please enter username: ")
        password = input("Please enter password: ")
        data = [username, password]
        data = libb.join_data(data)
        answer = build_send_recv_parse(conn, 'LOGIN', data)
        if answer[0] == 'LOGIN_OK':
            return
        print(answer[1])


def logout(conn):
    build_and_send_message(conn, 'LOGOUT', '')


def get_score(conn):
    score = build_send_recv_parse(conn, 'my_score'.upper(), '')
    print(score[1])


def get_highscore(conn):
    table = build_send_recv_parse(conn, 'get_highscore'.upper(), '')
    print(table[1])


def get_logged_users(conn):
    print('logged users: \n' +
          build_send_recv_parse(conn, 'GET_LOGGED', '')[1])


def on_press(key):
    if key == keyboard.Key.esc:
        global connection
        build_and_send_message(connection, 'CANCEL_GAME', '')


def on_release(key):
    if key == keyboard.Key.esc:
        print('realising')
        return False


def start_game(conn):
    global game_num
    build_and_send_message(conn, 'START_GAME', '')
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(recv_message_and_parse, conn)
        print('Searching for opponent...\n'
              'Enter ESC to CANCEL')
        with keyboard.Listener(
                on_press=on_press,
                on_release=on_release) as listener:
            answer = future.result()
            if answer[0] == 'STARTING_GAME':
                print(f'Starting GAME\n{answer}')
                game_num = libb.split_data(answer[1], 3)[0]
                return True
            elif answer[0] == 'GAME_CANCELED':
                print(answer[0])
                return False
            else:
                print('shit 2.0')


def play_game(conn):
    while True:
        build_and_send_message(conn, 'READY', game_num)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(recv_message_and_parse, conn)
            answer = future.result()
        if answer[0] == 'YOUR_TURN':
            board = answer[1]
            libb.print_board(board)
            while True:
                inp = input('Your move? ("x,y") ')
                try:
                    x, y = inp.split(',')
                    x, y = int(x), int(y)
                    if x <= 3 and y <= 3:
                        break
                except Exception:
                    pass
            data = libb.join_data([game_num, x, y])
            answer = build_send_recv_parse(conn, 'MY_MOVE', data)
            libb.print_board(answer[1])
            print()
        elif answer[0] == 'GAME_OVER':
            data = libb.split_data(answer[1], 2)
            print(data[0])
            libb.print_board(data[1])
            return
        else:
            print('shit')


if __name__ == '__main__':
    global connection
    connection = connect(SERVER_IP, SERVER_PORT)
    login(connection)
    while True:
        inp = input('\nwhat do you want?\n'
                    'show score\n'
                    'show highscore\n'
                    'show logged users\n'
                    'sign out\n'
                    'start game\n')
        if inp == 'show score':
            get_score(connection)
        elif inp == 'show highscore':
            get_highscore(connection)
        elif inp == 'show logged users':
            get_logged_users(connection)
        elif inp == 'sign out':
            logout(connection)
            break
        elif inp == 'start game':
            game = start_game(connection)
            if game:
                play_game(connection)
