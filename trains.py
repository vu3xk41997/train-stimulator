# import
import random
import sys
# import numpy
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra


# station class
class Station:
    def __init__(self, name, delay, line, northStation=None, southStation=None):
        '''
        params: name(str), delay(float), line(str), northStation(str), southStation(str)

        object structure: {'name' (str): name,
                           'delay' (float): delay,
                           'line' (dict): {
                                line: {
                                    'northStation': northStation,
                                    'southStation': southStation
                                }
                            }
                           }
        '''
        self.name = name
        self.delay = delay
        self.line = {line: {'northStation': northStation, 'southStation': southStation}}       

    def addLine(self, line, northStation=None, southStation=None):
        '''
        params: line(str), northStation(str), southStation(str)

        if a station is a connect point for two line, add new line, northStation, southStation for the station
        object structure after addLine: {'name' (str): name,
                                         'delay' (float): delay,
                                         'line' (dict): {
                                            line: {
                                                'northStation': northStation,
                                                'southStation': southStation
                                            },
                                            line: {
                                                'northStation': northStation,
                                                'southStation': southStation
                                            }
                                         }
                                        }
        '''
        self.line[line] = {'northStation': northStation, 'southStation': southStation}

# C = Station("C", 0.02, "Green", None, 'D')
# print(C.__dict__)
# color = "Green"
# C.line[color]['northStation'] = 'B'
# print(C.__dict__)
# line = "green"
# C.line = {line: {'northStation': 'X', 'southStation': 'Y'}}
# print(C.__dict__)

# train class
class Train:
    def __init__(self, id, position, line, direction, delayed=False):
        '''
        params: id(int), position(str), line(str), direction(str), delayed(bool)
        '''
        self.id = id
        self.position = position        # Randomly select between stations
        self.line = line                # Decided by position, if position has more than one line, randomly select which line it is
        self.direction = direction      # Randomly select between North or South 
        self.delayed = delayed          # Randomly decide delayed or not based on current position's delay time


# functions
def readStation(filename):
    '''
    params: filename(str)
    returns: dictionary {station_name(key): delay_probability(value)}

    raise FileNotFoundError if filename doesn't exist
    '''
    if filename:
        stations_dict = {}
        station_data = open(filename, 'r')
        seperate_stations = station_data.read().strip().split('\n')
        for station in seperate_stations:
            try:
                station_name, delay_probability = station.strip().split(',')
                stations_dict[station_name] = float(delay_probability)
            except ValueError:
                print(f"Warning: wrong input format for entry: {station}\n")
                pass
        return stations_dict
    else:
        raise FileNotFoundError
    
def readConnection(filename):
    '''
    params: filename(str)
    returns: list of lists [[start_station, end_station, line, direction]]

    raise FileNotFoundError if filename doesn't exist
    '''
    if filename:
        connections_list = []
        connection_data = open(filename, 'r')
        seperate_connections = connection_data.read().strip().split('\n')
        for connection in seperate_connections:
            try:
                start_station, end_station, line, direction = connection.strip().split(',')
                connections_list.append([start_station, end_station, line, direction])
            except ValueError:
                print(f"Warning: wrong input format for entry: {connection}\n")
                pass
        return connections_list
    else:
        raise FileNotFoundError
    

