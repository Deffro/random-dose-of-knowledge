import requests
from datetime import datetime
import pandas as pd
import plotly.graph_objs as go
import html


def read_my_reddit_password(filename='pswd.txt'):
    try:
        with open(filename, 'r') as f:
            return f.read()
    except FileNotFoundError:
        print(f'Please create a .txt file and store your reddit password there. There is not such file: "{filename}"')
        exit()


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
    Using the essential elements of prepare_request function, make an authorized connection with
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
TIMEFRAME = 'hour'  # hour, day, week, month, year, all


def get_post_details(res):
    """
    Extract and preprocess selected attributes from a result of a reddit api call (post only, not comments)
    :param
    res: json
        the result of a reddit api call for a random post of a specified subreddit
    :return: dict
        information about the post
    """
    post = res[0]['data']['children'][0]
    reddit_post_id = post['kind'] + '_' + post['data']['id']
    title = post['data']['title']
    subreddit = post['data']['subreddit']
    score = post['data']['score']
    created = datetime.utcfromtimestamp(int(post['data']['created'])).strftime('%Y-%m-%d %H:%M:%S')
    upvote_ratio = post['data']['upvote_ratio']
    permalink = 'https://reddit.com'+post['data']['permalink']
    thumbnail = post['data']['thumbnail']
    total_awards_received = post['data']['total_awards_received']
    num_comments = post['data']['num_comments']
    url = post['data']['url']
    timestamp_accessed = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {'title': title, 'score': score, 'created': created, 'upvote_ratio': upvote_ratio,
            'thumbnail': thumbnail, 'url': url, 'subreddit': subreddit,
            'permalink': permalink, 'total_awards_received': total_awards_received, 'num_comments': num_comments,
            'reddit_post_id': reddit_post_id, 'timestamp_accessed': timestamp_accessed}


def get_comments_details(res):
    """
    Extract and preprocess selected attributes from a result of a reddit api call (comments)
    :param
    res: json
        the result of a reddit api call for a random post of a specified subreddit
    :return: DataFrame
        information about the comments of the post
    """
    comments = pd.DataFrame()
    for i in range(len(res[1]['data']['children']))[:5]:
        post = res[1]['data']['children'][i]
        print(post['data']['body'], post['data']['score'], post['data']['total_awards_received'])
        if 'Welcome' not in post['data']['body']:
            body = html.unescape(post['data']['body'])
            comments = comments.append({'body': body, 'score': post['data']['score'],
                                        'reddit_comment_id': post['data']['id'],
                                        'total_awards_received': post['data']['total_awards_received']},
                                       ignore_index=True)
            comments['score'] = comments['score'].astype(int)
    return comments


def create_cumsum_plot(df):
    """
    For each subreddit create a line plot showing the cumulative count of its instances in the db over time
    resampled each 30 minutes
    """
    df['timestamp_accessed'] = pd.to_datetime(df['timestamp_accessed'])
    df = df.set_index('timestamp_accessed')

    grouper = df.groupby([pd.Grouper(freq='30min'), 'subreddit'])
    df = grouper['id'].count().unstack('subreddit').fillna(0).reset_index()
    for c in [c for c in df.columns if c not in ['subreddit', 'timestamp_accessed']]:
        df[c] = df[c].cumsum()

    fig = go.Figure()

    for c in [c for c in df.columns if c not in ['subreddit', 'timestamp_accessed']]:
        if c == 'todayilearned':
            color = '#ffc107'
            name = 'Today I Learned'
        elif c == 'YouShouldKnow':
            color = '#343a40'
            name = 'You Should Know'
        elif c == 'science':
            color = '#28a745'
            name = 'Science'
        elif c == 'funfacts':
            color = '#dc3545'
            name = 'Fun Facts'
        else:
            color = '#ffc107'
            name = c
        fig.add_trace(go.Scatter(x=df['timestamp_accessed'], y=df[c], name=name,
                                 mode='lines', marker=dict(size=4, color=color)))
    fig.update_layout(yaxis=dict(gridcolor='#DFEAF4'), xaxis=dict(gridcolor='#DFEAF4'), plot_bgcolor='white',
                      title=f'Amount of Knowledge Received over Time!', showlegend=True)

    fig.write_html('static/images/cumsum.html',
                   full_html=False,
                   include_plotlyjs='cdn'
                   )
