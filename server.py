import socket
import libb
import random
import select
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData


engine = create_engine('sqlite:///C:\\Users\yaron\\Desktop\\PycharmProjects\\TTT_project_pyqt5\\db\\tic_tac_toe.db', echo=True)
meta = MetaData()
users = Table(
    'first_table', meta,
    Column('id', Integer, primary_key=True),
    Column('username', String),
    Column('password', String),
    Column('score', Integer),
    Column('history', String),
)
games = Table(
    'second_table', meta,
    Column('id', Integer, primary_key=True),
    Column('x', String),
    Column('o', String),
    Column('board', String),
    Column('winner', String),
)

# GLOBALS
logged_users = {}
messages_to_send = []
client_sockets = []
waiting_list = []
live_games = {}
game_counter = 0

WIN_CONDITION = ({0, 1, 2}, {3, 4, 5}, {6, 7, 8}, {0, 3, 6}, {1, 4, 7}, {2, 5, 8}, {0, 4, 8}, {2, 4, 6})
SERVER_PORT = 10000
SERVER_IP = "0.0.0.0"
NEW_BOARD = '         '


def build_and_send_message(conn, cmd, data=''):
    full_msg = libb.encrypt_message(cmd, data)
    messages_to_send.append((conn, full_msg))
    print("[SERVER] ", full_msg)


def recv_message_and_parse(conn):
    try:
        full_msg = conn.recv(1024).decode()
        print("[CLIENT] ", full_msg)
        cmd, data = libb.decrypt_message(full_msg)
        return cmd, data
    except Exception as e:
        return None, None


def load_user_database():
    users = {
        "ohad": {"password": "ohad", "score": 0, 'history': []},
        "lior": {"password": "lior", "score": 50, 'history': []},
        "master": {"password": "master", "score": 200, 'history': []}
    }
    return users


# SOCKET CREATOR
def setup_socket():
    print('Server is booting...')
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((SERVER_IP, SERVER_PORT))
    sock.listen()
    print('Listening for clients...\nOn port 10000')
    return sock


def send_error(conn, error_msg):
    build_and_send_message(conn, 'ERROR', error_msg)


# MESSAGE HANDLING

def handle_getscore_message(conn, username):
    score = users.select().where(users.c.username == username)
    db_conn = engine.connect()
    search_result = db_conn.execute(score)
    for row in search_result:
        score = str(row[3])
    build_and_send_message(conn, 'YOUR_SCORE', score)


def handle_highscore_message(conn):
    scores = {}
    score = users.select()
    db_conn = engine.connect()
    search_result = db_conn.execute(score)
    for row in search_result:
        user = row[1]
        score = row[3]
        scores[user] = score
    scores = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    data = {}
    for k, v in scores:
        data[k] = v
    data = str(data)
    build_and_send_message(conn, 'ALL_SCORE', data)


def handle_logged_message(conn):
    build_and_send_message(conn, 'LOGGED_ANSWER', str(logged_users))


def handle_logout_message(conn):
    global logged_users
    global client_sockets

    try:
        del logged_users[conn.getpeername()]
    except Exception:
        pass
    client_sockets.remove(conn)
    conn.close()
    print('Connection closed')
    print_client_sockets(client_sockets)


def handle_login_message(conn, data):
    global logged_users
    username, password = libb.split_data(data, 2)

    s = users.select().where(users.c.username == username)
    db_conn = engine.connect()
    search_result = db_conn.execute(s)
    data = 'No such Username'
    for row in search_result:
        data = 'User is already logged in'
        if username in logged_users.values():
            break
        data = 'Wrong Password'
        if password == row[2]:
            build_and_send_message(conn, 'LOGIN_OK')
            logged_users[conn.getpeername()] = username
            return
    send_error(conn, data)


