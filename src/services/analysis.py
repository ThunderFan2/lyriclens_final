from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict
import re, random

import pronouncing
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

_analyzer = SentimentIntensityAnalyzer()
_WORD_RE = re.compile(r"[A-Za-z']+")


@dataclass
class AnalysisResult:
    lines: List[str]
    rhyme_scheme: str
    tone: str


def _last_stressed_vowel_phoneme(word: str) -> str:
    phones = pronouncing.phones_for_word(word.lower())
    if not phones:
        return word.lower()[-2:]
    return pronouncing.rhyming_part(phones[0]) or word.lower()[-2:]


def _line_end_token(line: str) -> str:
    tokens = _WORD_RE.findall(line)
    return tokens[-1].lower() if tokens else ""


def detect_tone(text: str) -> str:
    s = _analyzer.polarity_scores(text or "")["compound"]
    if s >= 0.3:
        return "uplifting"
    if s <= -0.3:
        return "melancholic"
    return "confident"


def detect_rhyme_scheme(lines: List[str]) -> str:
    ends = [_line_end_token(l) for l in lines if l.strip()]
    keys = [_last_stressed_vowel_phoneme(w) for w in ends]
    if len(keys) >= 4:
        a, b, c, d = keys[:4]
        if a == c and b == d and a != b:
            return "ABAB"
        if a == b and c == d and a != c:
            return "AABB"
        if a == d and b == c and a != b:
            return "ABBA"
    return "FREE"


def analyze(text: str) -> AnalysisResult:
    if not text:
        return AnalysisResult(lines=[], rhyme_scheme="FREE", tone="confident")
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    rhyme = detect_rhyme_scheme(lines)
    tone = detect_tone(text)
    return AnalysisResult(lines=lines, rhyme_scheme=rhyme, tone=tone)


_TEMPLATES = {
    "uplifting": [
        [
            "Lift up the chorus, let troubles unwind,",
            "paper-thin shadows fall out of the frame,",
            "Bright city rhythm keeps time in your mind,",
            "walk through the rain and remember your name.",
        ],
        [
            "Morning will open the blinds on your doubt,",
            "traffic will hum like a soft saxophone,",
            "you'll turn the volume of courage back out,",
            "finding the skyline is already home.",
        ],
    ],
    "melancholic": [
        [
            "Echoes on hallway tiles keep time,",
            "neon is humming a faded refrain,",
            "Letters you folded won’t quite rhyme,",
            "lonely umbrellas confess to the rain.",
        ],
        [
            "Windows breathe fog while the streetlights align,",
            "coffee cups shiver in puddles of gold,",
            "yesterday’s playlist replays every line,",
            "telling a story that’s already told.",
        ],
    ],
    "confident": [
        [
            "Hands on the groove and the city aligns,",
            "faces like mirrors reflect what you send,",
            "Beat after beat you redraw the lines,",
            "verse after verse you decide how they end.",
        ],
        [
            "Bass in your chest like a well-tuned machine,",
            "pavement becomes your own personal stage,",
            "you've learned to remix every awkward scene,",
            "dropping the doubt and then raising the gauge.",
        ],
    ],
}


def rewrite(text: str) -> Dict:
    analysis = analyze(text)
    tone = analysis.tone
    templates = _TEMPLATES.get(tone, _TEMPLATES["confident"])
    stanza = random.choice(templates)
    return {
        "analysis": {
            "detected_scheme": analysis.rhyme_scheme,
            "tone": analysis.tone,
            "line_count": len(analysis.lines),
        },
        "rewrite": stanza,
        "chosen_scheme": "ABAB",
        "source": "local-lite (no syllables)",
    }
