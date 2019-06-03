import sys
sys.path.append('../')
from tool import *
from agent.constants import unload_tm

def init():
    pass

class RouteAgent:
    cList = None
    edges = None
    volume = 0
    weight = 0
    tot_dist = 0
    max_volume = 16
    max_weight = 2.5
    timeof  = None
    distof = None
    def __init__(self, edges):
        self.cList = [(0, 8*60, 8*60), (0, 24*60, 24*60)]  #8:00-8:00 and 24:00-24:00
        self.edges = edges
        self.timeof = lambda x,y: self.edges.get_edge(x, y).spend_tm if x!=y else 0
        self.distof = lambda x,y: self.edges.get_edge(x, y).dist if x!=y else 0

    def traversing(self):
        for i in range(1, len(self.cList) - 1):
            yield i, self.cList[i][0]
        
    def check_goods(self, x):
        return self.volume + x.volume <= self.max_volume and self.weight + x.weight <= self.max_weight

    def check_route(self, x, pos):
        pre = self.cList[pos-1]
        nxt = self.cList[pos]
        reach_tm = max(pre[2] + self.timeof(pre[0], x.id), x.first_tm)
        leave_tm = nxt[1] - self.timeof(x.id, nxt[0])
        if(reach_tm <= x.last_tm and reach_tm + unload_tm <= leave_tm):
            return ((pos, self.distof(pre[0], x.id) + self.distof(x.id, nxt[0]) - self.distof(pre[0], nxt[0])), True)
        else:
            return ((-1, 0), False)

    def find_insert_pos(self, x):
        insert_pos, extra_cost = None, None
        if(not self.check_goods(x)):
            pass
        else:
            for i in range(1, len(self.cList)):
                result = self.check_route(x, i)
                if(result[1]):
                    insert_pos, extra_cost = result[0]
                    break
        return (insert_pos, extra_cost)

    def check_before_insert(self, x, info):
        pos, cost = info
        if(not self.check_goods(x)):
            return False
        else:
            result = self.check_route(x, pos)
            return result[1] and result[0][1] == cost
    
    def insert(self, x, info):
        pos, cost = info
        self.weight += x.weight
        self.volume += x.volume
        self.tot_dist += cost
        reach_tm = max(self.cList[pos-1][2] + self.timeof(self.cList[pos-1][0], x.id), x.first_tm)
        self.cList.insert(pos, (x.id, reach_tm, reach_tm + unload_tm))
        x.set_cond(self, reach_tm)
        #here update info in x
    
    def check_remove_cost(self, pos):
        pre = self.cList[pos-1]
        ths = self.cList[pos]
        nxt = self.cList[pos+1]
        return self.distof(pre[0], nxt[0]) - self.distof(pre[0], ths[0]) - self.distof(ths[0], nxt[0])
    
    def check_before_remove(self, x, info):
        pos, cost = info
        return self.cList[pos][0] == x.id and self.check_remove_cost(pos) == cost

    def remove(self, x, info):
        pos, cost = info
        self.weight -= x.weight
        self.volume -= x.volume
        self.tot_dist -= cost
        self.cList.pop(pos)
        x.set_cond(None, None)
    
    def print(self):
        print("route start")
        for nd in self.cList:
            print("(%d at %d) -> " % (nd[0], nd[1]))
        print("route end")
