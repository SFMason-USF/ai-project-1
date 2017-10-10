import sys
import re
from math import sqrt
import heapq
from collections import deque


# TODO: change distance heuristic to total distance traveled since start
# TODO: implement links heuristic search


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


def print_usage():
    '''Print how to use the function.'''
    print('Usage:')
    print('python ai-project-1.py connections_file locations_file' +
          ' start_city end_city excluded_cities heuristic output')
    print('''\tconnections_file:\tThe path to the file containing the connections between cities.
\t\t\t\tThis file should contain a list of each city, followed by the number of
\t\t\t\toutbound connections it contains, followed by its connections to other cities.
\t\t\t\te.g. The line for city A3, which is connected to cities B2, D6, and F1 would be:
\t\t\t\t\tA3 3 B2 D6 F1''')
    print('''\tlocations_file:\t\tThe path to the file containing the locations and names of cities.
\t\t\t\tThis file should contain a list of each city name,
\t\t\t\tfollowed by the city's x and y coordinates.
\t\t\t\te.g. The line for city A3 at (43, 112) would be:
\t\t\t\t\tA3 43 112''')
    print('''\tstart_city:\t\tThe name of the city (as listed in locations_file) to start at.''')
    print('''\tend_city:\t\tThe name of the city (as listed in locations_file) to end at.''')
    print('''\texcluded_cities:\tA comma-separated list of city names (as listed in locations_file)
\t\t\t\tthat should be excluded from the solution path. Enter any invalid name to exclude no cities.''')
    print('''\theuristic [1, 2]:\tWhich heuristic to use when searching.''' +
          ''' 1 - Straight line distance. 2 - Fewest links.''')
    print('''\toutput [1, 2]:\t\tWhich type of output to provide.''' +
          ''' 1 - Optimal path only. 2 - Step-by-step''')


def print_map_dicts(_map):
    '''Print a map'''
    for key, value in _map.items():
        print(key + ' -> ', end='')
        print([city['name'] for city in value['connections']])


def a_star_distance(cities, start, end, verbose=False):
    '''Perform a recursive A* search using the map defined by cities (adjacency list)
    start {City} -          The name of the city to start at
    end {City} -            The name of the city to end at
    verbose {bool} -        If True, the algorithm will provide step-by-step output
                            and wait for user input before proceeding
    returns path {City[]} - A list of cities that make up the path taken'''

    if verbose:
        print('\nStarting search from city {0}'.format(start.name))

    if start == end:
        if verbose:
            print('Start City is the same as end!')
        return [start]

    visited = set()
    visited.add(start.name)

    previously = {
        start.name: None
    }

    distance_traveled = {
        start.name: 0.0
    }

    frontier = start.connections[:]
    for city in frontier:
        previously[city.name] = start
        distance_traveled[city.name] = sqrt(city.distance_to(start))

    while frontier:
        if verbose:
            print()

        # sort descending by distance to end city
        # so that the last element will be the closest to end
        frontier.sort(key=lambda city: city.distance_to(end), reverse=True)

        if verbose:
            print('At city {0}'.format(previously[frontier[-1].name]))
            print('Currently, there are {0} potential paths. These are:'.format(
                len(frontier)))
            for city in frontier:
                print('{0} ({1} units away from end goal)'.format(
                    city.name, int(sqrt(city.distance_to(end)))))

        current_city = frontier.pop()
        visited.add(current_city.name)

        if verbose:
            print('The best path to take now is {0}'.format(current_city.name))
            input('Press enter to take this path...')

        if current_city == end:
            if verbose:
                input('End city found! Press enter to exit search...')
            path = [current_city]
            previous = previously[current_city.name]
            while previous is not None:
                path.append(previous)
                previous = previously[previous.name]
            path.reverse()
            return path

        for city in current_city.connections:
            # skip cities that have been visited
            if city.name in visited:
                continue
            previously[city.name] = current_city
            frontier.append(city)

    if verbose:
        input('No more valid paths found. ' +
              'There must not be a way to get to the end from start.\n' +
              'Press enter to continue...')
    return []


