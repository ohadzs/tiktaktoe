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
meta.create_all(engine)
