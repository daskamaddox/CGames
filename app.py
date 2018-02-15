from flask import Flask, redirect, url_for, session, render_template
from flask_oauth import OAuth
import config
import ast

GOOGLE_CLIENT_ID = config.GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET = config.GOOGLE_CLIENT_SECRET
REDIRECT_URI = '/oauth2callback'  # one of the Redirect URIs from Google APIs console

SECRET_KEY = 'development key'
DEBUG = True

app = Flask(__name__)
app.debug = DEBUG
app.secret_key = SECRET_KEY
oauth = OAuth()

google = oauth.remote_app('google',
                          base_url='https://www.google.com/accounts/',
                          authorize_url='https://accounts.google.com/o/oauth2/auth',
                          request_token_url=None,
                          request_token_params={'scope': 'https://www.googleapis.com/auth/userinfo.email',
                                                'response_type': 'code'},
                          access_token_url='https://accounts.google.com/o/oauth2/token',
                          access_token_method='POST',
                          access_token_params={'grant_type': 'authorization_code'},
                          consumer_key=GOOGLE_CLIENT_ID,
                          consumer_secret=GOOGLE_CLIENT_SECRET)
def save(user):
    print(user)

@app.route("/")
def index():
    return render_template('index.html')


@app.route('/signin')
def signin():
    access_token = session.get('access_token')
    if access_token is None:
        return redirect(url_for('login'))

    access_token = access_token[0]
    import urllib.request
    from urllib.error import URLError
    headers = {'Authorization': 'OAuth '+access_token}
    req = urllib.request.Request('https://www.googleapis.com/oauth2/v1/userinfo',
                  None, headers)
    try:
        res = urllib.request.urlopen(req)
    except URLError as e:
        if e.code == 401:
            # Unauthorized - bad token
            session.pop('access_token', None)
            return redirect(url_for('login'))
        return res.read()
    user = (res.read())
    #d = dict(toks.split(":",1) for toks in user.decode("utf-8").split(",") if toks)
    n=[]
    l = user.decode('utf-8').split(',')
    for item in l:
        new = item.split(':',1)
        for i in range(len(new)):
            n.append(new[i][new[i].find('"')+1:new[i].find('"',new[i].find('"')+1)])
    d={}

    for i in range(0,len(n),2):
        d[n[i]]=n[i+1]

    save(d)
    return render_template('profile.html',vname=d['name'],vphoto=d['picture'])

@app.route('/login')
def login():
    callback=url_for('authorized', _external=True)
    return google.authorize(callback=callback),





@app.route(REDIRECT_URI)
@google.authorized_handler
def authorized(resp):
    access_token = resp['access_token']
    session['access_token'] = access_token, ''
    return redirect(url_for('index'))


@google.tokengetter
def get_access_token():
    return session.get('access_token')


def main():
    app.run()



if __name__ == '__main__':
    main()