def a_star_links(cities, start, end, verbose=False):
    '''Perform a recursive A* search using the map defined by cities (adjacency list)
    cities {dict<str, dict>} - The map of cities as (city_name, city_data) pairs
    start {str} - The name of the city to start at
    end {str} - The name of the city to end at
    heuristic {int} - [1 || 2] The heuristic to use. 1 is distance, 2 is links
    returns path {city[]} - A list of cities that make up the path taken'''

    # TODO: still backtracking to visited cities for start
    visited = set()
    visited.add(start)

    path = [cities[start]]
    if end == start:
        return path

    while True:
        possible_moves = {city['name']: (distance_heuristic(cities[start], city)
                                         if heuristic == 1
                                         else links_heuristic(cities, cities[start], city))
                          for city in cities[path[-1]['name']]['connections']
                          if city['name'] not in visited}

        print('At City {0}. Possible moves are: {1}'.format(
            path[-1]['name'], list(possible_moves.keys())))

        if not possible_moves:
            if not path or path[-1] == cities[start]:
                print('No valid path found.')
                return path
            path = path[:-1]
            continue
        if cities[end]['name'] in possible_moves:
            path.append(cities[end])
            return path
        best_move = min(possible_moves, key=lambda x: possible_moves[x])
        visited.add(best_move)
        path.append(cities[best_move])


def main(args):
    '''Program entry point'''
    city_name_regex = re.compile(r'''([A-Z]\d{1,3}[a-z]?)''')

    cities = {}

    print('Loading map...')

    # load cities
    with open(args[1], 'r') as locations_file:
        city_regex = re.compile(city_name_regex.pattern + r' (\d+) (\d+)')
        for line in locations_file:
            name_match = city_regex.search(line)
            if name_match:
                # cities[name_match.group(1)] = {'name': name_match.group(
                #     1), 'x': name_match.group(2), 'y': name_match.group(3), 'connections': []}
                cities[name_match.group(1)] = City(
                    name=name_match.group(1),
                    x=name_match.group(2),
                    y=name_match.group(3))

    # load roads
    with open(args[0], 'r') as connections_file:
        road_count = 0
        source_city_regex = re.compile(city_name_regex.pattern + r' (\d+)')
        for line in connections_file:
            source_city_match = source_city_regex.search(line)
            if not source_city_match:
                break
            source_city = source_city_match.group(1)
            connections_count_match = source_city_regex.search(line)
            if not connections_count_match:
                break
            connections_count = int(connections_count_match.group(2))
            city_names = city_name_regex.findall(line)
            for i in range(1, connections_count + 1):
                if city_names[i] not in cities:
                    print('Error: invalid road given for City {0}. Exiting...'.format(
                        source_city))
                    return 1
                cities[source_city].connections.append(
                    cities[city_names[i]])
                road_count += 1
        print('Finished loading map. Found {0} cities and {1} roads. '
              'Filtering out excluded cities...'.format(
                  len(cities), road_count))

    # get list of excluded cities
    excluded_cities = [city_name.strip('" ')
                       for city_name in args[4].split(',') if city_name in cities]
    # filter out all excluded cities
    cities = {name: city for name,
              city in cities.items() if name not in excluded_cities}
    # remove all invalid roads
    for city in cities.values():
        city.connections = [
            road for road in city.connections if road.name in cities]

    print('Done filtering cities. Remaining {0} cities.'.format(len(cities)))

    # print('Map:')
    # for city in sorted(cities.values(), key=lambda x: x.name):
    #    print(city)
    # print_map_dicts(cities)

    # a_star(cities, args[2], args[3], args[5])
    if args[2] not in cities:
        print(
            'Error: "{0}" is not a valid city name. Exiting...'.format(args[2]))
        return 1
    start = cities[args[2]]
    if args[3] not in cities:
        print(
            'Error: "{0}" is not a valid city name. Exiting...'.format(args[3]))
        return 1
    end = cities[args[3]]
    if args[5] == '1':
        print([city.name for city in a_star_distance(cities, start, end, True)])
    elif args[5] == '2':
        print(a_star_links(cities, start, end, True))
    else:
        print_usage()

    return 0


if __name__ == '__main__':
    if len(sys.argv) != 8:
        print_usage()
    else:
        try:
            main(sys.argv[1:])
        except KeyboardInterrupt:
            print('\nProgram terminated by user. Exiting...')
