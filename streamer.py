from __future__ import unicode_literals
from TwitterAPI import *
import os
import socket
from threading import Thread
import thread
import cPickle as pickle
import json
import traceback
import pprint
import datetime
from pytz import timezone

pp = pprint.PrettyPrinter(indent=2)
tz = timezone("Asia/Kolkata")
fmt = '%H:%M:%S %Z'

class Streamer:
    def __init__(self,twitter_creds,host,port):
        self.api = TwitterAPI(twitter_creds["consumer_key"], twitter_creds["consumer_secret"],
                              twitter_creds["access_token_key"], twitter_creds["access_token_secret"])
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((host, port))
        print host,port
        self.s.listen(5)
        while True:
            try:
                c, addr = self.s.accept()
                self.c = c
                self.stream()
            except Exception  as e:
                print e

    def uncode(self, text):
        try:
            t = text
            if t:
                if not (type(t) is str or type(t) is unicode):
                    t = str(t)
                return ''.join([i if ord(i) < 128 else '' for i in t])
            else:
                return t
        except Exception as e:
            traceback.print_exc()

    def get_time(self, ms):
        t = datetime.datetime.fromtimestamp(int(ms)/1000.0)
        return tz.localize(t).strftime(fmt)

    def stream(self):
        try:
            print "in stream"
            iterator = self.api.request('statuses/filter', {'track': 'google', 'language':'en'}).get_iterator()
            for item in iterator:
                if 'text' in item:
                    ''' keys - value
                        --------------------------
                        text - main text
                        source - techinical source (android/ios/web etc.)
                        coordinates - coordinates
                        geo - geo
                        filter_level - filter_level
                        place["name"] - name of place
                        timestamp_ms - time in milliseconds
                        user["name"]  - handle
                        user["screen_name"]  - name
                        id - id of tweet
                        user["location"] - location
                        user["id"] - user id
                        user["description"] - user description
                        user["profile_image_url"] - user profile_image_url
                    '''
                    senditem = {}
                    senditem['text'] = self.uncode(item['text'])
                    senditem['source'] = self.uncode(item['source'])
                    senditem['coordinates'] = self.uncode(item['coordinates'])
                    senditem['geo'] = self.uncode(item['geo'])
                    senditem['filter_level'] = self.uncode(item['filter_level'])
                    senditem['timestamp_ms'] = self.uncode(self.get_time(item['timestamp_ms']))
                    senditem['id'] = self.uncode(item['id'])
                    if item['place']:
                        senditem['place'] = self.uncode(item['place']['name'])
                    else:
                        senditem['place'] = self.uncode("N/A")
                    senditem['user_id'] = self.uncode(item['user']["id"])
                    senditem['user_name'] = self.uncode(item['user']["name"])
                    senditem['user_handle'] = self.uncode(item['user']["screen_name"])
                    senditem['user_location'] = self.uncode(item['user']["location"])
                    senditem['user_description'] = self.uncode(item['user']["description"])
                    senditem['user_profile_image_url'] = self.uncode(item['user']["profile_image_url"])

                    senditem = json.dumps(senditem)
                    self.c.send(senditem)
                    self.c.send("\n")
                elif 'disconnect' in item:
                    event = item['disconnect']
                    if event['code'] in [2,5,6,7]:
                        raise Exception(event['reason'])
                    else:
                        pass
        except TwitterRequestError as e:
            if e.status_code < 500:
                raise
            else:
                pass
        except TwitterConnectionError:
            pass
        except Exception as e:
            print "Exception", e
            pass


if __name__=="__main__":
    twitter_creds = {}
    twitter_creds["consumer_key"] = "VVh4AvzH5ChbnkYiUJ3AELu5k"
    twitter_creds["consumer_secret"] = "4w2JkQKfg9yOFwA2vUxjcfBw2BoLXRd6S6XuBfdXd8kE2Evvpn"
    twitter_creds["access_token_key"] = "3307532864-LLlOcta1cGCqwXlgolGd13W7OpCUzoVYlFU4pm3"
    twitter_creds["access_token_secret"] = "wLzVbp96Z9nQpk3FHrmgIGcDUsrmB1pcTmTi0t3b8YcbT"
    port = 9999
    host = "localhost"
    stream = Streamer(twitter_creds,host,port)
