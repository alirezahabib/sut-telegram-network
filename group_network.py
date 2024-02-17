import csv

group_id = 1952093821


class User:
    def __init__(self, username, id, first_name, last_name):
        self.id = id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name


class Message:
    def __init__(self, message_id, from_user_id, reply_to, pinned, message, reactions):
        self.message_id = message_id
        self.from_user_id = from_user_id
        self.reply_to = reply_to
        self.pinned = pinned
        self.message = message
        self.reactions = reactions

    def __str__(self):
        return f'{self.message_id}, {self.from_user_id}, {self.reply_to}, {self.pinned}, {self.message}, {self.reactions}'


def main():
    with open(f'./database/group-{group_id}/messages.csv', 'r', encoding='UTF-8') as f:
        rows = csv.reader(f, delimiter=',', lineterminator='\n')
        next(rows, None)
        i = 0
        for row in rows:
            message = Message(row[0], row[1], row[2], row[3] == True, '', row[5])
            print(message)
            print(message.pinned)
            if i > 10:
                break
            i += 1


if __name__ == "__main__":
    main()
