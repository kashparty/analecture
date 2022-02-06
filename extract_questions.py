from datetime import datetime, time
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from os import environ
import django

environ.setdefault("DJANGO_SETTINGS_MODULE", "seapan.settings")
django.setup()
from seapanapp.models import QuestionAnswer, Recording

MIN_QUESTION_LENGTH = 3
nltk.download("punkt")


def parse_timestamp(timestamp_str):
    time_parts = timestamp_str.split(":")
    if len(time_parts) == 2:
        return time(0, int(time_parts[0]), int(time_parts[1]))
    elif len(time_parts) == 3:
        return time(int(time_parts[0]), int(time_parts[1]), int(time_parts[2]))
    else:
        raise RuntimeError("Timestamp must have 2 or 3 parts")


def load_phrases(filename):
    phrases = []
    with open(filename, "r") as f:
        lines = f.read().splitlines()
        metadata = lines[:5]
        lecture_id = metadata[0].split(": ")[1]
        lecture_title = metadata[1].split(": ", 1)[1]
        recording = Recording(panopto_id=lecture_id, name=lecture_title)
        recording.save()

        lecture_category = metadata[2].split(": ", 1)[1]
        lecturer = metadata[3].split(": ")[1]
        lecture_date = datetime.strptime(metadata[4].split(": ")[1], "%d/%m/%y")

        for i in range(5, len(lines), 2):
            timestamp = parse_timestamp(lines[i + 1])
            phrase_texts = sent_tokenize(lines[i])
            phrases += [
                Phrase(
                    timestamp,
                    text,
                    recording,
                    lecture_category,
                    lecturer,
                    lecture_date,
                )
                for text in phrase_texts
            ]

    return phrases


class Phrase:
    def __init__(
        self,
        timestamp,
        text,
        recording,
        lecture_category,
        lecturer,
        lecture_date,
    ):
        self.timestamp = timestamp
        self.text = text
        self.recording = recording
        self.lecture_category = lecture_category
        self.lecturer = lecturer
        self.lecture_date = lecture_date

    def __str__(self):
        return f"{self.recording.panopto_id}@{self.timestamp}: {self.text}"

    def is_question(self):
        words = word_tokenize(self.text)
        return self.text.endswith("?") and len(words) >= MIN_QUESTION_LENGTH

    def save(self):
        question_answer = QuestionAnswer(
            question=self.text,
            answer=self.text,
            timestamp=self.timestamp,
            recording=self.recording,
        )
        question_answer.save()


phrases = load_phrases("be689587-31aa-4495-9acc-ae3100d7e8aa.txt")
questions = [phrase for phrase in phrases if phrase.is_question()]

for question in questions:
    question.save()