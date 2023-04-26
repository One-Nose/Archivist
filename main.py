"""The root file of the program"""
from json import load

from src.archive import Archive

if __name__ == '__main__':
    with open('config.json', encoding='utf-8') as file:
        config = load(file)

    archive = Archive(config)
    archive.reset()

    period = archive.new_element_type('Period')
    period.add_property('Beginning')
    period.add_property('End')

    episode4 = archive.new_document('Star Wars Episode IV: A New Hope')
    episode4.declare(period)

    archive.commit()
    archive.close()
