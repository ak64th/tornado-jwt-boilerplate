class User(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def __str__(self):
        return "User(id='%s')" % self.id


users = [
    User(1, 'user1', '123456'),
    User(2, 'user2', 'qwerty'),
]

user_index = {u.id: u for u in users}
username_index = {u.username: u for u in users}
