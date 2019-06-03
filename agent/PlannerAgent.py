import sys
sys.path.append('../')
from tool.inputNode import CenterNode
from agent.constants import unload_tm

class PlannerAgent(CenterNode):
    custAgents = None
    routes = None
    cust_counts = None
    newRoute = None
    def __init__(self, d, custAgents, newRoute):
        CenterNode.__init__(self, d.id, d.x, d.y)
        self.custAgents = custAgents
        self.cust_counts = len(self.custAgents)
        self.newRoute = newRoute
        self.routes = [self.newRoute()]
    
    def get_initial_solution(self):
        for nd in reversed(self.custAgents):
            insert_pos, extra_cost = None, None
            for route in self.routes:
                insert_pos, extra_cost = route.find_insert_pos(nd)
                if(insert_pos != None):
                    route.insert(nd, (insert_pos, extra_cost))
                    break
            if(insert_pos == None):
                self.routes.append(self.newRoute())
                self.routes[-1].insert(nd, self.routes[-1].find_insert_pos(nd))
        
        #afterwork
        #to conform that custAgents[i].id == i
        self.custAgents.sort(key = lambda nd: nd.id)
        self.custAgents.insert(0, None)
    
    def check_solution(self):
        print("route counts", len(self.routes))
        print("first route")
        self.routes[0].print()
        count = 0
        for r in self.routes:
            count += len(r.cList) - 2
        print(count)
    #    for r in routes:
    #        print(len(r.cList), r.volume, r.weight)
        for i in range(20):
            cust = self.custAgents[i]
            r0 = cust.belong_to
            info = (cust.id, cust.served_tm, cust.served_tm + unload_tm)
            print(info)
            print(r0.cList)
            print(r0.cList.index(info))
            print(r0.check_remove_cost(r0.cList.index(info)))
    
    def customer_and_route_operations(self):
        cust_len = self.cust_counts + 1
        route_cnt = len(self.routes)
        remove_info = [(None, None)] * cust_len
        for route in self.routes:
            for pos, nodeid in route.traversing():
                remove_info[nodeid] = (pos, route.check_remove_cost(pos))
        
        belong_route = [None] * cust_len
        insert_info = [[(None, None)] * route_cnt for x in range(cust_len)]
        for i in range(1, cust_len):
            for j in range(route_cnt):
                node = self.custAgents[i]
                if(route is not node.belong_to):
                    insert_info[i][j]=self.routes[j].find_insert_pos(node)
                else:
                    belong_route[i] = j
        
        exchange_info = [[None] * (cust_len) for x in range(cust_len)]
        for i in range(1, cust_len):
            for j in range(1, cust_len):
                pos_i, cost_i = insert_info[i][belong_route[j]]
                pos_j, cost_j = insert_info[j][belong_route[i]]
                if(pos_i != None and pos_j != None):
                    exchange_info[i][j] = cost_i + cost_j + remove_info[i][1] + remove_info[j][1]

        C_Best_Insert = [(None, None)] * cust_len
        R_Best_Insert = [(None, None)] * route_cnt
        for i in range(1, cust_len):
            for j in range(route_cnt):
                insert_cost = insert_info[i][j][1] + remove_info[i][1]
                if(insert_cost < C_Best_Insert[i][1]):
                    C_Best_Insert[i] = (j, insert_cost)
                if(insert_cost < R_Best_Insert[j][1]):
                    R_Best_Insert[j] = (i, insert_cost)
        
        C_Best_Exchange = [(None, None)] * cust_len
        for i in range(1, cust_len):
            for j in range(1, cust_len):
                if(exchange_info[i][j] < C_Best_Exchange[i][1]):
                    C_Best_Exchange[i] = (j, exchange_info[i][j])
        
        R_Best_Exchange = [(None, None)] * route_cnt
        for i in range(route_cnt):
            for pos, nodeid in self.routes[i].traversing():
                if(C_Best_Exchange[nodeid] < R_Best_Exchange[i][1]):
                    R_Best_Exchange[i] = (nodeid, C_Best_Exchange[nodeid])