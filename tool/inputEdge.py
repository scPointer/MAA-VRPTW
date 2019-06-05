class Edge:
    def __init__(self, data):
        self.ID, self.fNode, self.tNode, self.dist, self.spend_tm = (int(x) for x in data.split(','))

    def print(self):
        print("ID = %d, fNode = %d, tNode = %d, dist = %d, spend_tm = %d" \
            % (self.ID, self.fNode, self.tNode, self.dist, self.spend_tm))

class Edges:
    dList = None
    def __init__(self):
        self.dList = list()

    def get_data(self, readName):
        inputFile = open(readName, 'r')
        inputFile.readline()
        data = inputFile.read()
        edges_str = data.split('\n')
        self.dList = [Edge(x) for x in edges_str if x != '']
        return self.dList
    
    def get_edge(self, i, j):
        if(len(self.dList) == 0):
            raise Exception("Data not found. You should take getdata() first.")
        if(i == j):
            raise Exception("Try to get an edge of node %d itself." % i)
        elif(i > j):
            i, j = j, i
        return self.dList[i * 1100 + j - 1] 

def initEdges(readName):
    edges = Edges()
    edges.get_data(readName)
    return edges
