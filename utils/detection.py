import re
from itertools import product
from dataclasses import dataclass

from utils.database import db_session, Slur, Goodword


_substitutions = {
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
_sub_regex = {c: f"[{re.escape(''.join(s))}]" for c, s in _substitutions.items()}
_special_regex = re.compile(r"[#%&\[\] _\-<>'\".,]*")


def _leet(word: str) -> list[str]:
    possibles = []
    for char in word.lower():
        options = _substitutions.get(char, char)
        possibles.append(options)

    return ["".join(permutations) for permutations in product(*possibles)]


def highlight_matches(text: str, matches: list[re.Match]) -> str | list[str]:
    highlighted = ""
    pos = 0
    for match in matches:
        highlighted += text[pos : match.start()]
        highlighted += f"***__{text[match.start() : match.end()]}__***"
        pos = match.end()

    highlighted += text[pos:]

    return re.sub(r"__\*{6}__", "", highlighted)


@dataclass
class SlurPattern:
    slur: str
    goodwords: list[str]

    def __post_init__(self):
        self._create_detector_regex()
        self._create_goodword_regex()

    def _create_detector_regex(self):
        self.regex = re.compile(
            _special_regex.pattern.join(
                _sub_regex.get(char, char) for char in self.slur.lower()
            ),
            re.IGNORECASE,
        )

    def _create_goodword_regex(self):
        self.goodword_regex = re.compile(
            "|".join(
                _special_regex.pattern.join(re.escape(char) for char in word)
                for word in self.goodwords
            ),
            re.IGNORECASE,
        )

    def __eq__(self, __value: object) -> bool:
        if self.slur == str(__value):
            return True
        if not isinstance(__value, SlurPattern):
            return False
        return self.slur == __value.slur

    def __hash__(self):
        return hash(self.slur)


class SlurDetector:
    slurs: set[SlurPattern]
    regex: re.Pattern
    unleet: dict[str, str]

    def __init__(self):
        self.load()

    def load(self):
        with db_session() as session:
            slurs = session.query(Slur).all()
            goodwords = session.query(Goodword).all()

            slur_patterns = [
                SlurPattern(
                    slur.slur,
                    [
                        goodword.goodword
                        for goodword in goodwords
                        if goodword.slur == slur.slur
                    ],
                )
                for slur in slurs
            ]

            self.slurs = set(slur_patterns)
            self.regex = re.compile(
                "|".join([slur.regex.pattern for slur in self.slurs]), re.IGNORECASE
            )

            self.unleet = {}
            for slur in self.slurs:
                self.unleet.update({leet: slur.slur for leet in _leet(slur.slur)})

    def find_slurs(self, __value: str) -> dict[str, list[re.Match]]:
        slurs = {}

        pos = 0
        while match := self.regex.search(__value, pos):
            slur = self.unleet[_special_regex.sub("", match.group().lower())]
            if slur not in slurs:
                slurs[slur] = []
            slurs[slur].append(match)
            pos = match.end()

        # Remove matches that are part of goodword
        for slur in self.slurs:
            if slur.slur not in slurs or not slur.goodwords:
                continue
            pos = 0
            while match := slur.goodword_regex.search(__value, pos):
                slurs[slur.slur] = [
                    slur_match
                    for slur_match in slurs[slur.slur]
                    if not (
                        match.start() <= slur_match.start()
                        and match.end() >= slur_match.end()
                    )
                ]
                pos = match.end()

        return {slur: matches for slur, matches in slurs.items() if matches}

    def __contains__(self, __value: str) -> bool:
        return self.regex.search(__value) is not None

    def __iter__(self):
        return iter(self.slurs)
