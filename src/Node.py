# A class to hold all the information on each node
class Node:

    nodeNum = 0
    coodX = 0.0
    coodY = 0.0

    def __init__(self, nodeNum, coodX, coodY):

        self.nodeNum = nodeNum
        self.coodX = coodX
        self.coodY = coodY

    def getNodeNum(self):

        return self.nodeNum

    def getCoodX(self):

        return self.coodX

    def getCoodY(self):

        return self.coodY
