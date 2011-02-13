# Title:		Python Playfair
# Version:		1.0
# Date:			2011-02-11
# Description:	A Python implementation of the Playfair cipher.
# Author:		Joel Verhagen
# Website:		http://www.joelverhagen.com
# Licensing:	Do whatever the heck you want with it. Golly, you don't even need to credit me if you don't want. Just don't say you originally wrote it. That would just make me sad.

import re

class PlayfairError(Exception):
	def __init__(self, message):
		print message

class Playfair:
	# omissionRule determines which omission rule you want to use (go figure). See the list at the beginning of the constructor
	# doublePadding determines what letter you would like to use to pad a digraph that is double letters
	# endPadding determines what letter you would like to use to pad the end of an input containing an odd number of letters
	def __init__(self, omissionRule = 0, doublePadding = 'X', endPadding = 'X'):
		omissionRules = [
			'Merge J into I',
			'Omit Q',
			'Merge I into J',
		]
		if omissionRule >= 0 and omissionRule < len(omissionRules):
			self.omissionRule = omissionRule
		else:
			raise PlayfairError('Possible omission rule values are between 0 and ' + (len(omissionRules) - 1) + '.')
		
		# start with a blank password
		self.grid = self.generateGrid('')
		
		# make sure the input for the double padding character is valid
		if len(doublePadding) != 1:
			raise PlayfairError('The double padding must be a single character.')
		elif not self.isAlphabet(doublePadding):
			raise PlayfairError('The double padding must be a letter of the alphabet.')
		elif doublePadding not in self.grid:
			raise PlayfairError('The double padding character must not be omitted by the omission rule.')
		else:
			self.doublePadding = doublePadding.upper()
		
		# make sure the input for the end padding character is valid 
		if len(endPadding) != 1:
			raise PlayfairError('The end padding must be a single character.')
		elif not self.isAlphabet(endPadding):
			raise PlayfairError('The end padding must be a letter of the alphabet.')
		elif endPadding not in self.grid:
			raise PlayfairError('The end padding character must not be omitted by the omission rule.')
		else:
			self.endPadding = endPadding.upper()
	
	# returns None if the letter should be discarded, else returns the converted letter
	def convertLetter(self, letter):
		if self.omissionRule == 0:
			if letter == 'J':
				letter = 'I'
			return letter
		elif self.omissionRule == 1:
			if letter == 'Q':
				letter = None
			return letter
		elif self.omissionRule == 2:
			if letter == 'I':
				letter = 'J'
			return letter
		else:
			raise PlayfairError('The omission rule provided has not been configured properly.')
	
	# returns the alphabet used by the cipher (takes into account the omission rule)
	def getAlphabet(self):
		fullAlphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
		alphabet = ''
		
		for letter in fullAlphabet:
			letter = self.convertLetter(letter)
			if letter is not None and letter not in alphabet:
				alphabet += letter
		
		return alphabet
	
	# generates the 25 character grid based on the omission rule and the given password
	def generateGrid(self, password):
		grid = ''
		alphabet = self.getAlphabet()
		
		for letter in password:
			if letter not in grid and letter in alphabet:
				grid += letter
		
		for letter in alphabet:
			if letter not in grid:
				grid += letter
		
		return grid
	
	# splits the text input into digraphs
	def generateDigraphs(self, input):
		input = self.toAlphabet(input).upper()
		inputFixed = ''
		
		for i in range(len(input)):
			letter = self.convertLetter(input[i])
			if letter is not None:
				inputFixed += letter
		
		digraphs = []
		
		counter = 0
		while counter < len(inputFixed):
			digraph = ''
			if counter + 1 == len(inputFixed): # we have reached the end of the inputFixed
				digraph = inputFixed[counter] + self.endPadding
				digraphs.append(digraph)
				break
			elif inputFixed[counter] != inputFixed[counter + 1]: # we just need to create a normal digraph
				digraph = inputFixed[counter] + inputFixed[counter + 1]
				digraphs.append(digraph)
				counter += 2
			else: # we have a double letter digraph, so we add the double padding
				digraph = inputFixed[counter] + self.doublePadding
				digraphs.append(digraph)
				counter += 1
		
		return digraphs
	
	# encrypts a digraph using the defined grid
	def encryptDigraph(self, input):
		if len(input) != 2:
			raise PlayfairError('The digraph that is going to be encrypted must be exactly 2 characters long.')
		elif not self.isUpper(input):
			raise PlayfairError('The digraph that is going to be encrypted must contain only uppercase letters of the alphabet.')
		
		firstLetter = input[0]
		secondLetter = input[1]
		
		firstLetterPosition = self.grid.find(firstLetter)
		secondLetterPosition = self.grid.find(secondLetter)
		
		firstLetterCoordinates = (firstLetterPosition % 5, firstLetterPosition / 5)
		secondLetterCoordinates = (secondLetterPosition % 5, secondLetterPosition / 5)
		
		if firstLetterCoordinates[0] == secondLetterCoordinates[0]: # letters are in the same column
			firstEncrypted = self.grid[(((firstLetterCoordinates[1] + 1) % 5) * 5) + firstLetterCoordinates[0]]
			secondEncrypted = self.grid[(((secondLetterCoordinates[1] + 1) % 5) * 5) + secondLetterCoordinates[0]]
		elif firstLetterCoordinates[1] == secondLetterCoordinates[1]: # letters are in the same row
			firstEncrypted = self.grid[(firstLetterCoordinates[1] * 5) + ((firstLetterCoordinates[0] + 1) % 5)]
			secondEncrypted = self.grid[(secondLetterCoordinates[1] * 5) + ((secondLetterCoordinates[0] + 1) % 5)]
		else: # letters are not in the same row or column, i.e. they form a rectangle
			firstEncrypted = self.grid[(firstLetterCoordinates[1] * 5) + secondLetterCoordinates[0]]
			secondEncrypted = self.grid[(secondLetterCoordinates[1] * 5) + firstLetterCoordinates[0]]
		
		return firstEncrypted+secondEncrypted
	
	# decrypts a digraph using the defined grid
	def decryptDigraph(self, input):
		if len(input) != 2:
			raise PlayfairError('The digraph that is going to be encrypted must be exactly 2 characters long.')
		elif not self.isUpper(input):
			raise PlayfairError('The digraph that is going to be encrypted must contain only uppercase letters of the alphabet.')
		
		firstEncrypted = input[0]
		secondEncrypted = input[1]
		
		firstEncryptedPosition = self.grid.find(firstEncrypted)
		secondEncryptedPosition = self.grid.find(secondEncrypted)
		
		firstEncryptedCoordinates = (firstEncryptedPosition % 5, firstEncryptedPosition / 5)
		secondEncryptedCoordinates = (secondEncryptedPosition % 5, secondEncryptedPosition / 5)
		
		if firstEncryptedCoordinates[0] == secondEncryptedCoordinates[0]: # letters are in the same column
			firstLetter = self.grid[(((firstEncryptedCoordinates[1] - 1) % 5) * 5) + firstEncryptedCoordinates[0]]
			secondLetter = self.grid[(((secondEncryptedCoordinates[1] - 1) % 5) * 5) + secondEncryptedCoordinates[0]]
		elif firstEncryptedCoordinates[1] == secondEncryptedCoordinates[1]: # letters are in the same row
			firstLetter = self.grid[(firstEncryptedCoordinates[1] * 5) + ((firstEncryptedCoordinates[0] - 1) % 5)]
			secondLetter = self.grid[(secondEncryptedCoordinates[1] * 5) + ((secondEncryptedCoordinates[0] - 1) % 5)]
		else: # letters are not in the same row or column, i.e. they form a rectangle
			firstLetter = self.grid[(firstEncryptedCoordinates[1] * 5) + secondEncryptedCoordinates[0]]
			secondLetter = self.grid[(secondEncryptedCoordinates[1] * 5) + firstEncryptedCoordinates[0]]
			
		return firstLetter+secondLetter
	
	# encrypts text input
	def encrypt(self, input):
		digraphs = self.generateDigraphs(input)
		encryptedDigraphs = []
		
		for digraph in digraphs:
			encryptedDigraphs.append(self.encryptDigraph(digraph))
		
		return ''.join(encryptedDigraphs)
	
	# decrypts text input
	def decrypt(self, input):
		digraphs = self.generateDigraphs(input)
		
		decryptedDigraphs = []
		
		for digraph in digraphs:
			decryptedDigraphs.append(self.decryptDigraph(digraph))
		
		return ''.join(decryptedDigraphs)
	
	# sets the password for upcoming encryptions and decryptions
	def setPassword(self, password):
		password = self.toAlphabet(password).upper()
		
		self.grid = self.generateGrid(password)
	
	# strips out all non-alphabetical characters from the input
	def toAlphabet(self, input):
		return re.sub('[^A-Za-z]', '', input)
	
	# tests whether the string only contains alphabetical characters
	def isAlphabet(self, input):
		if re.search('[^A-Za-z]', input):
			return False
		return True
	
	# tests whether the string only contains uppercase alphabetical characters
	def isUpper(self, input):
		if re.search('[^A-Z]', input):
			return False
		return True