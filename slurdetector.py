from itertools import product  # needed for slur obscurity permutations
import unidecode  # needed for cleaning accents and diacritic marks
import re

from utils.base import get_page
from utils.database import db_session, Slur, Goodword

slurs = []
goodword = []
slurs_list = []


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

    return ["".join(permutations) for permutations in product(*possibles)]


def get_slurs(*args, page=None, per_page=10):
    if page is None:
        return slurs_list
    else:
        return get_page(sorted(slurs_list), page, per_page)


def get_slurs_leet():
    return slurs


def get_goodwords(*args, page=None, per_page=10):
    if page is None:
        return goodword
    else:
        return get_page(sorted(goodword), page, per_page)


def load_slurdetector():
    load_slurs()
    load_goodwords()


def rm_slur(slur):
    if slur in slurs_list:
        slurs_list.remove(slur)
        slurs.clear()
        for item in slurs_list:
            slurs.extend(leet(item))

    with db_session() as session:
        session.query(Slur).filter_by(slur=slur).delete()
        session.commit()
    
    load_goodwords()


def rm_goodword(word: str):
    if word in goodword:
        goodword.remove(word)
    with db_session() as session:
        session.query(Goodword).filter_by(goodword=word).delete()
        session.commit()


def load_slurs():
    slurs.clear()
    slurs_list.clear()
    with db_session() as session:
        slur_list: list[Slur] = session.query(Slur).all()
        for slur in slur_list:
            slurs_list.append(slur.slur)
            slurs.extend(leet(slur.slur))


def load_goodwords():
    goodword.clear()
    with db_session() as session:
        goodword_list: list[Goodword] = session.query(Goodword).all()
        for word in goodword_list:
            goodword.append(word.goodword)


def clear_string(string: str) -> str:
    """clean up the message by eliminating special characters and making the entire message lowercase."""
    special_characters = ["#", "%", "&", "[", "]", " ", "]", "_", "-", "<", ">", "'"]

    string = string.lower()
    string = unidecode.unidecode(string)

    for char in special_characters:
        string = string.replace(char, "")

    return string


def detect_slur(message: str) -> list[str]:

    cleaned_message: str = clear_string(message)
    message = message.lower()
    message = message.replace(" ", "")

    slur_counter: int = 0  # more like based_counter, amirite?
    slur_list: list[str] = []

    for slur in slurs:
        s1: int = message.count(slur)
        s2: int = cleaned_message.count(slur)
        if s1 > 0:
            slur_list.append(slur)
            slur_counter += s1
        elif s2 > 0:
            slur_list.append(slur)
            slur_counter += s2

    for word in goodword:
        g1: int = message.count(word)
        g2: int = cleaned_message.count(word)
        if g1 > 0:
            slur_counter -= g1
        elif g2 > 0:
            slur_counter -= g2

    if slur_counter > 0:
        return slur_list
    else:
        return []


# I sure hope My pakistani friends and myself will be able to enjoy our spicy noodles among the beautiful skyscrapers of Montenegro    --Pando
