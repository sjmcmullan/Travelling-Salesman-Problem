from Node import Node
import time as timer
import sys
import math
import sqlite3

startTime = timer.time()


def checkTime(timeAllowed):
    if float((timer.time() - startTime)) >= timeAllowed:
        return False
    else:
        return True

# Calculates the Euclidean distance between 2 nodes.
def calcEucDist(node1, node2):

    xd = node2.coodX - node1.coodX
    yd = node2.coodY - node1.coodY
    return math.sqrt((xd * xd) + (yd * yd))


# Calculates and returns the current distance one must travel to visit each city
def getCurrentTourLength(nodeLst):

    totalDist = 0
    for x in range(len(nodeLst) - 1):
        totalDist = totalDist + calcEucDist(nodeLst[x], nodeLst[x + 1])
    return totalDist


# A helper function for the greedy algorithm, finds the node in a list that has the shortest distance
# from the other provided node.
def findClosestNode(node, nodeLst):

    index = 0
    shortestDist = 99999999999.99999

    for x in range(len(nodeLst)):
        if calcEucDist(node, nodeLst[x]) < shortestDist:
            shortestDist = calcEucDist(node, nodeLst[x])
            index = x

    return index


# My implementation of the greedy algorithm.
def greedy(nodeLst):

    newTour = nodeLst[1:]
    currentRoute = []
    currentRoute.append(nodeLst[0])
    for x in range(len(newTour)):
        index = findClosestNode(currentRoute[-1], newTour)
        currentRoute.append(newTour[index])
        newTour.pop(index)

    return currentRoute, getCurrentTourLength(currentRoute), int((timer.time() - startTime))


# Reverses a section of nodes in the list, thus swapping the ends of 2 edges.
# This will eliminate paths that cross over each other.
def swap(route, x, z):

    newRoute = route[0:x]
    newRoute.extend(reversed(route[x:z + 1]))
    newRoute.extend(route[z + 1:])

    return newRoute

# My implementation of 2-opt algorithm. Keeps going until it cannot improve the overall route any more.
# The starting list of nodes is just whatever order they are read in as.
# Will (hopefully) return the route with the best solution
def twoOpt(origNodeLst):

    cont = True
    while cont == True:
        currentRoute = origNodeLst
        bestDist = getCurrentTourLength(currentRoute)

        for x in range(len(currentRoute) - 1):
            for z in range((x + 1), len(currentRoute)):
                newRoute = swap(currentRoute, x, z)
                newDist = getCurrentTourLength(newRoute)

                if newDist < bestDist:
                    currentRoute = newRoute
                else:
                    cont = False

    return currentRoute, bestDist, float((timer.time() - startTime)), True

try:
    dbConnection = sqlite3.connect("Database\\TSP.db")
    dbCursor = dbConnection.cursor()
except:
    sys.stderr.write("Could not connect to database.")

problemName = ""
problemComment = ""
dimension = 0
edgeWeightType = ""
nodes = ""

origNodeLst = []
bestDist = 0
end = False
timeAllowed = 0

# Add a problem to the database.
if sys.argv[2] == "ADD":
    fle = open(sys.argv[3], mode='r')

    for line in fle:
        if line.startswith("NAME"):
            problemName = line.split(": ")[1].strip()
        if line.startswith("COMMENT"):
            problemComment = line.split(": ")[1].strip()
        if line.startswith("DIMENSION"):
            dimension = int(line.split(": ")[1].strip())
        if line.startswith("EDGE_WEIGHT_TYPE"):
            edgeWeightType = line.split(": ")[1].strip()

        if line.startswith("NODE_COORD_SECTION"):
            break
        line = line

    for line in fle:
        if line == "EOF\n":
            break
        else:
            nodes += line

    fle.close()

    try:
        dbCursor.execute(
            "INSERT INTO Problem VALUES (?, ?, ?, ?, ?, ?)", 
            (2, problemName, problemComment, dimension, edgeWeightType, nodes))
        dbConnection.commit()
    except:
        sys.stderr.write("Something went wrong.")
    dbConnection.close()

# Retreive a problem, solve it, then store it.
elif sys.argv[2] == "SOLVE":
    try:
        dbCursor.execute(
            "SELECT * FROM Problem WHERE problemName=?", (sys.argv[1],))
        tmp = dbCursor.fetchall()

        
        dimension = int(tmp[0][3])
        tmpStr = str(tmp[0][5]).splitlines()

        for x in tmpStr:
            tmpNode = Node(int(x.split()[0]), eval(x.split()[1]), eval(x.split()[2]))
            origNodeLst.append(tmpNode)

        timeAllowed = int(sys.argv[3])
        # Start of greedy, then 2-opt
        while checkTime(timeAllowed) and not end:
            newNodeLst, bestDist, timeReturned = greedy(origNodeLst)
            newNodeLst, bestDist, timeReturned, end = twoOpt(newNodeLst)
        
        if timeReturned >= timeAllowed:
            bestRoute = ""
            print("The best route that could be found in the allotted time was:", bestDist)
            print("The route is: ")
            for x in newNodeLst:
                print(x.nodeNum, end=' ')
                bestRoute += (str(x.nodeNum) + " ")

            try:
                dbCursor.execute(
                    "INSERT INTO Solution VALUES (?, ?, ?, ?, ?, DATE('now'))", 
                    (3, sys.argv[1], bestRoute, bestDist, timeAllowed))
                dbConnection.commit()
            except:
                sys.stderr.write("Something went wrong.")
            dbConnection.close()

        else:
            bestRoute = ""
            print("The best route that was found was:", bestDist, "in", timeReturned, "seconds.")
            print("The route is: ")
            for x in newNodeLst:
                print(x.nodeNum, end=' ')
                bestRoute += (str(x.nodeNum) + " ")

            try:
                dbCursor.execute(
                    "INSERT INTO Solution VALUES (?, ?, ?, ?, ?, DATE('now'))", 
                    (3, sys.argv[1], bestRoute, bestDist, timeReturned))
                dbConnection.commit()
            except:
                sys.stderr.write("Something went wrong.")
            dbConnection.close()
    except:
        sys.stderr.write("That problem does not exist in the database.")
        dbConnection.close()

elif sys.argv[2] == "FETCH":
    try:
        dbCursor.execute(
            "SELECT * FROM Solution WHERE problemName=?", (sys.argv[1],))
        tmp = dbCursor.fetchall()
        
        problemName = tmp[0][1]
        route = tmp[0][2]
        bestDist = tmp[0][3]
        timeTaken = tmp[0][4]
        solvedOn = tmp[0][5]

        print("The best route that was found for the", problemName, "probelm was:", bestDist, "in", timeTaken, "seconds.")
        print("The route is:", route)
        print("It was solved on:", solvedOn)
    except:
        sys.stderr.write("That solution does not exist in the database.")
        dbConnection.close()