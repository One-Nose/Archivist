"""The root file of the program"""
from json import load

from src.archive import Archive

if __name__ == '__main__':
    with open('config.json', encoding='utf-8') as file:
        config = load(file)

    archive = Archive(config)
