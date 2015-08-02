# AUTHOR Brynn Arborico
# DATE July 13, 2015
# COMPANY Upstream Health

# NAME Twitter-Mining for Real-Time Diabetes Tracking

# SOURCES Used code from marcobonzanini.com, stackoverflow.com


import tweepy # library to work with Twitter's API
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import json


# FILTER PARAMETERS

# Set desired geographical region; currently a box around the greater LA area
# (coordinates from http://boundingbox.klokantech.com/)
WORLD_GEOBOX = [-180,-90,180,90]
LA_GEOBOX = [-119, 33, -116, 34]

# gets keywords to monitor
keyWords = []
with open('SearchTerms.txt', 'r') as f:
    for line in f:
        searchTerm = line.rstrip().lower()
        keyWords.append(searchTerm)

# gets words to avoid        
omitWords = []
with open('OmitTerms.txt', 'r') as f:
    for line in f:
        omitTerm = line.rstrip().lower()
        omitWords.append(omitTerm)

def diseaseContent(text, keyWords, omitWords):
    '''Filters for messages containing certain desired words (stored in the list
    keyWords) and excluding others (contained in the list omitWords)'''
    text = text.lower()
    for word in omitWords:
        if word in text:
            return False
    for word in keyWords:
        if word in text:
            return True
    return False


# USING TWITTER'S STREAMING API

consumerKey = '****'
consumerSecret = '****'

# lets the app access twitter on behalf of my account
accessToken = '****'
accessSecret = '****'

class MyListener(StreamListener):

    def on_data(self, data):
        '''Streaming a single tweet'''
        try:
            # adds stream to the given file; each tweet will have time, location,
            # language, and message
            with open('TwitterStream.txt', 'a') as f:
                dataDict = json.loads(data) # contains the tweet's fields
                message = dataDict['text']
                
                if diseaseContent(message, keyWords, omitWords):

                    location = dataDict['coordinates'] # nullable (common)
                    if location is not None: # there is a geotag for that tweet
                        location = location['coordinates']
                    location = repr(location)

                    time = dataDict['created_at']

                    language = dataDict['lang'] # nullable (rare)
                    if language is None:
                        language = repr(language)
                    
                    toStore = time + " :: " + location + " :: " + language + " :: " + message + "\n"
                    f.write(toStore)
                return True

        except BaseException as e:
            print("Error on_data: %s" % str(e))
        return True
 
    def on_error(self, status):
        print(status)
        return True


# RUN PROGRAM

if __name__ == '__main__':
    auth = OAuthHandler(consumerKey, consumerSecret)
    auth.set_access_token(accessToken, accessSecret)
     
    api = tweepy.API(auth)

    twitterStream = Stream(auth, MyListener())
    twitterStream.filter(locations=LA_GEOBOX)

