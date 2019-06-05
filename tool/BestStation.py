class BestStationChoice:
    edges = None
    statNodes = None
    statChoice = None

    cust_cnt = None
    charge_tm = None
    distof = None
    timeof = None
    def __init__(self, edges, statNodes, cust_cnt, charge_tm):
        self.edges, self.statNodes, self.cust_cnt, self.charge_tm = edges, statNodes, cust_cnt, charge_tm
        self.timeof = lambda x, y: self.edges.get_edge(x, y).spend_tm if x!=y else 0
        self.distof = lambda x, y: self.edges.get_edge(x, y).dist if x!=y else 0
    
    def get_station_choice(self):
        self.statChoice = list()
        for i in range(self.cust_cnt):
            print(i)
            self.statChoice.append(list())
            for j in range(self.cust_cnt):
                choice = (None, (None, None), None, None)
                for stat in self.statNodes:
                    dist_pre = self.distof(i, stat.id)
                    dist_nxt = self.distof(stat.id, j)
                    time = self.timeof(i, stat.id) + self.charge_tm + self.timeof(stat.id, j)
                    if(choice[0] == None or dist_pre + dist_nxt < choice[1][0] + choice[1][1]):
                        choice = (stat.id, (dist_pre, dist_nxt), time, stat)
                self.statChoice[i].append(choice)
        return self.statChoice

class Stations:
    choiceInfo = None
    cust_cnt = None
    inputFile = None
    def __init__(self, cust_cnt, fileName):
        self.cust_cnt = cust_cnt
        self.inputFile = open(fileName, "r")

    def read_best_choice(self):
        self.choiceInfo = list()

        data = self.inputFile.read()
        edges_str = data.split('\n')
        for line in edges_str:
            if(line != ''):
                block = [int(x) for x in line.split(',')]
                self.choiceInfo.append((block[0], (block[1], block[2]), block[3]))
        return lambda x, y: self.choiceInfo[x * self.cust_cnt + y - 1]


def init_best_station(edges, statNodes, cust_cnt, charge_tm, outputFile):
    Choice = BestStationChoice(edges, statNodes, cust_cnt, charge_tm)
    statChoice = Choice.get_station_choice()
    for line in statChoice:
        string = ""
        for block in line:
            string += "%d,%d,%d,%d\n" % (block[0], block[1][0], block[1][1], block[2])
        outputFile.write(string)

def get_best_station(cust_cnt, fileName):
        chargeChoice = Stations(cust_cnt, fileName)
        return chargeChoice.read_best_choice()