def buildStations(station_data, connection_data):
    '''
    params: station_data(dict), connection_data(list)
    returns: list of objects and length of list should be the same as the length of data from stationFile
    '''
    # function logic:
    # split connection data into lines 
    # loop through each unique lines and find connections on that line
    # each line contains stations on the line and line color, relations between two station
    # get unique stations in the line, loop through each station and find current station's connections
    # if current station is not yet created in other line, then create new station, otherwise add new line to current station
    # loop through each connection current station has
    # if current station is not yet created in current line, then create new station, otherwise update north and south station value
    
    stations = []
    created_stations = []

    # find unique line values
    lines = []
    for i in range(len(connection_data)):
        lines.append(connection_data[i][2])
    unique_lines = list(set(lines))

    for line in unique_lines:
        created_stations_on_line = []
        stations_on_line = []
        connections_on_line = [connection for connection in connection_data if line in connection[2]]    # all connections on current line
        for i in range(len(connections_on_line)):
            stations_on_line.append(connections_on_line[i][0])
            stations_on_line.append(connections_on_line[i][1])
        unique_stations_on_line = list(set(stations_on_line))    # get unique stations on current line
        for station in unique_stations_on_line:
            station_connection = [matched for matched in connections_on_line if station in matched]    # find current station's connections
            if station not in created_stations:    # if station is not yet created in other line
                for i in range(len(station_connection)):    # loop through each connection current station has 
                    if station not in created_stations_on_line:    # if station is not yet created
                        if station_connection[i][0] == station:    # if station is first element on current connection
                            if station_connection[i][3].lower() == 's':    # if direction is south
                                currentStation, southStation, lineColor, direction = station_connection[i]
                                stations.append(Station(currentStation, station_data[currentStation], lineColor, None, southStation))
                                created_stations.append(station)    # shows current station is created and appended to final list of objects
                                created_stations_on_line.append(currentStation)    # shows current station is created in current line
                            elif station_connection[i][3].lower() == 'n':    # if connection is north
                                currentStation, northStation, lineColor, direction = station_connection[i]
                                stations.append(Station(currentStation, station_data[currentStation], lineColor, northStation, None))
                                created_stations.append(station)
                                created_stations_on_line.append(currentStation)
                            else:
                                raise ValueError    # direction value is neither 's' nor 'n'
                        elif station_connection[i][1] == station:    # if station is second element on current connection
                            if station_connection[i][3].lower() == 's':
                                northStation, currentStation, lineColor, direction = station_connection[i]
                                stations.append(Station(currentStation, station_data[currentStation], lineColor, northStation, None))
                                created_stations.append(station)
                                created_stations_on_line.append(currentStation)
                            elif station_connection[i][3].lower() == 'n':
                                southStation, currentStation, lineColor, direction = station_connection[i]
                                stations.append(Station(currentStation, station_data[currentStation], lineColor, None, southStation))
                                created_stations.append(station)
                                created_stations_on_line.append(currentStation)
                            else:
                                raise ValueError
                    else:    # if station is already created, update north and south stations
                        if station_connection[i][0] == station:
                            if station_connection[i][3].lower() == 's':
                                currentStation, southStation, lineColor, direction = station_connection[i]
                                targetStation = next(targetStation for targetStation in stations if targetStation.name == station)    # find target station from list of station objects
                                targetStation.line[lineColor]['southStation'] = southStation    # update current line's south station
                                created_stations_on_line.append(currentStation)
                            elif station_connection[i][3].lower() == 'n':
                                currentStation, northStation, lineColor, direction = station_connection[i]
                                targetStation = next(targetStation for targetStation in stations if targetStation.name == station)
                                targetStation.line[lineColor]['northStation'] = northStation    # update current line's north station
                                created_stations_on_line.append(currentStation)
                            else:
                                raise ValueError
                        elif station_connection[i][1] == station:
                            if station_connection[i][3].lower() == 's':
                                northStation, currentStation, lineColor, direction = station_connection[i]
                                targetStation = next(targetStation for targetStation in stations if targetStation.name == station)
                                targetStation.line[lineColor]['northStation'] = northStation
                                created_stations_on_line.append(currentStation)
                            elif station_connection[i][3].lower() == 'n':
                                southStation, currentStation, lineColor, direction = station_connection[i]
                                targetStation = next(targetStation for targetStation in stations if targetStation.name == station)
                                targetStation.line[lineColor]['southStation'] = southStation
                                created_stations_on_line.append(currentStation)
                            else:
                                raise ValueError
            else:    # station is create in another line already
                for i in range(len(station_connection)):
                    if station not in created_stations_on_line:
                        if station_connection[i][0] == station:
                            if station_connection[i][3].lower() == 's':
                                currentStation, southStation, lineColor, direction = station_connection[i]
                                targetStation = next(targetStation for targetStation in stations if targetStation.name == station)
                                targetStation.addLine(lineColor, None, southStation)    # add new current line to existing station object
                                created_stations_on_line.append(currentStation)
                            elif station_connection[i][3].lower() == 'n':
                                currentStation, northStation, lineColor, direction = station_connection[i]
                                targetStation = next(targetStation for targetStation in stations if targetStation.name == station)
                                targetStation.addLine(lineColor, northStation, None)
                                created_stations_on_line.append(currentStation)
                            else:
                                raise ValueError
                        elif station_connection[i][1] == station:
                            if station_connection[i][3].lower() == 's':
                                northStation, currentStation, lineColor, direction = station_connection[i]
                                targetStation = next(targetStation for targetStation in stations if targetStation.name == station)
                                targetStation.addLine(lineColor, northStation, None)
                                created_stations_on_line.append(currentStation)
                            elif station_connection[i][3].lower() == 'n':
                                southStation, currentStation, lineColor, direction = station_connection[i]
                                targetStation = next(targetStation for targetStation in stations if targetStation.name == station)
                                targetStation.addLine(lineColor, None, southStation)
                                created_stations_on_line.append(currentStation)
                            else:
                                raise ValueError
                    else:    # if station is already created, update north and south stations
                        if station_connection[i][0] == station:
                            if station_connection[i][3].lower() == 's':
                                currentStation, southStation, lineColor, direction = station_connection[i]
                                targetStation = next(targetStation for targetStation in stations if targetStation.name == station)
                                targetStation.line[lineColor]['southStation'] = southStation
                                created_stations_on_line.append(currentStation)
                            elif station_connection[i][3].lower() == 'n':
                                currentStation, northStation, lineColor, direction = station_connection[i]
                                targetStation = next(targetStation for targetStation in stations if targetStation.name == station)
                                targetStation.line[lineColor]['northStation'] = northStation
                                created_stations_on_line.append(currentStation)
                            else:
                                raise ValueError
                        elif station_connection[i][1] == station:
                            if station_connection[i][3].lower() == 's':
                                northStation, currentStation, lineColor, direction = station_connection[i]
                                targetStation = next(targetStation for targetStation in stations if targetStation.name == station)
                                targetStation.line[lineColor]['northStation'] = northStation
                                created_stations_on_line.append(currentStation)
                            elif station_connection[i][3].lower() == 'n':
                                southStation, currentStation, lineColor, direction = station_connection[i]
                                targetStation = next(targetStation for targetStation in stations if targetStation.name == station)
                                targetStation.line[lineColor]['southStation'] = southStation
                                created_stations_on_line.append(currentStation)
                            else:
                                raise ValueError
    return stations              

