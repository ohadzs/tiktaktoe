def print_board(board):
    for i in range(len(board)):
        if (i+1)%3 == 0:
            print(f' {board[i]} ')
        else:
            print(f' {board[i]} |', end='')


def make_move(board, inp, role):
    x, y = inp.split(',')
    x, y = int(x), int(y)
    print(x, y)
    place = (x-1) + (y-1)*3
    print(place)
    board = board[:place] + role + board[place+1:]
    print_board(board)

def check_board(board):
    win = ({0, 1, 2}, {3, 4, 5}, {6, 7, 8}, {0, 3, 6}, {1, 4, 7}, {2, 5, 8}, {1, 4, 8}, {2, 4, 6})
    lst = {}
    for i in ['X', 'O']:
        lst.update({i: []})
        for s in range(len(board)):
            if i == board[s]:
                lst[i].append(s)
        for w in win:
            if w.issubset(set(lst[i])):
                print('win')
    print(lst)




board = 'XXXOO XOX'
inp = '3,3'
role = 'X'
print_board(board)
make_move(board, inp, role)
check_board(board)

x = []
y = x.append(2)
print(y)

if ' ' in '   s ':
    print('here')
# X | 0 |
#