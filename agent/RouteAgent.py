import sys
sys.path.append('../')
from tool import *
from agent.constants import unload_tm, INF

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
    max_reverse_cost = 0
    max_shuffle_cost = 0
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

    def check_route(self, x, pos, pre_idx = -1, nxt_idx = 0):
        pre = self.cList[pos + pre_idx]
        nxt = self.cList[pos + nxt_idx]
        reach_tm = max(pre[2] + self.timeof(pre[0], x.id), x.first_tm)
        leave_tm = nxt[1] - self.timeof(x.id, nxt[0])
        if(reach_tm <= x.last_tm and reach_tm + unload_tm <= leave_tm):
            return ((pos, self.distof(pre[0], x.id) + self.distof(x.id, nxt[0]) - self.distof(pre[0], nxt[0])), True)
        else:
            return ((None, None), False)

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

    def check_can_replace(self, x, y, pos):
        if(self.volume - x.volume + y.volume > self.max_volume \
            or self.weight - x.weight + y.weight > self.max_weight):
            return None
        else:
            if(pos >= len(self.cList) - 1):
                return False
            result = self.check_route(y, pos, -1, 1)
            return result[0][1] if result[1] else None

    def check_before_insert(self, x, info):
        pos, cost = info
        if(not self.check_goods(x)):
            return False
        else:
            if(pos >= len(self.cList) - 1):
                return False
            result = self.check_route(x, pos)
            return result[1] and result[0][1] == cost
    
    def insert(self, x, info):
        pos, cost = info
        self.weight += x.weight
        self.volume += x.volume
        self.tot_dist += cost
        reach_tm = max(self.cList[pos-1][2] + self.timeof(self.cList[pos-1][0], x.id), x.first_tm)
        self.cList.insert(pos, (x.id, reach_tm, reach_tm + unload_tm, x))
        x.set_cond(self, reach_tm)
        #here update info in x
    
    def check_remove_cost(self, pos):
        pre = self.cList[pos-1]
        ths = self.cList[pos]
        nxt = self.cList[pos+1]
        return self.distof(pre[0], nxt[0]) - self.distof(pre[0], ths[0]) - self.distof(ths[0], nxt[0])
    
    def check_before_remove(self, x, info):
        pos, cost = info
        if(pos >= len(self.cList) - 1):
            return False
        return self.cList[pos][0] == x.id and self.check_remove_cost(pos) == cost

    def remove(self, x, info):
        pos, cost = info
        self.weight -= x.weight
        self.volume -= x.volume
        self.tot_dist += cost
        self.cList.pop(pos)
        x.set_cond(None, None)
    
    def time_schedule_as_early_as_possible(self, begin, end):
        saved_list = self.cList[begin: end]
        failed = False
        for pos in range(begin, end):
            pre = self.cList[pos-1]
            x = self.cList[pos][3]
            reach_tm = max(pre[2] + self.timeof(pre[0], x.id), x.first_tm)
            if(reach_tm <= x.last_tm):
                self.cList[pos] = (x.id, reach_tm, reach_tm + unload_tm, x)
            else:
                failed = True
                break
        if((not failed) and self.check_route(self.cList[end - 1][3], end - 1, -1, 1)):
            return True
        else:
            self.cList = self.cList[:begin] + saved_list + self.cList[end:]
            return False

    def reverse_nodes(self, begin, end):
        nd_pre, nd_first, nd_last, nd_nxt = self.cList[begin - 1], self.cList[begin], self.cList[end -1], self.cList[end] 
        cost = self.distof(nd_pre[0], nd_last[0]) + self.distof(nd_first[0], nd_nxt[0]) \
            - self.distof(nd_pre[0], nd_first[0]) - self.distof(nd_last[0], nd_nxt[0])
        if(cost > self.max_reverse_cost):
            return None
        
        saved_list = self.cList[begin: end]
        self.cList = self.cList[:begin] + reversed(saved_list) + self.cList[end:]
        if(not self.time_schedule_as_early_as_possible(begin, end)):
            self.cList = self.cList[:begin] + saved_list + self.cList[end:]
            return None
        else:
            return cost

    def route_reverse(self):
        update_cost = 0
        for i in range(1, len(self.cList) - 2):
            new_cost = self.reverse_nodes(i, i+1)
            if(new_cost != None):
                update_cost += new_cost

        for i in range(1, len(self.cList) - 3):
            new_cost = self.reverse_nodes(i, i+2)
            if(new_cost != None):
                update_cost += new_cost
        self.tot_dist += update_cost
        return update_cost

    def route_shuffle(self):
        cust_len = len(self.cList) - 1
        remove_info = [(i, self.check_remove_cost(i)) for i in range(1, cust_len)]
        remove_info.insert(0, (None, None))

        exchange_pair = (INF,) + (None,) * 2
        for i in range(1, cust_len):
            for j in range(i + 2, cust_len):
                node_i, node_j = self.cList[i][3], self.cList[j][3]
                info_i, can_insert_i = self.check_route(node_i, j, -1, 1)
                info_j, can_insert_j = self.check_route(node_j, i, -1, 1)
                if(can_insert_i and can_insert_j):
                    cost = info_i[1] + info_j[1] + remove_info[i][1] + remove_info[j][1]
                    if(cost < exchange_pair[0]):
                        exchange_pair = (cost, (node_i, remove_info[i], info_i), (node_j, remove_info[j], info_j))
        
        if(exchange_pair[0] < self.max_shuffle_cost):
            node_i, remove_info_i, info_i = exchange_pair[1]
            node_j, remove_info_j, info_j = exchange_pair[2]
            self.remove(node_j, remove_info_j)
            self.remove(node_i, remove_info_i)
            self.insert(node_i, info_i)
            self.insert(node_j, info_j)
            self.tot_dist += exchange_pair[0]
            return exchange_pair[0]
        else:
            return 0
    
    def route_optimization(self):
        times = 0
        update_cost = 0
        for i in range(times):
            update_cost += self.route_reverse()
            update_cost += self.route_shuffle()
        return update_cost

    def print(self):
        print("route start")
        for nd in self.cList:
            print("(%d at %d) -> " % (nd[0], nd[1]))
        print("route end")

    def check_feasibility(self):
        for i in range(1, len(self.cList) - 1):
            if(not self.check_route(self.cList[i][3], i, -1, 1)[1]):
                raise Exception("route infeasible")
            elif(self.cList[0][0] != 0 or self.cList[-1][0] != 0):
                raise Exception("illegal")