import ast
import socket
import sys
from PyQt5.QtGui import QColor
from PyQt5.uic import loadUi
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMessageBox, QDialog, QApplication, QTableWidgetItem, QListWidgetItem, QStackedWidget
import libb

SERVER_IP = socket.gethostbyname('ohad.hopto.org')
# SERVER_IP = '10.0.0.24'
SERVER_PORT = 10000
conn = None
game_num = 0
username = ''
role = ''
enemy = ''
r, c = 0, 0
result = ''


def build_and_send_message(connection, cmd, data=''):
    msg = libb.encrypt_message(cmd, data)
    connection.send(msg.encode())


def recv_message_and_parse(connection):
    full_msg = connection.recv(1024).decode()
    cmd, data = libb.decrypt_message(full_msg)
    return cmd, data


def build_send_recv_parse(connection, cmd, data=''):
    build_and_send_message(connection, cmd, data)
    cmd, msg = recv_message_and_parse(connection)
    return cmd, msg


def goto_loginscreen():
    build_and_send_message(conn, 'LOGOUT')
    login_screen = MainWindow()
    widget.addWidget(login_screen)
    widget.setCurrentWidget(login_screen)


def goto_screen2():
    screen2.startgame_button.setText('START GAME')
    screen2.get_highscore()
    screen2.get_online()
    widget.setCurrentWidget(screen2)


def goto_gamescreen():
    widget.setCurrentWidget(game_screen)


class MainWindow(QDialog):
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi('screens/login_screen.ui', self)
        global conn
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect((SERVER_IP, SERVER_PORT))

        self.login_button.clicked.connect(self.check_login)

    def check_login(self):
        global username
        username = self.username.text()
        password = self.password.text()
        data = [username, password]
        data = libb.join_data(data)
        answer = build_send_recv_parse(conn, 'LOGIN', data)
        if answer[0] == 'LOGIN_OK':
            goto_screen2()
        else:
            msg = QMessageBox()
            msg.setWindowTitle('error')
            msg.setText(answer[1])
            msg.setIcon(QMessageBox.Critical)
            msg.setStandardButtons(QMessageBox.Retry)
            msg.setInformativeText('Try again!')
            msg.setDetailedText('details')
            msg.exec_()


class Screen2(QDialog):
    def __init__(self):
        super(Screen2, self).__init__()
        loadUi('screens/screen2.ui', self)

        self.worker = Worker()
        self.startgame_button.clicked.connect(self.start_game)
        self.highscore_button.clicked.connect(self.get_highscore)
        self.online_button.clicked.connect(self.get_online)
        self.signout_button.clicked.connect(goto_loginscreen)

    def get_highscore(self):
        table = build_send_recv_parse(conn, 'get_highscore'.upper())
        res = ast.literal_eval(table[1])
        self.highscore_table.setRowCount(0)
        for k, v in res.items():
            rc = self.highscore_table.rowCount()
            self.highscore_table.insertRow(rc)
            self.highscore_table.setItem(rc, 0, QTableWidgetItem(str(k)))
            self.highscore_table.setItem(rc, 1, QTableWidgetItem(str(v)))
            if k == username:
                self.highscore_table.item(rc, 0).setBackground(QColor('#bf5b17'))
                self.highscore_table.item(rc, 1).setBackground(QColor('#bf5b17'))

    def get_online(self):
        onlines = build_send_recv_parse(conn, 'GET_LOGGED')[1]
        res = ast.literal_eval(onlines)
        # print('logged users: \n' + str(res))
        self.online_list.clear()
        for i in res.values():
            ii = QListWidgetItem(f'- {i}')
            if i == username:
                ii.setBackground(QColor('#bf5b17'))
            self.online_list.addItem(ii)

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            # print('keyesc')
            build_and_send_message(conn, 'CANCEL_GAME')
            self.startgame_button.setText('START GAME')
            self.highscore_button.clicked.connect(self.get_highscore)
            self.online_button.clicked.connect(self.get_online)
            self.signout_button.clicked.connect(goto_loginscreen)

    def start_game(self):
        if 'Opponent Found' in self.startgame_button.text():
            goto_gamescreen()
        elif 'START GAME' in self.startgame_button.text():
            self.startgame_button.setText('Searching for opponent...\n'
                                          'Enter ESC to CANCEL')
            self.highscore_button.disconnect()
            self.online_button.disconnect()
            self.signout_button.disconnect()
            self.worker = Worker()
            self.worker.start()
            self.worker.finished.connect(self.ewf)

    def ewf(self):
        if result != '':
            msg = QMessageBox()
            msg.setWindowTitle('Congratulations')
            msg.setText(f'You {result}')
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
        goto_screen2()
        self.highscore_button.clicked.connect(self.get_highscore)
        self.online_button.clicked.connect(self.get_online)
        self.signout_button.clicked.connect(goto_loginscreen)
        game_screen.print_board('         ')


