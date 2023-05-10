"""The root file of the program"""
from json import load

from src.archive import Archive

if __name__ == '__main__':
    with open('config.json', encoding='utf-8') as file:
        config = load(file)

    archive = Archive(config)
    archive.reset()

    period = archive.new_category('Period')
    beginning = period.new_property('Beginning')
    end = period.new_property('End')
    archive.add_order_rule(end, beginning)

    episode4 = archive.new_document('Star Wars Episode IV: A New Hope')

    civil_war = archive.new_element(period)
    episode4.declare_description(civil_war, 'It is a period of civil war.')

    rebel_victory = archive.new_element(period)
    episode4.declare_description(
        rebel_victory,
        'Rebel spaceships, striking from a hidden base, have won their first'
        ' victory against the evil Galactic Empire.',
    )

    episode4.declare_order(archive.point(4), archive.point(1))
    episode4.declare_order(archive.point(2), archive.point(5))

    archive.analyze()

    archive.commit()
    archive.close()
