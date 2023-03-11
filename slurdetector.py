from itertools import product   # needed for slur obscurity permutations
import unidecode                # needed for cleaning accents and diacritic marks

from baseutils import get_page
import configutils

slurs = []
goodword = []
slurs_list = []

config = configutils.Configuration.from_yaml_file("./persistent_data/config.yaml")


def leet(word):
    substitutions = {
        "a": ("a", "@", "*", "4", "æ", "λ", "δ"),
        "i": ("i", "*", "l", "1", "!", "¡", "j"),
        "o": ("o", "*", "0", "@", "θ"),
        "u": ("u", "*", "v"),
        "v": ("v", "*", "u", "\\/"),
        "l": ("l", "1"),
        "e": ("e", "*", "3", "€", "ε"),
        "s": ("s", "$", "5"),
        "t": ("t", "7", "†", "ł"),
        "y": ("y", "¥"),
        "n": ("n", "и", "η"),
        "r": ("r", "я", "®"),
    }
    possibles = []
    for char in word.lower():
        options = substitutions.get(char, char)
        possibles.append(options)

    return [''.join(permutations) for permutations in product(*possibles)]


def get_slurs(config=None, page=None, per_page=10):
    if page is None:
        return slurs_list
    else:
        return get_page(sorted(slurs_list), page, per_page)


def get_slurs_leet():
    return slurs


def get_goodwords(config=None, page=None, per_page=10):
    if page is None:
        return goodword
    else:
        return get_page(sorted(goodword), page, per_page)


def load_slurdetector():
    load_slurs()
    load_goodwords()


def rm_slur(slur):
    lines = []
    if slur in slurs_list:
        slurs_list.remove(slur)
        slurs.clear()
        for item in slurs_list:
            slurs.extend(leet(item))

    slur_comb(slur)

    with open(config.datafiles.slurfile, "r") as fp:
        lines = fp.readlines()

    with open(config.datafiles.slurfile, "w") as fp:
        for line in lines:
            if line.strip("\n") != slur:
                fp.write(line)


def slur_comb(slur):
    for word in goodword:
        if slur in word:
            rm_goodword(word)


def rm_goodword(word):
    lines = []
    if word in goodword:
        goodword.remove(word)
    with open(config.datafiles.goodwordfile, "r") as fp:
        lines = fp.readlines()

    with open(config.datafiles.goodwordfile, "w") as fp:
        for line in lines:
            if line.strip("\n") != word:
                fp.write(line)


def load_slurs():
    slurs.clear()
    slurs_list.clear()
    with open(config.datafiles.slurfile, "r") as file:
        for line in file:
            line = line.replace('\n', '')
            slurs_list.append(line)
            slurs.extend(leet(line))


def load_goodwords():
    goodword.clear()
    with open(config.datafiles.goodwordfile, "r") as file:
        for line in file:
            line = line.replace('\n', '')
            goodword.append(line)


def clear_string(string):
    """clean up the message by eliminating special characters and making the entire message lowercase."""
    special_characters = ['#', '%', '&', '[', ']', ' ', ']', '_', '-', '<', '>', '\'']

    string = string.lower()
    string = unidecode.unidecode(string)

    for char in special_characters:
        string = string.replace(char, '')

    return string


def detect_slur(messageData):
    if str(messageData).startswith("s!"):  # ignores if message was a command
        return []

    cleanedMessageData = clear_string(messageData)
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


# I sure hope My pakistani friends and myself will be able to enjoy our spicy noodles among the beautiful skyscrapers of Montenegro    --Pando
