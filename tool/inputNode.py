import pandas as pd
class Node:
    def __init__(self, id, x, y, nd_type):
        self.id, self.x, self.y, self.nd_type = id, x, y, nd_type

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
    def __init__(self):
        self.nodes = list()
    
    def getdata(self, readFile = r'.\input_node.xlsx'):
        data = pd.read_excel(readFile)

        for i in range(len(data)):
            nd = data.ix[i]
            if(nd[1] == 1): #type = Center
                self.nodes.append(CenterNode(nd[0], nd[2], nd[3]))
            elif(nd[1] == 2): #type = Customer
                self.nodes.append(CustomerNode(nd[0], nd[2], nd[3], nd[4], nd[5], self.time2int(nd[6]), self.time2int(nd[7])))
            elif(nd[1] == 3): #type = Station
                self.nodes.append(StationNode(nd[0], nd[2], nd[3]))
            else:
                raise Exception("Unknown node type %d" % nd[1])
        #print(self.nodes[2].nd_type, self.nodes[2].x, self.nodes[2].last_tm)
        return self.nodes
    
    @staticmethod
    def time2int(t):
        return t.hour * 3600 + t.minute * 60 + t.second

nd=Nodes()
nd.getdata()

