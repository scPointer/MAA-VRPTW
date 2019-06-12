import sys
sys.path.append('../')
from tool.inputNode import CenterNode
from agent import constants
from agent.constants import unload_tm, INF, iveco_info, truck_info

class Operation:
    def __init__(self, op_type, id, opr):
        self.op_type, self.id, self.goal, self.cost = op_type, id, opr[0], opr[1] # opr = (goal, cost)

class PlannerAgent(CenterNode):
    custAgents = None
    routes = None
    movePool = None

    newRoute = None

    cust_counts = None

    tot_dist = None
    tot_cost = None
    custInfo = None
    insertInfo = None
    originBelong = None
    exchangeNodes = None
    def __init__(self, d, custAgents, newRoute):
        CenterNode.__init__(self, d.id, d.x, d.y)
        self.custAgents = custAgents
        
        self.newRoute = newRoute
        self.routes = [self.newRoute(truck_info)]
        
        self.cust_counts = len(self.custAgents)
        self.tot_dist = 0

    def get_initial_solution(self):
        for nd in reversed(self.custAgents):
            insert_pos, extra_cost = None, None
            for route in self.routes:
                insert_pos, extra_cost = route.find_insert_pos(nd)
                if(insert_pos != None):
                    route.insert(nd, (insert_pos, extra_cost))
                    self.tot_dist += extra_cost
                    break
            if(insert_pos == None):
                self.routes.append(self.newRoute(truck_info))
                insert_pos, extra_cost = self.routes[-1].find_insert_pos(nd)
                self.routes[-1].insert(nd, (insert_pos, extra_cost))
                self.tot_dist += extra_cost
        
        #afterwork
        #to conform that custAgents[i].id == i
        #for route in self.routes:
        #    route.max_dist = 150000
        self.custAgents.sort(key = lambda nd: nd.id)
        self.custAgents.insert(0, None)
        for route in self.routes:
            if(route.tot_dist < truck_info[3]):
                route.update(iveco_info)
    
    def print_solution(self, fileName):
        outputFile = open(fileName, 'w')
        for route in self.routes:
            route.output_route(outputFile)

    def find_charging_station(self):
        for route in self.routes:
            self.tot_dist += route.choose_charging()
            if(route.feasible == False):
                route.update(truck_info)
                route.feasible = True
                self.tot_dist += route.choose_charging()

            while(route.feasible == False):
                self.routes.append(self.newRoute(truck_info))
                route.route_dividing(self.routes[-1])
                route.feasible = True
                route.choose_charging()
    
    def check_solution(self):
        #print("route counts", len(self.routes))
        #print("first route")
        #self.routes[0].print()
        count, dist, dist_cost = 0, 0, 0
        for route in self.routes:
            count += len(route.cList) - 2
            dist += route.tot_dist
            dist_cost += route.tot_dist * route.unit_trans_cost
        if(count != self.cust_counts):
            raise Exception("customer loss")
        #for route in self.routes:
         #   route.check_feasibility()
        print("routes=", len(self.routes))
        print("tot_dist=", dist)
        
        vehi_cost = len(self.routes) * constants.vehicle_cost
        wait_cost = 0
        charging_cost = 0
        for route in self.routes:
            wait_cost += route.get_waiting_cost()
            charging_cost += constants.charge_cost if route.charge_pos != None else 0
        print("wait_cost=", wait_cost)
        print("charging_cost=", charging_cost)
        
        self.tot_cost = dist_cost + vehi_cost + wait_cost + charging_cost
        print("tot_cost=", self.tot_cost) 
    #    for r in routes:
    #        print(len(r.cList), r.volume, r.weight)
        """for i in range(20):
            cust = self.custAgents[i]
            r0 = cust.belong_to
            info = (cust.id, cust.served_tm, cust.served_tm + unload_tm)
            print(info)
            print(r0.cList)
            print(r0.cList.index(info))
            print(r0.check_remove_cost(r0.cList.index(info)))"""
    
    def init_movePool(self):
        cust_len = self.cust_counts + 1
        route_cnt = len(self.routes)
        remove_info = [(None, None)] * cust_len
        for route in self.routes:
            for pos, nodeid in route.traversing():
                remove_info[nodeid] = (pos, route.check_remove_cost(pos))
        self.custInfo = remove_info
        
        belong_route = [None] * cust_len
        insert_info = [[(None, None)] * route_cnt for x in range(cust_len)]
        for i in range(1, cust_len):
            for j in range(route_cnt):
                node = self.custAgents[i]
                route = self.routes[j]
                if(route is not node.belong_to):
                    insert_info[i][j]=route.find_insert_pos(node)
                else:
                    belong_route[i] = j
        self.originBelong = belong_route
        self.insertInfo = insert_info

        for i in range(1, cust_len):
            if remove_info[i][0] == None:
                print(i ,belong_route[i])
                self.routes[belong_route[i]].print()
        
        exchange_info = [[None] * (cust_len) for x in range(cust_len)]
        for i in range(1, cust_len):
            for j in range(1, cust_len):
                if(belong_route[i] == belong_route[j]):
                #if(i == j):
                    continue
                elif(i > j):
                    #exchange_info[i][j] = exchange_info[j][i]
                    continue
                node_i = self.custAgents[i]
                node_j = self.custAgents[j]
                replace_i_with_j = node_i.belong_to.check_can_replace(node_i, node_j, remove_info[i][0])
                replace_j_with_i = node_j.belong_to.check_can_replace(node_j, node_i, remove_info[j][0])
                if(replace_i_with_j != None and replace_j_with_i != None):
                    exchange_info[i][j] = replace_i_with_j + replace_j_with_i + remove_info[i][1] + remove_info[j][1]

        C_Best_Insert = [(None, INF)] * cust_len
        R_Best_Insert = [(None, INF)] * route_cnt
        for i in range(1, cust_len):
            for j in range(route_cnt):
                if(insert_info[i][j][0] == None):
                    continue
                insert_cost = insert_info[i][j][1] + remove_info[i][1]
                if(insert_cost < C_Best_Insert[i][1]):
                    C_Best_Insert[i] = (j, insert_cost)
                if(insert_cost < R_Best_Insert[j][1]):
                    R_Best_Insert[j] = (i, insert_cost)
        
        C_Best_Exchange = [(None, INF)] * cust_len
        for i in range(1, cust_len):
            for j in range(1, cust_len):
                if(exchange_info[i][j] == None):
                    continue
                elif(exchange_info[i][j] < C_Best_Exchange[i][1]):
                    C_Best_Exchange[i] = (j, exchange_info[i][j])
        self.exchangeNodes = C_Best_Exchange

        R_Best_Exchange = [(None, INF)] * route_cnt
        for i in range(route_cnt):
            for pos, nodeid in self.routes[i].traversing():
                if(C_Best_Exchange[nodeid][0] == None):
                    continue
                elif(C_Best_Exchange[nodeid][1] < R_Best_Exchange[i][1]):
                    R_Best_Exchange[i] = (nodeid, C_Best_Exchange[nodeid][1])
        
        self.movePool = list()
        for i in range(1, cust_len):
            if(C_Best_Insert[i][0] != None):
                self.movePool.append(Operation("CBI", i, C_Best_Insert[i]))
            if(C_Best_Exchange[i][0] != None):
                self.movePool.append(Operation("CBE", i, C_Best_Exchange[i]))
        for i in range(route_cnt):
            if(R_Best_Insert[i][0] != None):
                self.movePool.append(Operation("RBI", i, R_Best_Insert[i]))
            if(R_Best_Exchange[i][0] != None):
                self.movePool.append(Operation("RBE", i, R_Best_Exchange[i]))
    
    def exchange_operation(self, nodeid_i, nodeid_j):
        info_i, info_j = self.custInfo[nodeid_i], self.custInfo[nodeid_j]
        """
        if(info_i[0] > info_j[0]):
            nodeid_i, nodeid_j = nodeid_j, nodeid_i
            info_i, info_j = info_j, info_i"""
        node_i, node_j = self.custAgents[nodeid_i], self.custAgents[nodeid_j]
        route_i = self.routes[self.originBelong[nodeid_i]]
        route_j = self.routes[self.originBelong[nodeid_j]]
        """
        if(route_i is route_j and info_i[0] + 1 == info_j[0]):
            return False"""
        if(not route_i.check_before_remove(node_i, info_i)):
            return False
        if(not route_j.check_before_remove(node_j, info_j)):
            return False
        
        new_info_j = (info_i[0], route_i.check_can_replace(node_i, node_j, info_i[0]))
        new_info_i = (info_j[0], route_j.check_can_replace(node_j, node_i, info_j[0]))
        if(new_info_i[1] == None or new_info_j[1] == None):
            return False
        
        route_j.remove(node_j, info_j)
        route_i.remove(node_i, info_i)
        route_i.insert(node_j, new_info_j)
        route_j.insert(node_i, new_info_i)
        self.tot_dist += info_i[1] + info_j[1] + new_info_i[1] + new_info_j[1]
        return True

    def insert_operation(self, nodeid, routeid):
        info = self.custInfo[nodeid]
        new_info = self.insertInfo[nodeid][routeid]
        node = self.custAgents[nodeid]
        route = self.routes[self.originBelong[nodeid]]
        goal_route = self.routes[routeid]
        if(not route.check_before_remove(node, info)):
            return False

        if(not goal_route.check_before_insert(node, new_info)):
            return False
        
        route.remove(node, info)
        goal_route.insert(node, new_info)
        self.tot_dist += info[1] + new_info[1]
        return True
        
    def p_best_move_selection(self):
        self.movePool.sort(key = lambda opt : opt.cost)
        for opt in self.movePool:
            if(opt.cost >= 0):
                break
            if(opt.op_type == "RBE"):
                opt.id = opt.goal
                opt.goal, opt.cost = self.exchangeNodes[opt.id]
                opt.type = "CBE"
            if(opt.op_type == "CBE"):
                self.exchange_operation(opt.id, opt.goal)
            if(opt.op_type == "RBI"):
                opt.id, opt.goal = opt.goal, opt.id
                opt.type = "CBI"
            if(opt.op_type == "CBI"):
                self.insert_operation(opt.id, opt.goal)
    
    def p_route_optimization(self):
        for route in self.routes:
            self.tot_dist += route.route_optimization()
            