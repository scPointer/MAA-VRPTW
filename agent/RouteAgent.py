import sys
sys.path.append('../')
#from tool import *
from agent import constants
from agent.constants import unload_tm, INF

def init():
    pass

class RouteAgent:
    cList = None
    edges = None
    chargeChoice = None
    charge_pos = None
    charge_info = None
    volume = 0
    weight = 0
    tot_dist = 0

    before_charge = None
    max_volume = None
    max_weight = None
    unit_trans_cost = None
    driving_range = None
    max_dist = 999999
    max_reverse_cost = 0
    max_shuffle_cost = 0
    feasible = True
    timeof  = None
    distof = None
    def __init__(self, edges, center, chargeChoice, vehi_info):
        self.cList = [(0, 8*60, 8*60, center), (0, 24*60, 24*60, center)]  #8:00-8:00 and 24:00-24:00
        self.edges = edges
        self.chargeChoice = chargeChoice
        self.max_volume, self.max_weight, self.unit_trans_cost, self.driving_range = vehi_info
        self.timeof = lambda x,y: self.edges.get_edge(x, y).spend_tm if x!=y else 0
        self.distof = lambda x,y: self.edges.get_edge(x, y).dist if x!=y else 0

    def traversing(self):
        for i in range(1, len(self.cList) - 1):
            yield i, self.cList[i][0]

    def update(self, vehi_info):
        self.max_volume, self.max_weight, self.unit_trans_cost, self.driving_range = vehi_info
        
    def check_goods(self, x):
        return self.volume + x.volume <= self.max_volume and self.weight + x.weight <= self.max_weight

    def check_route(self, x, pos, pre_idx = -1, nxt_idx = 0):
        pre = self.cList[pos + pre_idx]
        nxt = self.cList[pos + nxt_idx]
        reach_tm = max(pre[2] + self.timeof(pre[0], x.id), x.first_tm)
        leave_tm = nxt[1] - self.timeof(x.id, nxt[0])
        if(reach_tm <= x.last_tm and reach_tm + unload_tm <= leave_tm):
            update_dist = self.distof(pre[0], x.id) + self.distof(x.id, nxt[0]) - self.distof(pre[0], nxt[0])
            if(self.tot_dist + update_dist <= self.max_dist):
                return ((pos, update_dist), True)
            else:
                return ((None, None), False)
        else:
            return ((None, None), False)

    def check_insert_pos(self, x, pos):
        insert_pos, extra_cost = None, None
        if(not self.check_goods(x)):
            pass
        else:
            result = self.check_route(x, pos)
            if(result[1] and self.tot_dist - self.before_charge + result[0][1] <= self.driving_range):
                insert_pos, extra_cost = result[0]
        return (insert_pos, extra_cost)

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
    
    def time_schedule_as_late_as_possible(self, pos):
        ths = self.cList[pos]
        nxt = self.cList[pos + 1]
        reach_tm = nxt[1] - self.timeof(ths[0], nxt[0]) - unload_tm
        if(pos > 0):
            reach_tm = min(reach_tm, ths[3].last_tm)
        self.cList[pos] = (ths[0], reach_tm, reach_tm + unload_tm, ths[3])

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
            new_cost = self.reverse_nodes(i, i + 2)
            if(new_cost != None):
                update_cost += new_cost

        for i in range(1, len(self.cList) - 3):
            new_cost = self.reverse_nodes(i, i + 3)
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

    def output_route(self, outputFile):
        node_num = len(self.cList) - 2 + (1 if self.charge_pos == None else 0)
        string = ""
        if(not self.feasible):
            string += "INFEASIBLE\n"
        string += "totdist = %d , weight = %.3f, volume = %.3f, (node, dist to previous node, reach time, leave time) = \n" \
            % (self.tot_dist, self.weight, self.volume)
        
        for i in range(1, len(self.cList) - 1):
            ths = self.cList[i]
            pre = self.cList[i - 1]
            if(self.charge_pos == i - 1):
                info = self.charge_info
                reach_tm = pre[2] + self.timeof(pre[0], info[0])
                leave_tm = reach_tm + constants.charge_tm
                string += "(%d,%d,%d,%d)," % (info[0], info[1][0], reach_tm, leave_tm)
                string += "(%d,%d,%d,%d)," % (ths[0], info[1][1], leave_tm + self.timeof(info[0], ths[0]), ths[2])
            else:
                string += "(%d,%d,%d,%d)," % (ths[0], self.distof(pre[0], ths[0]), pre[2] + self.timeof(pre[0], ths[0]), ths[2])
        
        if(self.charge_pos == len(self.cList) - 1):
            info = self.charge_info
            pre = self.cList[-2]
            reach_tm = pre[2] + self.timeof(pre[0], info[0])
            leave_tm = reach_tm + constants.charge_tm
            string += "(%d,%d,%d,%d)," % (info[0], info[1][0], reach_tm, leave_tm)
        outputFile.write(string[0:-1] + '\n')
        
    def check_feasibility(self):
        for i in range(1, len(self.cList) - 1):
            if(self.charge_pos == i - 1):
                if(self.cList[i - 1][2] + self.charge_info[2] > self.cList[i][1]):
                    raise Exception("arrive late after charging")
            else:
                if(not self.check_route(self.cList[i][3], i, -1, 1)[1]):
                    raise Exception("route infeasible")
                elif(self.cList[0][0] != 0 or self.cList[-1][0] != 0):
                    raise Exception("illegal")

    def get_waiting_cost(self):
        wait_time = 0
        for i in range(2, len(self.cList) - 1):
            pre = self.cList[i - 1]
            ths = self.cList[i]
            if(self.charge_pos == i - 1):
                wait_time += ths[1] - (pre[2] + self.charge_info[2])
            else:
                wait_time += ths[1] - (pre[2] + self.timeof(pre[0], ths[0]))
        return wait_time * constants.wait_cost
    
    def init_dist_list(self):
        lens = len(self.cList)
        dist_by = [None]
        pre_dist = [0]
        flo_dist = [0] * lens
        for i in range(1, lens):
            pre = self.cList[i - 1]
            ths = self.cList[i]
            dist_by.append(self.distof(pre[0], ths[0]))
            pre_dist.append(pre_dist[-1] + dist_by[-1])
        for i in reversed(range(lens - 1)):
            flo_dist[i] = flo_dist[i + 1] + dist_by[i + 1]
        return pre_dist, flo_dist

    def choose_charging(self):
        # take charging into consideration
        update_dist = 0
        if(self.tot_dist <= self.driving_range):
            return update_dist
        pre_dist, flo_list = self.init_dist_list()
        for i in reversed(range(len(self.cList) - 1)):           
            ths = self.cList[i]
            nxt = self.cList[i + 1]
            charge_info = self.chargeChoice(ths[0], nxt[0])
            dist_l, dist_r = charge_info[1]
            if(pre_dist[i] + dist_l > self.driving_range or dist_r + flo_list[i + 1] > self.driving_range \
                or ths[2] + charge_info[2] > nxt[1]):
                self.time_schedule_as_late_as_possible(i)
            else:
                self.charge_pos = i
                self.charge_info = charge_info
                update_dist = dist_l + dist_r - self.distof(ths[0], nxt[0])
                #print(ths[2], charge_info[2], nxt[1])
                break
        
        if(self.charge_pos == None):
            #raise Exception("available charging station not found")
            self.feasible = False
        self.tot_dist += update_dist
        return update_dist
    
    def pop_to(self, pos, newR):
        ths = self.cList[pos]
        new_pos = len(newR.cList) - 1
        info = newR.check_insert_pos(ths[3], new_pos)
        if(info[0] != None):
            x = ths[3]
            cost = self.check_remove_cost(pos)
            self.remove(x, (pos, cost))
            newR.insert(x, info)
            return True
        else:
            return False

    def route_dividing(self, newR):
        self.time_schedule_as_early_as_possible(1, 2)

        first_nd = self.cList[1][3]
        cost = self.check_remove_cost(1)
        self.remove(first_nd, (1, cost))

        newR.insert(first_nd, newR.find_insert_pos(first_nd))
        for pos in range(1, len(self.cList) - 1):
            ths = self.cList[pos]
            x = ths[3]
            charge_info = self.chargeChoice(first_nd.id, ths[0])
            if(newR.cList[1][2] + charge_info[2] <= x.last_tm and newR.check_goods(x)):
                reach_tm = max(newR.cList[1][2] + charge_info[2], x.first_tm)
                leave_tm = reach_tm + unload_tm
                newR.weight += x.weight
                newR.volume += x.volume
                newR.tot_dist += charge_info[1][0] + charge_info[1][1] \
                    + newR.distof(ths[0], newR.cList[2][0]) - newR.distof(newR.cList[1][0], newR.cList[2][0])
                
                cost = self.check_remove_cost(pos)
                self.remove(x, (pos, cost))
                newR.cList.insert(2, (x.id, reach_tm, leave_tm, x))
                newR.before_charge = newR.distof(newR.cList[1][0], newR.cList[0][0]) + charge_info[1][0]
                newR.charge_pos = 1
                newR.charge_info = charge_info
                x.set_cond(newR, reach_tm)
                break
        
        if(len(newR.cList) == 3):
            charge_info = newR.chargeChoice(newR.cList[1][0], newR.cList[2][0])
            newR.tot_dist += charge_info[1][0] + charge_info[1][1]
            newR.charge_pos = 1
            newR.charge_info = charge_info
        else:
            ended = False
            count = 0
            for pos in range(1, len(self.cList) - 1):
                if(ended or pos >= len(self.cList) - 1):
                    break
                while(self.pop_to(pos, newR)):
                    count += 1
                    if(count >=3 or pos >= len(self.cList) - 1):
                        ended = True
                        break
                