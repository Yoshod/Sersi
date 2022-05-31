from itertools import product   # needed for slur obscurity permutations
import unidecode                # needed for cleaning accents and diacritic marks
slurs = []
slurs_list = []
goodword = []


def leet(word):
    substitutions = {
        "a": ("a", "@", "*", "4", "æ", "λ", "δ"),
        "i": ("i", "*", "l", "1", "!", "¡"),
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

    return [''.join(permutations) for permutations in product(*possibles)]


def get_slurs(page=None):
    if page is None:
        return slurs_list
    else:
        pages = 1 + (len(slurs_list) - 1) // 100

        index = page - 1
        if index < 0:
            index = 0
        elif index >= pages:
            index = pages - 1

        if index == (pages - 1):
            return slurs_list[index * 100:], pages, index + 1
        else:
            return slurs_list[index * 100: index * 100 + 100], pages, index + 1


def get_goodwords(page=None):
    if page is None:
        return goodword
    else:
        pages = 1 + (len(goodword) - 1) // 100

        index = page - 1
        if index < 0:
            index = 0
        elif index >= pages:
            index = pages - 1

        if index == (pages - 1):
            return goodword[index * 100:], pages, index + 1
        else:
            return goodword[index * 100: index * 100 + 100], pages, index + 1


def load_slurdetector():
    load_slurs()
    load_goodwords()


def rmSlur(ctx, slur):
    lines = []
    if slur in slurs_list:
        slurs_list.remove(slur)
        slurs.clear()
        for item in slurs_list:
            slurs.extend(leet(item))
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
    slurs.clear()
    slurs_list.clear()
    with open("slurs.txt", "r") as file:
        for line in file:
            line = line.replace('\n', '')
            slurs_list.append(line)
            slurs.extend(leet(line))


def load_goodwords():
    goodword.clear()
    with open("goodword.txt", "r") as file:
        for line in file:
            line = line.replace('\n', '')
            goodword.append(line)


def clearString(string):
    """cleaning up the message by eliminating special characters and making the entire message lowercase"""
    special_characters = ['#', '%', '&', '[', ']', ' ', ']', '_', '-', '<', '>']

    string = string.lower()
    string = unidecode.unidecode(string)

    for char in special_characters:
        string = string.replace(char, '')

    return string


def detectSlur(messageData):
    if not str(messageData).startswith("s!"):  # ignores if message was a command

        cleanedMessageData = clearString(messageData)
        messageData = messageData.lower()
        messageData = messageData.replace(' ', '')

        slur_counter = 0  # more like based_counter, amirite?
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
    else:
        return []


# I sure hope My pakistani friends and myself will be able to enjoy our spicy noodles among the beautiful skyscrapers of Montenegro    --Pando
