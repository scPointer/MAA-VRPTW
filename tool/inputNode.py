import pandas as pd

class Node:
    def __init__(self, id, x, y, nd_type):
        self.id, self.x, self.y, self.nd_type = id, x, y, nd_type
    
    def print_pos(self):
        print("x=%lf, y=%lf" % (self.x, self.y))

class CenterNode(Node):
    def __init__(self, id, x, y):
        Node.__init__(self, id, x, y, "Center")

class StationNode(Node):
    def __init__(self, id, x, y,):
        Node.__init__(self, id, x, y, "Station")

class CustomerNode(Node):
    def __init__(self, id, x, y, weight, volume, first_tm, last_tm):
        Node.__init__(self, id, x, y, "Customer")
        self.weight, self.volume, self.first_tm, self.last_tm = weight, volume, first_tm, last_tm

class Nodes:
    centNodes = list()
    custNodes = list()
    statNodes = list()
    def __init__(self):
        pass
    
    def getdata(self, readFile):
        data = pd.read_excel(readFile)

        for i in range(len(data)):
            nd = data.ix[i]
            if(nd[1] == 1): #type = Center
                self.centNodes.append(CenterNode(nd[0], nd[2], nd[3]))
            elif(nd[1] == 2): #type = Customer
                self.custNodes.append(CustomerNode(nd[0], nd[2], nd[3], nd[4], nd[5], self.time2int(nd[6]), self.time2int(nd[7])))
            elif(nd[1] == 3): #type = Station
                self.statNodes.append(StationNode(nd[0], nd[2], nd[3]))
            else:
                raise Exception("Unknown node type %d" % nd[1])
        #print(self.nodes[2].nd_type, self.nodes[2].x, self.nodes[2].last_tm)
        return (self.centNodes, self.custNodes, self.statNodes)
    
    @staticmethod
    def time2int(t):
        return t.hour * 60 + t.minute

def initNodes(readFile = r'.\input_node.xlsx'):
    return Nodes().getdata(readFile)
