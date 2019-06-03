import sys
sys.path.append('../')
from tool.inputNode import CenterNode
from agent.constants import unload_tm

class PlannerAgent(CenterNode):
    custAgents = None
    routes = None
    custCounts = None
    newRoute = None
    def __init__(self, d, custAgents, newRoute):
        CenterNode.__init__(self, d.id, d.x, d.y)
        self.custAgents = custAgents
        self.custCounts = len(self.custAgents)
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
            print(r0.check_remove_cost(cust, r0.cList.index(info)))