class Worker(QtCore.QThread):
    def run(self):
        global game_num
        global role
        global enemy
        global result
        result = ''
        answer = build_send_recv_parse(conn, 'START_GAME')
        if answer[0] == 'STARTING_GAME':
            # print(f'Starting GAME\n{answer[1]}')
            data = libb.split_data(answer[1], 3)
            game_num = data[0]
            x = data[1]
            o = data[2]
            if x == username:
                role = 'x'
                enemy = o
                # print(f'you are {role}. playing VS {enemy}')
            else:
                role = 'o'
                enemy = x
                # print(f'you are {role}. playing VS {enemy}')
            screen2.startgame_button.setText('Opponent Found\n'
                                             'click to start game')
            game_screen.play_game()
        elif answer[0] == 'GAME_CANCELED':
            print(answer[0])
        else:
            print('shit 2.0')


class Game_screen(QDialog):
    def __init__(self):
        super(Game_screen, self).__init__()
        loadUi('screens/screen3.ui', self)
        self.top_left.clicked.connect(lambda: self.change_turn(1, 1))
        self.top_mid.clicked.connect(lambda: self.change_turn(2, 1))
        self.top_right.clicked.connect(lambda: self.change_turn(3, 1))
        self.mid_left.clicked.connect(lambda: self.change_turn(1, 2))
        self.mid.clicked.connect(lambda: self.change_turn(2, 2))
        self.mid_right.clicked.connect(lambda: self.change_turn(3, 2))
        self.bot_left.clicked.connect(lambda: self.change_turn(1, 3))
        self.bot_mid.clicked.connect(lambda: self.change_turn(2, 3))
        self.bot_right.clicked.connect(lambda: self.change_turn(3, 3))

    def change_turn(self, a, b):
        global r
        global c
        r = a
        c = b

    def print_board(self, board):
        self.top_left.setText(board[0])
        self.top_mid.setText(board[1])
        self.top_right.setText(board[2])
        self.mid_left.setText(board[3])
        self.mid.setText(board[4])
        self.mid_right.setText(board[5])
        self.bot_left.setText(board[6])
        self.bot_mid.setText(board[7])
        self.bot_right.setText(board[8])

    def play_game(self):
        global r
        global c
        global result
        self.role.setText(f'You are {role.upper()}')
        if role == 'x':
            game_screen.turn.setText('Your Turn')
        else:
            game_screen.turn.setText(f"{enemy}'s Turn")
        while True:
            build_and_send_message(conn, 'READY', game_num)
            answer = recv_message_and_parse(conn)
            if answer[0] == 'YOUR_TURN':
                self.turn.setText('Your Turn')
                r, c = 0, 0
                board = answer[1]
                self.print_board(board)
                while True:
                    if 0 < r <= 3 and 0 < c <= 3:
                        break
                data = libb.join_data([game_num, r, c])
                answer = build_send_recv_parse(conn, 'MY_MOVE', data)
                self.print_board(answer[1])
                self.turn.setText(f"{enemy}'s Turn")
            elif answer[0] == 'GAME_OVER':
                data = libb.split_data(answer[1], 2)
                self.print_board(data[1])
                result = data[0]
                break
            else:
                print('shit')


app = QApplication(sys.argv)
widget = QStackedWidget()
widget.setWindowTitle('Tic-Tac_Toe')
login_screen = MainWindow()
screen2 = Screen2()
game_screen = Game_screen()
widget.addWidget(login_screen)
widget.addWidget(screen2)
widget.addWidget(game_screen)
widget.setFixedHeight(372)
widget.setFixedWidth(322)
widget.show()

sys.exit(app.exec_())
