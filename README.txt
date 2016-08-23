Analysis of tweets to determine depressing tweets

Uses Python, MongoDB and Apache Spark
Uses python libraries: flask, pymongo, textblob
Uses foreman to run the servers

Installation: Refer to INSTALL.txt

Usage: Refer to RUNNING.txt

Files:

streamer.py: the file to convert the twitter stream to socket stream
analyse.py: stream the tweets using apache spark and filter the positive and negative tweets
server.py: Runs a flask webserver to present the tweets
Procfile: Defines the server configuration for foreman
data/filter_words.txt: defines the list of filter words
data/happy_words.txt: defines the list of happy words
templates/index.html: jinja2 template for home page
templates/tweet.html: jinja2 template for tweet page
templates/login.html: jinja2 template for login page

Mechanism

streamer.py creates a twitter stream connection and then sends it over via socket using json pickling
analyse.py creates a spark job to connect to the stream and filter the tweets
server.py runs a webserver to show the tweets graphically
