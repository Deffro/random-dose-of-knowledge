import requests
from datetime import datetime
import pandas as pd
import plotly.graph_objs as go


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
TIMEFRAME = 'hour'  # hour, day, week, month, year, all


def get_post_details(res):
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


def create_cumsum_plot(df):

    df['timestamp_accessed'] = pd.to_datetime(df['timestamp_accessed'])
    df = df.set_index('timestamp_accessed')

    df_til = df.loc[df['subreddit'] == 'todayilearned']
    df_ysk = df.loc[df['subreddit'] == 'YouShouldKnow']

    df_til = df_til.resample('1min').count().reset_index().rename({'id': 'count'}, axis=1)[['timestamp_accessed', 'count']]
    df_til['count'] = df_til['count'].cumsum()
    df_til = df_til.tail(200)

    df_ysk = df_ysk.resample('1min').count().reset_index().rename({'id': 'count'}, axis=1)[['timestamp_accessed', 'count']]
    df_ysk['count'] = df_ysk['count'].cumsum()
    df_ysk = df_ysk.tail(200)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_til['timestamp_accessed'], y=df_til['count'], name='Today I Learned',
                             mode='lines+markers', marker=dict(size=4, color='#ffc107')))
    fig.add_trace(go.Scatter(x=df_ysk['timestamp_accessed'], y=df_ysk['count'], name='You Should Know',
                             mode='lines+markers', marker=dict(size=4, color='#343a40')))
    fig.update_layout(yaxis=dict(gridcolor='#DFEAF4'), xaxis=dict(gridcolor='#DFEAF4'), plot_bgcolor='white',
                      title=f'Amount of Knowledge Received over Time', showlegend=True)
    print('ok plot')
    fig.write_html('static/images/cumsum.html',
                   full_html=False,
                   include_plotlyjs='cdn'
                   )
