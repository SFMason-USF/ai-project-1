import sys
import re

def print_usage():
    '''Print how to use the function.'''
    print('Usage:')
    print('python ai-project-1.py connections_file locations_file start_city end_city excluded_cities heuristic output')
    print(
'''\tconnections_file:\tThe path to the file containing the connections between cities.
\t\t\t\tThis file should contain a list of each city, followed by the number of 
\t\t\t\toutbound connections it contains, followed by its connections to other cities.
\t\t\t\te.g. The line for city A3, which is connected to cities B2, D6, and F1 would be:
\t\t\t\t\tA3 3 B2 D6 F1''')
    print(
'''\tlocations_file:\t\tThe path to the file containing the locations and names of cities.
\t\t\t\tThis file should contain a list of each city name,
\t\t\t\tfollowed by the city's x and y coordinates.
\t\t\t\te.g. The line for city A3 at (43, 112) would be:
\t\t\t\t\tA3 43 112''')
    print(
'''\tstart_city:\t\tThe name of the city (as listed in locations_file) to start at.''')
    print(
'''\tend_city:\t\tThe name of the city (as listed in locations_file) to end at.''')
    print(
'''\texcluded_cities:\tA comma-separated list of city names (as listed in locations_file)
\t\t\t\tthat should be excluded from the solution path.''')
    print(
'''\theuristic [1, 2]:\tWhich heuristic to use when searching. 1 - Straight line distance. 2 - Fewest links.''')
    print(
'''\toutput [1, 2]:\t\tWhich type of output to provide. 1 - Optimal path only. 2 - Step-by-step''')


def main(args):
    city_name_regex = re.compile(r'''[A-Z]\d{1,3}[a-z]?''')

    cities = {}
    connections = None
    locations = None

    with open(args[1], 'r') as locations_file:
        for line in locations_file:
            name_match = city_name_regex.search(line)
            if name_match:
                cities[name_match.group(0)] = {'name': name_match.group(0), 'x': -1, 'y': -1, 'connections': []}
    
    with open(args[0], 'r') as connections_file:
        source_city_regex = re.compile(r'({0}) (\d+) '.format(city_name_regex.pattern))
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
                cities[source_city]['connections'].append(city_names[i]) #TODO: instead of storing city names in connections, store references to objects

        print(cities)

if __name__ == '__main__':
    if len(sys.argv) != 8:
        print_usage()
    else:
        main(sys.argv[1:])