# buildStations('stations1.csv', 'connections1.csv')


def buildTrain(num_of_trains, station_data):
    '''
    params: num_of_trains (int), station_data(list of objects)
    returns: list of objects, length should be the same as num_of_trains
    '''
    # function logic:
    # take a number for the amount of trains should be generate
    # loop from 1 to num_of_trains as train id
    # randomly decide which station(position) it's on
    # line based on position, if current station has more than one line, randomly decide which line it's on
    # randomly decide which direction (N or S)
    # use current station's delay probability to randomly decide if this train will delay or not    
    
    trains = []

    for i in range(1, num_of_trains+1):
        train_id = i
        target_Station = random.choice(station_data)
        train_position = target_Station.name
        station_lines = list(target_Station.line.keys())
        if len(station_lines) > 1:
            target_line = random.choice(station_lines)
            train_line = target_line
        else:
            train_line = station_lines[0]
        directions = ['n', 's']
        train_direction = random.choice(directions)
        train_delayed = random.random() < target_Station.delay
        trains.append(Train(train_id, train_position, train_line, train_direction, train_delayed))
    return trains


# station_data = buildStations('stations1.csv', 'connections1.csv')
# train_data = buildTrain(3, station_data)
# for train in train_data:
#     print(train.__dict__)


def driveTrain(station_data, train_data):
    '''
    params: station_data (list of station objects), train_data(list of train objects)
    returns: list of objects, should have same train objects as input but updated
    '''
    # function logic
    # every time this function is run each train will move forward one station
    # check if is at the end station for it's direction, means it can't go furthur but has to turn around
    # when train can all go forward, then update train to next station base on train position
    # train attributes that needs to be updated: position, delayed
    # train attributes remains the same: id, line, direction

    for train in train_data:
        target_Station = next(station for station in station_data if station.name == train.position)
        if train.direction == 's':    # check train's original direction
            if target_Station.line[train.line]['southStation'] == None:
                train.direction = 'n'
        else:
            if target_Station.line[train.line]['northStation'] == None:
                train.direction = 's'
        
        if train.direction == 's':    # check train's direction after modifying 
            next_station = next(station for station in station_data if station.name == target_Station.line[train.line]['southStation'])
        else:
            next_station = next(station for station in station_data if station.name == target_Station.line[train.line]['northStation'])

        new_position = next_station.name
        new_delayed = random.random() < next_station.delay

        train.position = new_position
        train.delayed = new_delayed

    return train_data


