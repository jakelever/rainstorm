
import sys
import argparse
import os
import base64
from Crypto.Cipher import XOR
import random
import twitter
import time
import datetime

def getKey():
	key = None
	if os.path.isfile('key'):
		with open('key') as f:
			key = f.read().strip()
	elif 'key' in os.environ:
		key = os.environ['key']
	return key

def encrypt(key, plaintext):
	cipher = XOR.new(key)
	return base64.b64encode(cipher.encrypt(plaintext))

def decrypt(key, ciphertext):
	cipher = XOR.new(key)
	return cipher.decrypt(base64.b64decode(ciphertext))

def decryptFile(key,filename):
	with open(filename,'rb') as f:
		encrypted = f.read()
	decrypted = str(decrypt(key,encrypted),'utf-8')
	return decrypted.split('\n')

if __name__ == '__main__':
	key = getKey()
	if key is None:
		print("Nothing to see here")
		sys.exit(0)

	day = datetime.datetime.today().weekday()
	if day > 4:
		print("I don't work now")
		sys.exit(0)

	settings = decryptFile(key,'settings')

	account = settings[0]
	consumer_key = settings[1]
	consumer_secret = settings[2]
	access_token = settings[3]
	access_token_secret = settings[4]

	api = twitter.Api(consumer_key=consumer_key,
			consumer_secret=consumer_secret,
			access_token_key=access_token,
			access_token_secret=access_token_secret,
			tweet_mode='extended')

	statuses = api.GetUserTimeline(screen_name=account,count=200)
	recentTweets = [ status.text.strip() for status in statuses ]

	if len(statuses) > 0:
		twelveHours = 60*60*12
		status0 = statuses[0]
		lastTweetTime =  status0.created_at_in_seconds
		secondsSince = time.time() - lastTweetTime
		if secondsSince < twelveHours:
			print("Taking the day off...")
			sys.exit(0)

	potentialTweets = decryptFile(key,'lines')
	potentialTweets = [ t.strip() for t in potentialTweets ]
	potentialTweets = [ t for t in potentialTweets if t and not t in recentTweets ]

	assert len(potentialTweets) > 0

	selectedTweet = random.choice(potentialTweets)

	status = api.PostUpdate(selectedTweet)

	print("Job done")