def handle_start_game_message(conn):
    global waiting_list
    for w in waiting_list:
        print(w.fileno())
        if w.fileno() == -1:
            print('444')
            waiting_list.remove(w)

    waiting_list.append(conn)
    print(f'Waiting List: {waiting_list}')
    if len(waiting_list) == 2:
        a = waiting_list[0]
        b = waiting_list[1]
        ran = random.randint(0, 1)
        if ran:
            a, b = b, a
        start_game(a, b)
        waiting_list = waiting_list[:-2]
        print(f'Waiting List: {waiting_list}')


def start_game(x, o):
    global logged_users
    global live_games
    global game_counter
    game_counter += 1
    print('STARTING GAME\n'
          f'X - {x}\n'
          f'O - {o}\n')
    data = libb.join_data([game_counter, logged_users[x.getpeername()], logged_users[o.getpeername()]])
    build_and_send_message(x, 'STARTING_GAME', data)
    build_and_send_message(o, 'STARTING_GAME', data)
    live_games.update({game_counter: {
        'x': x,
        'o': o,
        'board': NEW_BOARD,
        'x_lst': [],
        'o_lst': []
    }})


def handle_cancel_game_message(conn):
    global waiting_list
    build_and_send_message(conn, 'GAME_CANCELED')
    if conn in waiting_list:
        waiting_list.remove(conn)
    print(f'Waiting List: {waiting_list}')


def handle_ready_message(conn, data):
    game_num = int(data)
    board = live_games[game_num]['board']
    num_of_x = board.count('x')
    num_of_o = board.count('o')
    player_role = find_role(conn, game_num)

    if (num_of_x == num_of_o and player_role == 'x') or (num_of_x > num_of_o and player_role == 'o'):
        build_and_send_message(conn, 'YOUR_TURN', board)


def handle_my_move_message(conn, data):
    global live_games
    data = libb.split_data(data, 3)
    game_num = int(data[0])
    x = int(data[1])
    y = int(data[2])
    place = (x - 1) + (y - 1) * 3
    player_role = find_role(conn, game_num)
    board = live_games[game_num]['board']
    new_board = make_move(board, place, player_role)
    if new_board == board:
        build_and_send_message(conn, 'YOUR_TURN', board)
        return
    live_games[game_num]['board'] = new_board
    build_and_send_message(conn, 'MOVE_RECEIVED', new_board)
    if player_role == 'x':
        live_games[game_num]['x_lst'].append(place)
        player_on_map = live_games[game_num]['x_lst']
        other_player = live_games[game_num]['o']
    else:
        live_games[game_num]['o_lst'].append(place)
        player_on_map = live_games[game_num]['o_lst']
        other_player = live_games[game_num]['x']
    print(player_on_map)

    # check if the game is over
    for w in WIN_CONDITION:
        if w.issubset(set(player_on_map)):
            build_and_send_message(conn, 'GAME_OVER', libb.join_data(['WON', new_board]))
            winner_username = logged_users[conn.getpeername()]
            s = users.select().where(users.c.username == winner_username)
            db_conn = engine.connect()
            search_result = db_conn.execute(s)
            for row in search_result:
                score = row[3]
                history = row[4]
            s = users.update().where(users.c.username == winner_username).values(score=score + 1)
            db_conn.execute(s)
            s = users.update().where(users.c.username == winner_username).values(history=history + 'W')
            db_conn.execute(s)

            build_and_send_message(other_player, 'GAME_OVER', libb.join_data(['LOSE', new_board]))
            loser_username = logged_users[other_player.getpeername()]
            s = users.select().where(users.c.username == loser_username)
            search_result = db_conn.execute(s)
            for row in search_result:
                score = row[3]
                history = row[4]
            s = users.update().where(users.c.username == loser_username).values(score=score - 1)
            db_conn.execute(s)
            s = users.update().where(users.c.username == loser_username).values(history=history + 'L')
            db_conn.execute(s)

            x_username = winner_username
            o_username = loser_username
            if player_role == 'o':
                x_username = loser_username
                o_username = winner_username

            s = games.insert().values(x=x_username, o=o_username, board=new_board, winner=winner_username)
            db_conn.execute(s)
            return
    if ' ' in new_board:
        handle_ready_message(other_player, game_num)
    else:
        # if its a tie, the last player that played is the o
        o_username = logged_users[conn.getpeername()]
        x_username = logged_users[other_player.getpeername()]

        db_conn = engine.connect()
        s = users.select().where(users.c.username == o_username)
        search_result = db_conn.execute(s)
        for row in search_result:
            history = row[4]
        s = users.update().where(users.c.username == o_username).values(history=history + 'T')
        db_conn.execute(s)

        s = users.select().where(users.c.username == x_username)
        search_result = db_conn.execute(s)
        for row in search_result:
            history = row[4]
        s = users.update().where(users.c.username == x_username).values(history=history + 'T')
        db_conn.execute(s)

        s = games.insert().values(x=x_username, o=o_username, board=new_board, winner='none')
        db_conn.execute(s)

        data = libb.join_data(['TIE', new_board])
        build_and_send_message(conn, 'GAME_OVER', data)
        build_and_send_message(other_player, 'GAME_OVER', data)


