import random

waiting_list = ['lior']


def handle_start_game_message(name):
    global waiting_list
    waiting_list.append(name)
    print(f'Waiting List: {waiting_list}')
    if len(waiting_list) % 2 == 0:
        a = waiting_list[-2]
        b = waiting_list[-1]
        ran = random.randint(0, 1)
        if ran:
            a, b = b, a

        start_game(a, b)
        # print(waiting_list)
        waiting_list = waiting_list[:-2]
        print(waiting_list)


def start_game(x, o):
    print('STARTING GAME\n'
          f'x - {x}\n'
          f'O - {o}\n')


def handle_cancel_game_message(name):
    global waiting_list
    waiting_list.remove(name)
    print(waiting_list)


handle_start_game_message('ohad')
handle_start_game_message('ohady')
handle_cancel_game_message('ohady')
# print(waiting_list)
