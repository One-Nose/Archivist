"""The root file of the program"""
from json import load

from src.archive import Archive

if __name__ == '__main__':
    with open('config.json', encoding='utf-8') as file:
        config = load(file)

    archive = Archive(config)
    archive.reset()

    period = archive.new_element_type('Period')
    period.new_property('Beginning')
    period.new_property('End')

    event = archive.new_element_type('Event')
    event.new_property('Date')

    during = event.new_relation_type('During %%', period)

    episode4 = archive.new_document('Star Wars Episode IV: A New Hope')

    civil_war = episode4.declare(period)
    civil_war.add_title('Civil War')

    rebel_victory = episode4.declare(event)
    rebel_victory.add_relation(during, civil_war)

    archive.commit()
    archive.close()