def make_move(board, place, role):
    if board[place] == ' ':
        board = board[:place] + role + board[place + 1:]
        libb.print_board(board)
    return board


def find_role(conn, game_num):
    if live_games[game_num]['x'] == conn:
        return 'x'
    elif live_games[game_num]['o'] == conn:
        return 'o'
    else:
        print('shit 3.0')


def handle_client_message(conn, cmd, data):
    global logged_users
    if conn.getpeername() in logged_users:
        if cmd == 'LOGOUT' or cmd is None:
            handle_logout_message(conn)
        elif cmd == 'MY_SCORE':
            handle_getscore_message(conn, logged_users[conn.getpeername()])
        elif cmd == 'GET_HIGHSCORE':
            handle_highscore_message(conn)
        elif cmd == 'GET_LOGGED':
            handle_logged_message(conn)
        elif cmd == 'START_GAME':
            handle_start_game_message(conn)
        elif cmd == 'CANCEL_GAME':
            handle_cancel_game_message(conn)
        elif cmd == 'READY':
            handle_ready_message(conn, data)
        elif cmd == 'MY_MOVE':
            handle_my_move_message(conn, data)
        else:
            send_error(conn, 'something went wrong with your message')
            print('shit 5.0')
    elif cmd == 'LOGIN':
        handle_login_message(conn, data)
    else:
        send_error(conn, 'something went wrong with your message')
        print('shit 50.0')


def print_client_sockets(sock_lst):
    print(f'client_sockets:\n'
          f'\t\t IP \t\t | PORT')
    for i in sock_lst:
        ip, port = i.getpeername()
        print(f'{ip.center(20)} | {port}')


def main():
    # global users
    global messages_to_send
    global client_sockets
    # users = load_user_database()
    print("Welcome to Tic-Tac-Toe Server!")
    server_socket = setup_socket()
    while True:
        ready_to_read, ready_to_write, in_error = select.select([server_socket] + client_sockets, client_sockets, [])
        for current_socket in ready_to_read:
            if current_socket is server_socket:
                client_socket, client_address = current_socket.accept()
                print('New client joined!', client_address)
                client_sockets.append(client_socket)
                print_client_sockets(client_sockets)
            else:
                print('New data arrived from client')
                try:
                    command, data = recv_message_and_parse(current_socket)
                except Exception:
                    command = None
                if command is None:
                    handle_logout_message(current_socket)
                else:
                    handle_client_message(current_socket, command, data)

        for message in messages_to_send:
            current_socket, data = message
            if current_socket in ready_to_write:
                current_socket.send(data.encode())
                messages_to_send.remove(message)


if __name__ == '__main__':
    main()
