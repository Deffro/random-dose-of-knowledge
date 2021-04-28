import requests
# import pandas as pd


def read_my_reddit_password(filename='pswd.txt'):
    with open(filename, 'r') as f:
        return f.read()


def prepare_request():
    """
    Return the essential elements to make an authorized request on reddit
    """
    auth = requests.auth.HTTPBasicAuth(CLIENT_ID, SECRET_KEY)

    data = {
        'grant_type': 'password',
        'username': REDDIT_USERNAME,
        'password': REDDIT_PASSWORD
    }

    headers = {'User-Agent': 'today-i-learned/0.1'}

    return auth, data, headers


def get_access_token():
    """
    Using the essential elemets of prepare_request function, make an authorized connection with
    reddit and return the headers dictionary with the Authorization token inside
    """
    auth, data, headers = prepare_request()
    res = requests.post('https://www.reddit.com/api/v1/access_token',
                        auth=auth,
                        data=data,
                        headers=headers)
    token = res.json()['access_token']
    headers['Authorization'] = f'bearer {token}'
    return headers


def get_reddit(subreddit):
    """
    Return a random post of the specified subreddit after making an authorized connection and getting the
    Authorized token inside the headers dictionary
    """
    headers_with_token = get_access_token()
    try:
        url = f'https://oauth.reddit.com/r/{subreddit}/{LISTING}.json?count={COUNT}&t={TIMEFRAME}'
        res = requests.get(url, headers=headers_with_token)
    except:
        return 'An Error Occurred'
    return res.json()


SECRET_KEY = 'UfjnQRWnzRgA2p6JDPcupuLfKaKs5Q'
CLIENT_ID = 'xD3Mj1MwQ9JRTA'
REDDIT_USERNAME = 'deffrosy'
REDDIT_PASSWORD = read_my_reddit_password(filename='utils/pswd.txt')
LISTING = 'random'  # controversial, best, hot, new, random, rising, top
COUNT = '1'
TIMEFRAME = 'all'  # hour, day, week, month, year, all

# res = get_reddit(subreddit='python')
#
# df = pd.DataFrame()
#
# for post in res[0]['data']['children']:
#     df = df.append({
#         'id': post['kind'] + '_' + post['data']['id'],
#         'title': post['data']['title'],
#         'subreddit': post['data']['subreddit'],
#         'upvote_ratio': post['data']['upvote_ratio'],
#         'total_awards_received': post['data']['total_awards_received'],
#         'score': post['data']['score'],
#         'created': post['data']['created'],
#         'num_comments': post['data']['num_comments'],
#         'url': post['data']['url'],
#         'selftext': post['data']['selftext'],
#         'upvote_ratio': post['data']['upvote_ratio'],
#     }, ignore_index=True)
# df
