import sys


def fprint(text_type, text, newline=True):
    print(f'[{text_type}] {text}',end=("\n" if newline else ""))


def null(*args, **kwargs):
    pass
