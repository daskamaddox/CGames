from flask import Flask, redirect, url_for, session, render_template
from flask_oauth import OAuth
import config

'''
    connecting to google OAuth
    source tutorial: https://pythonspot.com/login-to-flask-app-with-google
'''

GOOGLE_CLIENT_ID = config.GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET = config.GOOGLE_CLIENT_SECRET
REDIRECT_URI = '/oauth2callback'
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

'''
    the function save is the template for saving the user, a table will have to
    be set up with the user info and stats
'''
def save(user):
    print(user)

'''
    this is the homepage; all it does is renders the index.html file
'''

@app.route("/")
def index():
    return render_template('index.html')

'''
    when the sign in button or link is clicked, this function runs
    here is where the OAuth is requested and if completed returns
    a bytes array of user information which is then converted into a dictonary
    then a template profile page is shown profile.html with a name and image
'''

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
    n=[]
    l = user.decode('utf-8').split(',')
    for item in l:
        new = item.split(':',1)
        for i in range(len(new)):
            n.append(new[i][new[i].find('"')+1:new[i].find('"',new[i].find('"')+1)])
    d={}

    for i in range(0,len(n),2):
        d[n[i]]=n[i+1]

    return render_template('profile.html',vname=d['name'],vphoto=d['picture'])

'''
    the login function runs the google oath
'''

@app.route('/login')
def login():
    callback=url_for('authorized', _external=True)
    return google.authorize(callback=callback),

'''
    authorize handles the redirect of the google oath
'''

@app.route(REDIRECT_URI)
@google.authorized_handler
def authorized(resp):
    access_token = resp['access_token']
    session['access_token'] = access_token, ''
    return redirect(url_for('index'))

'''
    get_access_token returns the access_token from the flask session
'''

@google.tokengetter
def get_access_token():
    return session.get('access_token')

'''
    main runs the app
'''

def main():
    app.run()

if __name__ == '__main__':
    main()
