from itertools import product 	#needed for slur obscurity permutations
import unidecode				#needed for cleaning accents and diacritic marks
slurs = []
goodword = []

def leet(word):
	substitutions = {
		"a": ("a", "@", "*", "4", "æ", "λ", "δ"),
		"i": ("i", "*", "l", "1"),
		"o": ("o", "*", "0", "@", "θ"),
		"u": ("u", "*", "v"),
		"v": ("v", "*", "u"),
		"l": ("l", "1"),
		"e": ("e", "*", "3", "€", "ε"),
		"s": ("s", "$", "5"),
		"t": ("t", "7"),
		"y": ("y", "¥"),
		"n": ("n", "и", "η"),
		"r": ("r", "я", "®"),
		"t": ("t", "†", "ł"),
	}
	possibles = []
	for char in word.lower():
		options = substitutions.get(char, char)
		possibles.append(options)
		
	#print(possibles)
	return [''.join(permutations) for permutations in product(*possibles)]

def load_slurdetector():
	load_slurs()
	load_goodwords()

def rmSlur(ctx, slur):
	lines = []
	if slur in slurs:
		for slurvariant in leet(slur):
			slurs.remove(slurvariant)
	with open("slurs.txt", "r") as fp:
		lines = fp.readlines()
	
	with open("slurs.txt", "w") as fp:
		for line in lines:
			if line.strip("\n") != slur:
				fp.write(line)

def rmGoodword(ctx, word):
	lines = []
	if word in goodword:
		goodword.remove(word)
	with open("goodword.txt", "r") as fp:
		lines = fp.readlines()
	
	with open("goodword.txt", "w") as fp:
		for line in lines:
			if line.strip("\n") != word:
				fp.write(line)

def load_slurs():
	with open("slurs.txt", "r") as file:
		for line in file:
			line = line.replace('\n', '')
			slurs.extend(leet(line))

def load_goodwords():
	with open("goodword.txt", "r") as file:
		for line in file:
			line = line.replace('\n', '')
			goodword.append(line)

#cleaning up the message by eliminating special characters and making the entire message lowercase    
def clearString(string):
	special_characters = ['!', '#', '%', '&', '[', ']', ' ', ']', '_', '-', '<', '>']

	string = string.lower()
	string = unidecode.unidecode(string)
	
	for char in special_characters:
		string = string.replace(char, '')
	
	return string

def detectSlur(messageData):
	if not str(messageData).startswith("s!"): #ignores if message was a command
		#known slurs and safe words; both lists can be amended freely
		#WORDS MUST BE LOWERCASE
		#slurs = ["spick", "coon", "trann", "fag", "retard", "nigg", "kike", "yid", "chink", "gook", "negro", "shemale", "e621", "killyourself", "kys", "gypsy", "809891646606409779", "spastic", "spas", "spaz", "darky", "gippo", "paki", "spic", "dyke", "shizo", "mong"]
		#goodword = ["skyscraper", "montenegro", "pakistan", "spicy", "among", "mongrel", "schizophrenia", "zelenskys", "tycoon", "suspicious", "racoon", "yiddish"]
		
		cleanedMessageData = clearString(messageData)
		messageData = messageData.lower()
		messageData = messageData.replace(' ', '')
		
		#if a slur is detected, we increase by 1, if a word that cointains a slur but is safe is found, you get a free pass (substracting that increment), any slur that is not exused that way will be reported
		slur_counter = 0 #more like based_counter, amirite?
		slur_list = []
		
		for slur in slurs:
			s1 = messageData.count(slur)
			s2 = cleanedMessageData.count(slur)
			if s1 > 0:
				slur_list.append(slur)
				slur_counter += s1
			elif s2 > 0:
				slur_list.append(slur)
				slur_counter += s2

		for word in goodword:
			g1 = messageData.count(word)
			g2 = cleanedMessageData.count(word)
			if g1 > 0:
				slur_counter -= g1
			elif g2 > 0:
				slur_counter -= g2

		if slur_counter > 0:
			return slur_list
		else:
			return []
	else: return []
	
## I sure hope My pakistani friends and myself will be able to enjoy our spicy noodles among the beautiful skyscrapers of Montenegro	--Pando	