import sqlite3
from faker import Faker
fake = Faker()

import uuid

print(fake.first_name())
print(fake.email())

user = {
    'user_id': str(uuid.uuid4()),
    'user_name': str(fake.first_name()),
    'user_email': str(fake.email())
}
print(user)

users = [
    {
    'user_id': str(uuid.uuid4()),
    'user_name': str(fake.first_name()),
    'user_email': str(fake.email())
    },
    {
    'user_id': str(uuid.uuid4()),
    'user_name': str(fake.first_name()),
    'user_email': str(fake.email())
    },

]
print(users)

# Loop for adding multiple users at once
usr = []
for _ in range(10):
    ur = {
        'user_id': str(uuid.uuid4()),
        'user_name': str(fake.first_name()),
        'user_email': str(fake.email()),
        'user_password': str(fake.password())
    }
    usr.append(ur)

# Listcomprehention
list_comp = [{
        'user_id': str(uuid.uuid4()),
        'user_name': str(fake.first_name()),
        'user_email': str(fake.email())
    } for _ in range(10)]

try:
    db = sqlite3.connect('database.db')
    #counter = db.execute('INSERT INTO users VALUES(:user_id, :user_name, :user_email, :user_password)', user).rowcount
    #counter = db.executemany('INSERT INTO users VALUES(:user_id, :user_name, :user_email)', users, :user_password).rowcount
    counter = db.executemany('INSERT INTO users VALUES(:user_id, :user_name, :user_email, :user_password)', usr).rowcount
    if not counter:
        print('ups...')
    db.commit()
    print(f'{user} was inserted!')
except Exception as ex:
    print(ex)
finally:
    db.close()