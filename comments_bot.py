# coding=utf-8
import getpass
import asyncio
import time
import requests

from instagram_private_api import Client


async def login(username, password):  # authorize to account
    try:
        api = Client(username, password)
        print('[I] Login to "' + username + '" OK!')
        return api

    except Exception as err:
        print('[E] Login to ' + username + ' FAILED!\n ERROR: {}'.format(err))
        return


async def comment_usernames_to_post(auth, user_to_get, comments_to_photo):  # Get user followers
    try:
        # Получить список подписок
        ig_client = await login(auth['username'], auth['password'])
        user_res = ig_client.username_info(user_to_get)
        user_id = user_res['user']['pk']
        next_max_id = None

        a = requests.get('https://api.instagram.com/oembed/?url={}'.format(comments_to_photo))
        media_id = a.json()['media_id']

        while True:
            kwargs = {}
            if next_max_id:
                kwargs['max_id'] = next_max_id
            followers_info = ig_client.user_followers(user_id, rank_token=ig_client.generate_uuid(), **kwargs)

            followers = followers_info['users']
            next_max_id = followers_info['next_max_id']

            try:
                comment_nicknames = []
                for profile in range(len(followers)):
                    followers_profile = followers[profile]
                    follower_username = followers_profile['username']

                    comment_nicknames.append('@{}'.format(follower_username))
                    if len(comment_nicknames) == 5:  # todo
                        comment = '{} Sorry for this'.format(' '.join(comment_nicknames))

                        ig_client.post_comment(media_id, comment)
                        comment_nicknames = []
                        time.sleep(15)

            except Exception as err:
                print('[E] While attempting to post a comment \n ERROR: {}'.format(err))
                continue

            if not next_max_id:
                break

    except Exception as err:
        print('[E] While attempting to login get_followings\n ERROR: {}'.format(err))
        return None


async def start():  # Get username and password by terminal
    username = input('Please, put your username here >>> ')
    password = getpass.getpass('Please put your password here >>> ')
    user_to_get = input('Please, write username of who you want to get followers >>> ')
    comments_to_photo = input('Please, put photo link >>> ')

    auth = {'username': username, 'password': password}

    await comment_usernames_to_post(auth, user_to_get, comments_to_photo)


if __name__ == '__main__':
    asyncio.run(start())
