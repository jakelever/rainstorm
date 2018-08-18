
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

def getTweets(screen_name):
	all_statuses = []
	max_id = None
	while True:
		if max_id is None:
			statuses = api.GetUserTimeline(screen_name=screen_name,count=200)
		else:
			statuses = api.GetUserTimeline(screen_name=screen_name,count=200,max_id=max_id)

		all_statuses_set = set(all_statuses)
		new_statuses = [ s for s in statuses if not s in all_statuses_set ]

		if len(new_statuses) == 0:
			break

		all_statuses += new_statuses
		max_id = all_statuses[-1].id

	return all_statuses

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
	search_term = settings[5]

	api = twitter.Api(consumer_key=consumer_key,
			consumer_secret=consumer_secret,
			access_token_key=access_token,
			access_token_secret=access_token_secret,
			tweet_mode='extended',
			sleep_on_rate_limit=True)

	statuses = getTweets(account)
	recentTweets = [ status.full_text.strip() for status in statuses ]

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
	potentialTweets = [ t for t in potentialTweets if t and len(t) < 280 and not t in recentTweets ]

	assert len(potentialTweets) > 0

	selectedTweet = random.choice(potentialTweets)

	status = api.PostUpdate(selectedTweet)

	print("Message sent")

	next_cursor = -1
	currently_following = []
	while True:
		next_cursor,previous_cursor,users = api.GetFriendsPaged(screen_name=account,skip_status=True,count=200,include_user_entities=False,cursor=next_cursor)
		if len(users) == 0:
			break
		currently_following += [ u.screen_name for u in users ]
	currently_following = set(currently_following)

	oneWeek = 7*24*60*60
	now = time.time()

	potentials = []
	for page in range(1,20):
		users = api.GetUsersSearch(term=search_term,count=20,page=page)
		if len(users) == 0:
			break

		userDicts = [ u.AsDict() for u in users ]
		for ud in userDicts:
			screen_name = ud['screen_name']

			if not 'status' in ud:
				continue
			if screen_name in currently_following:
				continue

			lastTweetDate = ud['status']['created_at']

			lastTweetDate_datetime = datetime.datetime.strptime(lastTweetDate, '%a %b %d %H:%M:%S %z %Y')
			secondsSinceLastTweet = now - lastTweetDate_datetime.timestamp()

			if secondsSinceLastTweet < oneWeek:
				potentials.append(screen_name)

	potentials = sorted(list(set(potentials)))
	if len(potentials) > 0:
		selected = random.choice(potentials)
		api.CreateFriendship(screen_name=selected)
		print("Found a friend")

