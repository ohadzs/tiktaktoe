from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData

engine = create_engine('sqlite:///tic_tac_toe.db', echo=True)
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


def add_user(username, password):
    # check if username already exist
    s = users.select().where(users.c.username == username)
    db_conn = engine.connect()
    search_result = db_conn.execute(s)
    for r in search_result:
        print('username is taken')
        return
    s = users.insert().values(username=username, password=password, score=0, history='')
    db_conn.execute(s)


add_user('player', '123456')
