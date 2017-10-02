import sys
import re


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
\t\t\t\tthat should be excluded from the solution path.''')
    print('''\theuristic [1, 2]:\tWhich heuristic to use when searching.''' +
          ''' 1 - Straight line distance. 2 - Fewest links.''')
    print('''\toutput [1, 2]:\t\tWhich type of output to provide.''' +
          ''' 1 - Optimal path only. 2 - Step-by-step''')


def print_map(_map):
    '''Print a map'''
    for key, value in _map.items():
        print(key + ' -> ', end='')
        print([city['name'] for city in value['connections']])


def distance_heuristic(start, end):
    '''Calculate the score for start given end based on straight-line distance'''
    return (float(start['x']) - float(end['x']))**2 + (float(start['y']) - float(end['y']))**2


def links_heuristic(cities, start, end):
    '''Calculate the score for start given end and the full map cities
    based on how many links start is away from end in the map'''
    return 0.0


def a_star(cities, start, end, heuristic):
    '''Perform a recursive A* search using the map defined by cities (adjacency list)
    cities {dict<str, dict>} - The map of cities as (city_name, city_data) pairs
    start {str} - The name of the city to start at
    end {str} - The name of the city to end at
    heuristic {int} - [1 || 2] The heuristic to use. 1 is distance, 2 is links
    returns path {city[]} - A list of cities that make up the path taken'''

    # TODO: still backtracking to visited cities for start
    visited = set(start)

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
            path[-1]['name'], possible_moves.keys()))

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
                cities[name_match.group(1)] = {'name': name_match.group(
                    1), 'x': name_match.group(2), 'y': name_match.group(3), 'connections': []}

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
                # TODO: instead of storing city names in connections, store references to objects
                cities[source_city]['connections'].append(
                    cities[city_names[i]])
                road_count += 1
        print('Finished loading map. Found {0} cities and {1} roads. '
              'Filtering out excluded cities...'.format(
                  len(cities), road_count))

    # get list of excluded cities
    excluded_cities = args[4].split(',')
    # filter out all excluded cities
    cities = {name: city for name,
              city in cities.items() if name not in excluded_cities}
    # remove all invalid roads
    for city in cities.values():
        city['connections'] = [
            road for road in city['connections'] if road['name'] in cities]

    print('Done filtering cities. Remaining {0} cities.'.format(len(cities)))

    print('Map:')
    print_map(cities)

    a_star(cities, args[2], args[3], args[5])


if __name__ == '__main__':
    if len(sys.argv) != 8:
        print_usage()
    else:
        main(sys.argv[1:])
