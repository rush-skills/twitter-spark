from pymongo import MongoClient
from flask import *
from bson import json_util, ObjectId
import json

app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
connection = MongoClient('mongodb://localhost:27017/')
db = connection.t4.tweets
pos_db = connection.t4.pos
neg_db = connection.t4.neg

users = {"google":"password"}

def get_db(stage):
    if stage:
        if stage=="pos":
            return pos_db
        if stage=="neg":
            return neg_db
    return db

def generate_full_image(image):
    x = image.split(".")
    pre = x[:-2]
    extn = x[-1]
    x = '_'.join(x[-2].split("_")[:-1])
    return '.'.join(pre+[x]+[extn])

def get_coordinates(tweet):
    if tweet["geo"]:
        return tweet["geo"]
    if tweet["coordinates"]:
        return tweet["coordinates"]
    return "N/A"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        password = request.form['password']
        if user in users:
            if users[user]==password:
                session['username'] = user
                return redirect(url_for('root'))
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('root'))

@app.route('/api', methods=['GET'])
def get():
    pos_tweets = list(pos_db.find())[-20::]
    neg_tweets = list(neg_db.find())[-20::]
    pos_tweets_sanitized = json.loads(json_util.dumps(pos_tweets))
    neg_tweets_sanitized = json.loads(json_util.dumps(neg_tweets))
    return jsonify({"pos_tweets":pos_tweets_sanitized,"neg_tweets":neg_tweets_sanitized})

@app.route('/api/<last>', methods=['GET'])
def more(last):
    pos_tweets = list(pos_db.find({"_id": {"$gt": ObjectId(last)}}))
    neg_tweets = list(neg_db.find({"_id": {"$gt": ObjectId(last)}}))
    pos_tweets_sanitized = json.loads(json_util.dumps(pos_tweets))
    neg_tweets_sanitized = json.loads(json_util.dumps(neg_tweets))
    return jsonify({"pos_tweets":pos_tweets_sanitized,"neg_tweets":neg_tweets_sanitized})

@app.route('/tweet/<id>', methods=['GET'])
def tweet(id):
    stage = request.args.get('stage')
    idb = db
    tweets = list(idb.find({"_id": ObjectId(id)}))
    tweet_sanitized = json.loads(json_util.dumps(tweets[0]))
    image = generate_full_image(tweet_sanitized["user_profile_image_url"])
    coordinates = get_coordinates(tweet_sanitized)
    return render_template("tweet.html",tweet=tweet_sanitized,image=image,coordinates=coordinates)

@app.route('/')
def root():
    user = None
    if 'username' in session:
        user = session['username']
    return render_template("index.html", user=user)

if __name__ == '__main__':
    app.run(host='0.0.0.0',threaded=True, port=5050,debug=True)
