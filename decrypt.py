
import argparse
import os
import base64
from Crypto.Cipher import XOR

def key():
	if os.path.isfile('key'):
		with open('key') as f:
			key = f.read().strip()
	else:
		key = os.environ['key']
	return key

def encrypt(key, plaintext):
	cipher = XOR.new(key)
	return base64.b64encode(cipher.encrypt(plaintext))

def decrypt(key, ciphertext):
	cipher = XOR.new(key)
	return cipher.decrypt(base64.b64decode(ciphertext))

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--i',required=True)
	parser.add_argument('--o',required=True)
	args = parser.parse_args()

	with open(args.i,'rb') as inF, open(args.o,'wb') as outF:
		outF.write(decrypt(key(),inF.read()))

