from trains import (
    Station,
    Train,
    readStation,
    readConnection,
    buildStations,
    buildTrain,
    driveTrain
)


def test_create_new_Station():
    B = Station("B", 0.001, "Green", "A", "C")
    assert(B.name) == "B"
    assert(B.delay) == 0.001
    assert(type(B.line)) == dict
    assert(B.__dict__) == {'name': 'B', 'delay': 0.001, 'line': {'Green': {'northStation': 'A', 'southStation': 'C'}}}

def test_addLine():
    B = Station("B", 0.001, "Green", "A", "C")
    B.addLine("Blue", "X", "Y")
    assert(B.name) == "B"
    assert(B.delay) == 0.001
    assert(type(B.line)) == dict
    assert(B.__dict__) == {'name': 'B', 'delay': 0.001, 'line': {'Green': {'northStation': 'A', 'southStation': 'C'}, 'Blue': {'northStation': 'X', 'southStation': 'Y'}}}
    

def test_readStation():
    data = readStation('stations1.csv')
    assert(type(data)) == dict
    assert(data) == {'a': 0.001, 'b': 0.001, 'c': 0.2, 'd': 0.001, 'x': 0.1, 'y': 0.1, 'z': 0.1}

def test_readConnection():
    data = readConnection('connections1.csv')
    assert(type(data)) == list
    assert(data) == [['a', 'b', 'blue', 'S'], ['b', 'c', 'blue', 'S'], ['c', 'd', 'blue', 'S'], ['x', 'y', 'green', 'S'], ['y', 'c', 'green', 'S'], ['c', 'z', 'green', 'S']]

stations = {'a': 0.001, 'b': 0.001, 'c': 0.2, 'd': 0.001, 'x': 0.1, 'y': 0.1, 'z': 0.1}
connections = [['a', 'b', 'blue', 'S'], ['b', 'c', 'blue', 'S'], ['c', 'd', 'blue', 'S'], ['x', 'y', 'green', 'S'], ['y', 'c', 'green', 'S'], ['c', 'z', 'green', 'S']]

def test_buildStations():
    data = buildStations(stations, connections)
    assert(type(data)) == list
    assert(len(data)) == len(readStation('stations1.csv'))


def test_buildTrain():
    station_data = buildStations(stations, connections)
    train_data = buildTrain(3, station_data)
    assert(type(train_data)) == list
    assert(len(train_data)) == 3


def test_driveTrain():
    station_data = buildStations(stations, connections)
    train_data = buildTrain(3, station_data)
    driveOnce = driveTrain(station_data, train_data)
    driveTwice = driveTrain(station_data, driveOnce)
    assert(type(driveOnce)) == list
    assert(driveOnce) == train_data
    assert(type(driveTwice)) == list
    assert(driveTwice) == driveOnce