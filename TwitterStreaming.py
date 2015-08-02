# AUTHOR Brynn Arborico
# DATE July 13, 2015
# COMPANY Upstream Health

# NAME Twitter-Mining for Real-Time Disease Tracking

# SOURCES Used code from marcobonzanini.com, stackoverflow.com


import tweepy # library to work with Twitter's API
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import json
import time

def parseTerms(text):
    '''takes a string and parses it (separating by line breaks) to create a list
    of terms, which is returned'''
    terms = []
    term = ""
    for char in text:
        if char == "\n" or char == "\r":
            if term:
                terms.append(term.lower())
                term = ""
        else:
            term += char
    terms.append(term.lower()) # gets the last term
    return terms

def hasDesiredContent(text, includeTerms, excludeTerms):
    '''filters for messages containing certain desired words (stored in the list
    keyWords) and excluding others (contained in the list omitWords)'''
    text = text.lower()
    for word in excludeTerms:
        if word in text:
            return False
    if includeTerms: # list not empty
        for word in includeTerms:
            if word in text:
                return True
    else:
        return True
    return False


class TwitterListener(StreamListener):
    '''object to handle Twitter streaming'''

    
    def __init__(self, includeTerms, excludeTerms):
        '''takes in a list of terms to include and a list of terms to exclude;
        then creates a streaming object'''
        
        self.includeTerms = includeTerms
        self.excludeTerms = excludeTerms

        self.maxTweets = 5
        self.numTweets = 0

        self.tweets = ""

        self.waitTime = 5
        self.waitTime420 = 60
        
    def on_data(self, data):
        '''streams a single tweet
        called whenever raw data is received from the connection'''
        
        try:
            # adds stream to the given file; each tweet will have time, location,
            # language, and message
            dataDict = json.loads(data) # contains the tweet's fields
            message = dataDict['text']
            
            # limit number of tweets
            if self.numTweets >= self.maxTweets:
                return False
            # filter tweets by content
            #print "checking content", self.numTweets, " message: ", message
            if hasDesiredContent(message, self.includeTerms, self.excludeTerms):

                location = dataDict['coordinates'] # nullable (common)
                if location is not None: # there is a geotag for that tweet
                    location = location['coordinates']
                location = repr(location)

                time = dataDict['created_at']

                language = dataDict['lang'] # nullable (rare)
                if language is None:
                    language = repr(language)
                
                toStore = time + " :: " + location + " :: " + language + " :: " + message + "\n"
                self.tweets += toStore + "\n"

                self.numTweets += 1
            return True

        except BaseException as e:
            print("Error on_data: %s" % str(e))
        return True
 
    def on_error(self, status):
        '''reports errors and implements backoff
        called whenever a non-200 status code is called'''
        
        print "error: ", status
        
        # avoid rate limiting
        if status == 420:
            # stop streaming if wait time exceeds 4min
            if self.waitTime420 > 360:
                return False
            time.sleep(self.waitTime420)
            self.waitTime420 *= 2
            
        else:
            time.sleep(self.waitTime)
            if self.waitTime <= 320:
                self.waitTime *= 2
                
        return True

    def on_limit(self, track):
        '''stops streaming on receipt of a limitation notice'''
        
        print "limited"
        return False


# RUN PROGRAM

def streamTweets(geobox, includeString, excludeString):
    '''Takes as inputs:
            geobox (latitudinal and longitudinal boundaries), a list of the form
            [W, S, E, N]
            includeString, terms to include, separated by line breaks
            excludeString, terms to include, separated by line breaks
    And then returns a stream of tweets, filtered by those inputs'''

    # gets term lists
    includeTerms = parseTerms(includeString)
    excludeTerms = parseTerms(excludeString)

    # USING TWITTER'S STREAMING API

    consumerKey = '****'
    consumerSecret = '****'

    # lets the app access twitter on behalf of my account
    accessToken = '****'
    accessSecret = '****'

    auth = OAuthHandler(consumerKey, consumerSecret)
    auth.set_access_token(accessToken, accessSecret)
     
    api = tweepy.API(auth)

    myListener = TwitterListener(includeTerms, excludeTerms)
    twitterStream = Stream(auth, myListener)
    twitterStream.filter(locations=geobox)

    return myListener.tweets
