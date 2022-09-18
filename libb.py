CMD_FIELD_LENGTH = 16  # Exact length of cmd field (in bytes)
MAX_DATA_LENGTH = 1000
MAX_MSG_LENGTH = CMD_FIELD_LENGTH + MAX_DATA_LENGTH  # Max size of total message
DELIMITER = "|"  # Delimiter character in protocol
DATA_DELIMITER = "#"  # Delimiter in the data part of the message
ERROR_RETURN = None


def encrypt_message(cmd, data):
    if len(cmd) > CMD_FIELD_LENGTH or len(str(data)) > MAX_DATA_LENGTH:
        return ERROR_RETURN
    while len(cmd) < CMD_FIELD_LENGTH:
        cmd += ' '
    full_msg = cmd + DELIMITER + data
    return full_msg


def join_data(data_fields):
    # gets a list of things to send and parses into a string with data delimiter between them
    data_fields = list(map(lambda x: str(x), data_fields))
    ret = f'{data_fields[0]}'
    part = iter(data_fields)
    next(part)
    for p in part:
        ret += DATA_DELIMITER
        if p != ' ':
            ret += p
        if p == ' ':
            continue
    return ret


def decrypt_message(user_data):
    if len(user_data.split(DELIMITER)) != 2:
        print('shit 4.0')
        return ERROR_RETURN
    splited_data = user_data.split(DELIMITER)
    cmd = splited_data[0].split(' ')[0]
    msg = splited_data[1]
    return cmd, msg


def split_data(msg, expected_fields):
    split_msg = msg.split(DATA_DELIMITER)
    if len(split_msg) == expected_fields:
        return split_msg
    return ERROR_RETURN


def print_board(board):
    for i in range(len(board)):
        if (i+1)%3 == 0:
            print(f' {board[i]} ')
        else:
            print(f' {board[i]} |', end='')


if __name__ == '__main__':
    print(join_data(['ohad', 'zvi', 'shaboo']))
    print(encrypt_message('LOGIN', join_data(['ohad', 'zvi', 'shaboo'])))
    a, b, c = split_data(join_data(['ohad', 'zvi', 'shaboo']), 3)
    print(a)

