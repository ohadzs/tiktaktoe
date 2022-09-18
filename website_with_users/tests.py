from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData
import hashlib

engine = create_engine('sqlite:///ttt_users.db', echo=True)
meta = MetaData()

users = Table(
    'first_table', meta,
    Column('id', Integer, primary_key=True),
    Column('username', String),
    Column('password', Integer),
)


# username = input('username: ')
# password = input('password: ')
# password = hashlib.md5(password.encode()).hexdigest()
# print(password)
# ins = users.insert()
# ins = users.insert().values(username=username, password=password)
# conn = engine.connect()
# result = conn.execute(ins)

# password = 'Ozs184801'
# password = hashlib.sha256().hexdigest()
# s = users.select().where(users.c.username == 'ohad')
# conn = engine.connect()
# search_result = conn.execute(s)
# for r in search_result:
#     print(r[2])
#     if password == r[2]:
#         print(True)

username = 'ohad'
s = users.select().where(users.c.username == username)
conn = engine.connect()
search_result = conn.execute(s)
for r in search_result:
    print('1')
