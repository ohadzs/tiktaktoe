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

score = users.select().where(users.c.username == 'ohad')
db_conn = engine.connect()
search_result = db_conn.execute(score)
for row in search_result:
    print(f'score - {row[3]}')

score = users.select()
db_conn = engine.connect()
search_result = db_conn.execute(score)
for row in search_result:
    print(f'{row[1]} - {row[3]}')
    # score = row[3]


scores = {}
scores['ohad'] = 17
scores['lior'] = 5
scores['yaron'] = 500
scores = sorted(scores.items(), key=lambda item: item[1], reverse=True)
data = ''
for k, v in scores:
    data += f'{k}: {v}\n'
print(data)


s = users.select().where(users.c.username == 'ohad')
db_conn = engine.connect()
search_result = db_conn.execute(s)
for row in search_result:
    score = row[3]
s = users.update().where(users.c.username == 'ohad').values(score=score+1)
db_conn.execute(s)