# station_data = buildStations('stations1.csv', 'connections1.csv')
# original_train_data = buildTrain(3, station_data)
# for train in original_train_data:
#     print(train.__dict__)

# train_data_1 = driveTrain(station_data, original_train_data)
# for train in train_data_1:
#     print(train.__dict__)

# train_data_2 = driveTrain(station_data, original_train_data)
# for train in train_data_2:
#     print(train.__dict__)


def trainInfo(train_id, station_data, train_data):
    '''
    params: train_id(int), train_data(list of train objects)
    returns: string of train info
    '''
    
    target_train = next(train for train in train_data if train.id == train_id)
    target_station = next(station for station in station_data if station.name == target_train.position)

    train_line = target_train.line.upper()
    train_position = target_train.position.upper()

    # if train is at the end station for current direction, should display as opposite direction
    train_direction = target_train.direction
    if train_direction == 's':
        if target_station.line[target_train.line]['southStation'] == None:
            train_direction = 'North'
        else:
            train_direction = 'South'
    else:
        if target_station.line[target_train.line]['northStation'] == None:
            train_direction = 'South'
        else:
            train_direction = 'North'

    # display delayed if train is delayed (true)
    if target_train.delayed:
        train_delayed = ' (delayed)'
    else:
        train_delayed = ''

    train_info = f'\nTrain {target_train.id} on {train_line} line is at Station {train_position} heading in {train_direction} direction{train_delayed}\n'
    return train_info


def connectionsMatrix(station_data, connection_data):
    '''
    params: station_data(list of station objects), connection_data(list of connection list)
    return: list of float lists
    '''
    station_names = []
    for station in station_data:
        station_names.append(station.name)
    station_names = sorted(station_names)
    station_count = len(station_names)
    graph = []
    for i in range(station_count):
        row_list = []
        for j in range(station_count):
            row_list.append(0)
        graph.append(row_list)
    for connection in connection_data:
        column_index = station_names.index(connection[0])
        row_index = station_names.index(connection[1])
        graph[column_index][row_index] = 1
        graph[row_index][column_index] = 1
    
    graph = csr_matrix(graph)

    result_matrix = []
    for i in range(station_count):
        dist_matrix, predecessors = dijkstra(csgraph=graph, directed=False, indices=i, return_predecessors=True)
        result_matrix.append(dist_matrix.tolist())
    
    for i in range(len(result_matrix)):
        for j in range(len(result_matrix[i])):
            result_matrix[i][j] = int(result_matrix[i][j])
    
    return result_matrix

# station_file = readStation('stations1.csv')
# connection_file = readConnection('connections1.csv')
# station_data = buildStations(station_file, connection_file)
# connectionsMatrix(station_data, connection_file)


def shortestPath(start_station, end_station, max_step, station_data, connection_matrix):
    '''
    params: start_station(str), end_station(str), max_step(int), station_data(list of station objects), connection_matrix (list of lists)
    return: Boolean, if one can go from start_station to end_station within max_step then return true, else return false
    '''
    # function logic:
    # generate sorted list of station names, station names' index will be used in connection_matrix
    # find distance between start_station and end_station
    # if distance > max_step then return false (end_station can't be reached from start_station within max_step)
    # else return true (end_station can be reached from start_station within max_step)

    station_names = []
    for station in station_data:
        station_names.append(station.name)
    station_names = sorted(station_names)

    start_station_index = station_names.index(start_station)
    end_station_index = station_names.index(end_station)

    distance = connection_matrix[start_station_index][end_station_index]

    if distance > max_step:
        return False
    else:
        return True



