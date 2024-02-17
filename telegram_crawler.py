import os

from telethon.errors import SessionPasswordNeededError
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest, GetHistoryRequest, GetMessageReactionsListRequest
from telethon.tl.types import InputPeerEmpty, InputPeerChat
from getpass import getpass
import csv

from credentials import api_id, api_hash, phone_number

client = TelegramClient(phone_number, api_id, api_hash)

client.connect()
if not client.is_user_authorized():
    client.send_code_request(phone_number)
    try:
        client.sign_in(phone_number, input('Enter the code: '))
    except SessionPasswordNeededError:
        client.sign_in(password=getpass('Enter 2-step verification password: '))


def list_users_in_group(group_id=None, update_photos=False):
    if group_id:
        target_group = client.get_entity(group_id)
    else:
        chats = []
        last_date = None
        chunk_size = 200
        groups = []

        result = client(GetDialogsRequest(
            offset_date=last_date,
            offset_id=0,
            offset_peer=InputPeerEmpty(),
            limit=chunk_size,
            hash=0
        ))
        chats.extend(result.chats)

        for chat in chats:
            try:
                print(chat)
                groups.append(chat)
            except:
                continue

        print('Choose a group to scrape members from:')
        for i, g in enumerate(groups):
            print(str(i) + ' - ' + g.title)

        g_index = input('Enter a Number: ')
        target_group = groups[int(g_index)]

        print('\n\nSelected group:\t' + groups[int(g_index)].title)

    print('Fetching Members...')
    all_participants = client.get_participants(target_group, aggressive=True)

    print('Saving In file...')
    directory = f'./database/group-{target_group.id}/'
    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(directory + 'members.csv', 'w', encoding='UTF-8') as f:
        writer = csv.writer(f, delimiter=',', lineterminator='\n')
        writer.writerow(['user_id', 'username', 'access_hash', 'first_name', 'last_name', 'group_id', 'group'])
        for user in all_participants:
            print(user)
            if user.photo and (update_photos or not os.path.isfile(f'./database/profile_pics/{user.id}.jpg')):
                client.download_profile_photo(user, f'./database/profile_pics/{user.id}.jpg', download_big=True)

            writer.writerow(
                [user.id, user.username or '', user.access_hash, user.first_name or '',
                 user.last_name or '', target_group.id, target_group.title])
    print('Members saved successfully.')


def get_messages_from_group(id):
    group = client.get_entity(id)
    messages = []

    done = False
    offset = 0
    while not done:
        posts = client(GetHistoryRequest(
            peer=group,
            limit=50,
            offset_date=None,
            offset_id=0,
            max_id=0,
            min_id=0,
            add_offset=offset,
            hash=0))
        messages.extend(posts.messages)
        offset += 50
        if len(posts.messages) < 50:
            done = True

    print('Saving In file...')

    with open(f'./database/group-{id}/messages.csv', 'w', encoding='UTF-8') as f:
        writer = csv.writer(f, delimiter=',', lineterminator='\n')
        writer.writerow(['message_id',
                         'from_user_id',
                         'reply_to',
                         'pinned',
                         'message',
                         'reactions'])

        for message in messages:
            # if (not message.from_id) or message.mentioned or message.pinned or message.reply_to or message.reactions:
            #     #print(message.from_id.user_id)
            #     print(message)
            #     print()
            reactions_ids = []
            if message.reactions:
                reactions_response = client(GetMessageReactionsListRequest(group, message.id, limit=100))
                for reaction in reactions_response.reactions:
                    reactions_ids.append(str(reaction.peer_id.user_id))

            writer.writerow(
                [message.id,
                 message.from_id.user_id if message.from_id else '',
                 message.reply_to.reply_to_msg_id if message.reply_to else '',
                 message.pinned,
                 message.message or '',
                 '-'.join(reactions_ids)])
    print('Messages saved successfully.')

def merge_with_legacy(id_old, id_new):
    with open(f'database/group-{id_new}/messages.csv', 'a', newline='') as f1, open(f'database/group-{id_old}/messages.csv', 'r') as f2:
        # Read CSV file2 excluding the header
        reader2 = csv.reader(f2)
        next(reader2)  # Skip the header
        data2 = list(reader2)

        # Append data from file2 to file1
        writer = csv.writer(f1)
        writer.writerows(data2)


if __name__ == "__main__":
    list_users_in_group(update_photos=True)
    #get_messages_from_group(1952093821)
    #get_messages_from_group(4035585261)
    #merge_with_legacy(4035585261, 1952093821)
    pass

