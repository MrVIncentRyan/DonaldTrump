
import nltk
import sys
import sqlite3
import string
import re
import praw
import time
import datetime 
import tweepy
import math
import praw
from collections import Counter

data = sqlite3.connect('users.db')
cur = data.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS users(username, score)')
data.commit()

consumer_key = 'CAhhQzaLq5R5RUdnGe5dlQRbS'
consumer_secret = 'RIA7Lh4CjHYyTjpeWefDHEbnIcFpNxcWnZ1FocVy12bTp04qWM'
access_token_key = '819717298479046656-k7PVX591CMT97JoKP50LTuXFzf3cyBc'
access_token_secret = 'DtWb9V8YnWTgjUtjklKOA0CS8hi2MLybxdtT5QFhpnIse'
twitter_uri = 'http://howtrumpareyou.com/'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token_key, access_token_secret)
api = tweepy.API(auth)

user_agent = 'Extracts text from comments on Reddit for comparison purposes'
reddit = praw.Reddit(username='ComparisonBot',password='r3dd1t2016',client_id='slOtREeDSDjALg',client_secret='w0TBMNHGcZ0j9W6rqrCrUYM08nE', user_agent=user_agent)

trump = None
compare = ''
contrast = ''

class user(object):

	def __init__(self, account):
		self.account = account

	def get_information(self):
		tweet_list = []
		user_tweets = api.user_timeline(self.account, count=200)
		for tweet in user_tweets:
			tweet_list.append(tweet)
		last = tweet_list[-1].id - 1
		while len(user_tweets) > 0:
			user_tweets = api.user_timeline(self.account, count=200, max_id=last)
			for tweet in user_tweets:
				tweet_list.append(tweet)
			last = tweet_list[-1].id - 1
		master = [str(tweet.text) for tweet in tweet_list]
		return master

	def sort_information(self):
		tweets = self.get_information()
		tweet_words = nltk.word_tokenize(str(tweets))
		return (tweet_words,tweets)

class comparison(object):

	def __init__(self, person):
		self.person = user(person).sort_information()
		self.name = person
		self.response()

	def calculate_similarity(self):
		argument_1 = Counter(trump[0])
		argument_2 = Counter(self.person[0])
		terms = set(argument_1).union(argument_2)
		product = sum(argument_1.get(i,0) * argument_2.get(i,0) for i in terms)
		first = math.sqrt(sum(argument_1.get(i,0)**2 for i in terms))
		second = math.sqrt(sum(argument_2.get(i,0)**2 for i in terms))
		solution = product/(first*second)
		length_1 = sum(argument_1.values())
		length_2 = sum(argument_2.values())
		lengths = min(length_1,length_2) / float(max(length_1,length_2))
		similarity = round(lengths*solution * 100,2)
		return similarity

	def sentence_similarity(self):
		sim = self.calculate_similarity()
		arg = Counter(str(trump[1]))
		kwarg = Counter(str(self.person[1]))
		intercept = set(arg.keys()) & (set(kwarg.keys()))
		num = sum([arg[i] * kwarg[i] for i in intercept])
		first = sum([arg[i]**2 for i in arg.keys()])
		second = sum([kwarg[i]**2 for i in kwarg.keys()])
		den = math.sqrt(first) * math.sqrt(second)
		if not den:
			similarity = 0.0
		else:
			similarity = float(num)/den
		similarity = round((similarity*sim),2)
		return similarity

	def response(self):
		similarity = self.sentence_similarity()
		print('{} is {} percent like {}!'.format(self.name,similarity,compare))

class redditor_(object):

	def __init__(self,account):
		self.account = account

	def get_information(self):
		comment_list = []
		user = reddit.redditor(str(self.account))
		[comment_list.append(str(comment.body)) for comment in user.comments.new(limit=5000)]
		return comment_list

	def sort_information(self):
		comments = self.get_information()
		comment_words = nltk.word_tokenize(str(comments))
		return (comment_words, comments)

class reddit_comparison(object):

	def __init__(self, person):
		self.person = redditor_(person).sort_information()
		self.name = person
		self.response()

	def calculate_similarity(self):
		argument_1 = Counter(trump[0])
		argument_2 = Counter(self.person[0])
		terms = set(argument_1).union(argument_2)
		product = sum(argument_1.get(i,0) * argument_2.get(i,0) for i in terms)
		first = math.sqrt(sum(argument_1.get(i,0)**2 for i in terms))
		second = math.sqrt(sum(argument_2.get(i,0)**2 for i in terms))
		solution = product/(first*second)
		length_1 = sum(argument_1.values())
		length_2 = sum(argument_2.values())
		lengths = min(length_1,length_2) / float(max(length_1,length_2))
		similarity = round(lengths*solution * 100,2)
		return similarity

	def sentence_similarity(self):
		sim = self.calculate_similarity()
		arg = Counter(str(trump[1]))
		kwarg = Counter(str(self.person[1]))
		intercept = set(arg.keys()) & (set(kwarg.keys()))
		num = sum([arg[i] * kwarg[i] for i in intercept])
		first = sum([arg[i]**2 for i in arg.keys()])
		second = sum([kwarg[i]**2 for i in kwarg.keys()])
		den = math.sqrt(first) * math.sqrt(second)
		if not den:
			similarity = 0.0
		else:
			similarity = float(num)/den
		similarity = round((similarity*sim),2)
		return similarity

	def response(self):
		similarity = self.sentence_similarity()
		print('{} is {} percent like {} as of {}!'.format(self.name,similarity,compare, time.strftime('%D')))

def main():
	global trump, compare, contrast
	account_type = int(input('Is this a Reddit (1) or Twitter (2) account? '))
	if account_type == 2:
		compare = input('Twitter handle 1: ')
		contrast = input('Compare to: ')
		trump = user(compare).sort_information()
		comparison(contrast)
	else:
		compare = input('Reddit username 1: ')
		contrast = input('Reddit username 2: ')
		print('Calculating...')
		trump = redditor_(compare).sort_information()
		reddit_comparison(contrast)

if __name__ == '__main__':
	main()