# station_file = readStation('stations1.csv')
# connection_file = readConnection('connections1.csv')
# station_data = buildStations(station_file, connection_file)
# connection_matrix = connectionsMatrix(station_data, connection_file)
# print(shortestPath('a', 'z', 7, station_data, connection_matrix))


def main():
    '''
    main function to control the flow of program
    '''
    # function logic
    # ask for station file, connection file, and amount of trains to stimulate
    # generate stations, connections, and trains
    # allow user to select between continue simulation [1], train info [2], exit [q], anything other than 1,2,q should consider input error
    # select 1: run driveTrain function once
    # select 2: ask for train id [1 - n], display current train information
    # select q: exit function

    while True:
        try:
            station_file = input('Enter name of stations file: ')
            station_data = readStation(station_file)
            break
        except FileNotFoundError:
            print("That file does not exist.")
    
    while True:
        try:
            connection_file = input('Enter name of connections file: ')
            connection_data = readConnection(connection_file)
            break
        except FileNotFoundError:
            print("That file does not exist.")
    
    while True:
        try:
            num_of_trains = input('Enter how many trains to simulate: ')
            if int(num_of_trains) and int(num_of_trains) > 0:
                num_of_trains = int(num_of_trains)
            else:
                raise ValueError
            break
        except ValueError:
            print("Please enter a number at least 1.")

    # build stations, connections, and trains
    stations = buildStations(station_data, connection_data)
    trains = buildTrain(num_of_trains, stations)

    # get sorted station names
    station_names = []
    for i in range(len(stations)):
        station_names.append(stations[i].name.lower())
    station_names = sorted(station_names)

    while True:
        try:
            print("Continue simulation [1], train info [2], route info [3], exit [q].")
            current_mode = input("Select an option: ")
            if current_mode == '1':
                trains = driveTrain(stations, trains)
                print('\n')
            elif current_mode == '2':
                while True:
                    try:
                        target_train = input(f'Which train [1 - {num_of_trains}]: ')
                        if int(target_train) and int(target_train) > 0 and int(target_train) <= num_of_trains:
                            print((trainInfo(int(target_train), stations, trains)))
                            break
                        else:
                            raise ValueError
                    except ValueError:
                        print("Please enter a valid train number.")
            elif current_mode == '3':
                while True:
                    try:
                        start_station = input("Select a start station: ")
                        if start_station.lower() in station_names:
                            start_station = start_station.lower()
                            break
                        else:
                            raise ValueError
                    except ValueError:
                        print("Please enter a valid station name.")
                
                while True:
                    try:
                        end_station = input("Select an end station: ")
                        if end_station.lower() in station_names:
                            end_station = end_station.lower()
                            break
                        else:
                            raise ValueError
                    except ValueError:
                        print("Please enter a valid station name.")

                while True:
                    try:
                        max_step = input("Select timesteps:")
                        if int(max_step):
                            max_step = int(max_step)
                            break
                        else:
                            raise ValueError
                    except ValueError:
                        print("Please enter a number at least 1.")

                # create station connection matrix for shortest path
                connection_matrix = connectionsMatrix(stations, connection_data)

                if shortestPath(start_station, end_station, max_step, stations, connection_matrix):
                    print(f'\nStation {end_station.upper()} is reachable from station {start_station.upper()} within {max_step} timesteps.\n')
                else:
                    print(f'\nStation {end_station.upper()} is not reachable from station {start_station.upper()} within {max_step} timesteps.\n')
            elif current_mode.lower() == 'q':
                sys.exit("Thank you and goodbye!")
            else:
                raise ValueError
        except ValueError:
            print("Invalid input, try again.")
    
    

if __name__ == '__main__':
    main()