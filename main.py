"""The root file of the program"""
from json import load

from src.archive import Archive, BuiltInCategory

if __name__ == '__main__':
    with open('config.json', encoding='utf-8') as file:
        config = load(file)

    archive = Archive(config)
    archive.reset()

    period = archive.new_category('Period')
    beginning = period.new_property('Beginning')
    end = period.new_property('End')
    archive.add_rule(BuiltInCategory.GREATER, end, beginning)

    event = archive.new_category('Event')
    date = event.new_property('Date')

    during = archive.new_category('During')
    during_event = during.new_property('Event', event)
    during_period = during.new_property('Period', period)
    archive.add_rule(
        BuiltInCategory.GREATER, (during_event, date), (during_period, beginning)
    )
    archive.add_rule(BuiltInCategory.LESS, (during_event, date), (during_period, end))

    episode4 = archive.new_document('Star Wars Episode IV: A New Hope')

    civil_war = episode4.declare(period)
    civil_war.add_description('It is a period of civil war.')

    rebel_victory = episode4.declare(event)
    rebel_victory.add_description(
        'Rebel spaceships, striking from a hidden base, have won their first'
        ' victory against the evil Galactic Empire.'
    )

    rebel_victory_during = episode4.declare(during)
    rebel_victory_during.declare_property(during_event, rebel_victory)
    rebel_victory_during.declare_property(during_period, civil_war)

    archive.commit()
    archive.close()
