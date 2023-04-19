"""The root file of the program"""
from json import load

from src.archive import Archive

# from server import start_server

if __name__ == '__main__':
    with open('config.json', encoding='utf-8') as file:
        config = load(file)

    archive = Archive(config)
    archive.new_document('doc')
    archive.commit()

    # start_server()
