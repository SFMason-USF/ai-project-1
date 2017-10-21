import sys
import random

class City():
    '''Represents a node with an integer x,y position and a list of other City
    objects that can be reached from this City'''

    def __init__(self, name, x, y, connections=None):
        self.name = str(name)
        self.x = int(x)
        self.y = int(y)
        try:
            self.connections = list(connections)
        except TypeError:
            self.connections = []

    def __str__(self):
        return '''City {:<80}\n ({:>3}, {:>3}) -> {}'''.format(
            "'{}'".format(self.name),
            str(self.x),
            str(self.y),
            [city.name for city in self.connections])

    def distance_to(self, city):
        '''Get the cartesian distance (squared) between this City and city as a float'''
        return (float(self.x) - float(city.x))**2 + (float(self.y) - float(city.y))**2
    

def make_cities(count, connections_average, connections_deviation):
    '''Generate a map of cities.
{int} count - The number of cities to generate
{int} connections_average - The average number of cities that a city has roads leading to
{int} connections_deviation - The maximum deviation from the average number of roads
returns: {dict} - A map of city names->City()'''

    cities = {}
    
    for i in range(0, count, 1):
        name = '{0:x}'.format(i)
        cities[name] = City(name, -1, -1, [])

    x = 0
    y = 0
    step = 800 / count
    city_names = list(cities.keys())
    random.shuffle(city_names)
    for name in city_names:
        cities[name].x = int(x)
        cities[name].y = int(y)
        x += step
        y += int((step * 4.31)**3)
        y %= 800

    for name in cities:
        connections = min(max(random.randint(connections_average - connections_deviation, connections_average + connections_deviation), 0), count - 1)
        random.shuffle(city_names)
        cities[name].connections = [cities[city_name] for city_name in city_names if city_name != name][:connections]

    return cities


def write_locations(cities, filename='locations.txt'):
    with open(filename, 'w+') as file:
        for name, city in cities.items():
            file.write('{} {} {}\r\n'.format(name, city.x, city.y))


def write_connections(cities, filename='connections.txt'):
    with open(filename, 'w+') as file:
        for name, city in cities.items():
            line = '{} {} '.format(name, len(city.connections))
            for connection in city.connections:
                line += '{} '.format(connection.name)
            line.strip()
            line += '\r\n'
            file.write(line)


def main(args):
    '''Program entry point'''
    cities = make_cities(1000, 100, 90)
    write_connections(cities, 'connections_long.txt')
    write_locations(cities, 'locations_long.txt')

if __name__ == '__main__':
    main(sys.argv[1:])
    print('Done.')
