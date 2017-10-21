import sys
import re
from math import sqrt
import time


class Stopwatch():
    '''Provides a simple stopwatch for measuring timing'''

    def __init__(self):
        self.__counter = 0.0
        self.__started = None

    def start(self):
        'Start timing'
        self.__counter = 0.0
        self.__started = time.time()

    def stop(self):
        'Stop timing and record counter'
        if self.__started is None:
            return
        self.__counter += time.time() - self.__started
        self.__started = None

    def reset(self):
        'Stop timing and reset counter time'
        self.stop()
        self.__counter = 0.0

    def elapsed(self):
        'Get the time elapsed. Returns None if Stopwatch is running'
        return self.__counter if self.__started is None else None


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


def a_star(start, end, use_distance=True, verbose=False):
    '''Perform an A* search using the start and end nodes of an adjacency list
    start {City} -          The name of the city to start at
    end {City} -            The name of the city to end at
    use_distance {bool} -   Whether to use euclidean distance to determine how closes
                            a city is from the end. If false, assumes all cities are
                            equal distance to the end (i.e. fewest links heuristic)
    verbose {bool} -        If True, the algorithm will provide step-by-step output
                            and wait for user input before proceeding
    returns path {City[]} - A list of cities that make up the path taken'''

    if verbose:
        print('\nStarting search beginning with city {0}'.format(start.name))

    if start == end:
        if verbose:
            print('Start City is the same as end!')
        return [start]

    visited = set() #previously visited cities by name

    frontier = [start] #potential paths to take

    previously = {} #records the previously visited city for each city, so the path can be reconstructed
    previously[start.name] = None

    distance_from_start = {} #best score for each city during the search, to allow accumulation of distance traveled
    distance_from_start[start.name] = 0.0

    def heuristic(city):
        '''Return the heuristic score for a city.'''
        if use_distance:
            return float(distance_from_start[city.name] + sqrt(city.distance_to(end)))
        return distance_from_start[city.name] + 1 #assume every city is 1 link away from the end

    while frontier:
        # sort the frontier so that the closest node to the end is in the back
        frontier.sort(key=heuristic, reverse=True)

        if verbose and frontier[-1].name in previously and previously[frontier[-1].name]:
            print('\nCurrently at city {0}. Possible paths are:'.format(previously[
                frontier[-1].name].name))
            for city in frontier:
                print('{0}\t(Path would be at least {1} units long.)'.format(
                    city.name, int(heuristic(city))))
            print()

        current_city = frontier.pop()
        visited.add(current_city.name)

        if verbose:
            print('The best path to take now is {0}'.format(current_city.name))
            input('Press enter to take this path...')

        if current_city == end:
            if verbose:
                input('End city found! Path was {0} units long.\nPress enter to exit search...'.format(
                    int(distance_from_start[current_city.name])))
            #reconstruct the path we took
            path = [current_city]
            previous = previously[current_city.name]
            while previous is not None: #walk back to the start
                path.append(previous)
                previous = previously[previous.name]
            path.reverse() #path was backwards
            return path

        for city in current_city.connections:
            if city.name in visited:
                continue
            if city not in frontier: #avoid duplicating paths
                frontier.append(city)
            distance_traveled = distance_from_start[current_city.name] + \
                (sqrt(current_city.distance_to(city)) if use_distance else 1)

            #if we've never been here or this path is better than the path we;ve already found for city
            if city.name not in distance_from_start or \
                    distance_traveled < distance_from_start[city.name]:
                distance_from_start[city.name] = distance_traveled
                previously[city.name] = current_city

    if verbose:
        input('No more valid paths found. ' +
              'There must not be a way to get to the end from start.\n' +
              'Press enter to continue...')

    return []


def main(args):
    '''Program entry point'''

    if args[5] not in '12' and args[6] not in '12':
        print_usage()
        return 1

    city_name_pattern = r'''(?P<city_name>\w+)'''
    locations_regex = re.compile(
        r'^' + city_name_pattern + r''' +(?P<x>\d+) +(?P<y>\d+)''')
    connections_regex = re.compile(
        r'^' + city_name_pattern + r''' +(?P<connections_count>\d+) +''')

    cities = {}

    print('Loading map...')

    # load cities
    with open(args[1].strip('''"' '''), 'r') as locations_file:
        line_num = 0 #to track parsing errors/malformed input
        for line in locations_file:
            line_num += 1
            if not line.strip():  # skip empty lines
                continue
            match = locations_regex.match(line.strip())
            if match:
                cities[match.group('city_name')] = City(match.group(
                    'city_name'), match.group('x'), match.group('y'), [])
            else:
                print('Parsing error on line ' + str(line_num) +
                      ' in file ' + locations_file.name)
                print('', bytes(line.strip(), 'utf-8'))

    # load roads
    with open(args[0].strip('''"' '''), 'r') as connections_file:
        road_count = 0 #total number of roads
        line_num = 0 #to track parsing errors/malformed input
        for line in connections_file:
            line_num += 1
            if not line.strip():
                continue
            match = connections_regex.match(line.strip())
            if not match:
                print('Parsing error on line ' + str(line_num) +
                      ' in file ' + connections_file.name)
                print('', bytes(line.strip(), 'utf-8'))
                break
            source_city = match.group('city_name')
            connections_count = int(match.group('connections_count'))
            city_names = re.findall(city_name_pattern, line)
            # skip the first two matches, which are the source city and connections count
            for name in city_names[2:]:
                if name not in cities:
                    print('''Error: invalid road ('{1}') given for City {0}. Exiting...'''.format(
                        source_city, name))
                    return 1
                cities[source_city].connections.append(
                    cities[name])
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

    if str(args[2]) not in cities:
        print(
            'Error: No city exists with name "{0}". Exiting...'.format(args[2]))
        return 1
    start = cities[args[2]]
    if str(args[3]) not in cities:
        print(
            'Error: No city exists with name "{0}". Exiting...'.format(args[3]))
        return 1
    end = cities[args[3]]

    print('Starting A* search...')

    timer = Stopwatch()
    timer.start()
    path = a_star(start, end, args[5] == '1', args[6] == '2')
    timer.stop()
    print('Algorithm took {0:.3f} seconds'.format(timer.elapsed()))

    print('Path:')
    print([city.name for city in path])

    return 0


if __name__ == '__main__':
    if len(sys.argv) != 8:
        print_usage()
    else:
        try:
            main(sys.argv[1:])
            input('Done. Press enter to continue...')
        except KeyboardInterrupt:
            print('\nProgram terminated by user. Exiting...')
