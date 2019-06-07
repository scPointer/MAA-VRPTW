from tool import inputEdge, inputNode, BestStation
from agent import PlannerAgent, CustomerAgent, RouteAgent
from agent import constants
from math import atan2

calculate_times = 40
edgeFile = r'.\data\input_distance-time.txt'
nodeFile = r'.\data\input_node.xlsx'
initFile = r'.\data\station_choice0.txt'
outputFile = r'.\data\solution6521.txt'

def sort_nodes(nodes, x0, y0):
    nodes.sort(key = lambda nd : atan2(nd.y - y0, nd.x - x0))

def calculate():
    edges = inputEdge.initEdges(edgeFile)
    centNodes, custNodes, statNodes = inputNode.initNodes(nodeFile)
    chargeChoice = BestStation.get_best_station(len(centNodes) + len(custNodes), initFile)

    sort_nodes(custNodes, centNodes[0].x, centNodes[0].y)
    custAgents = [CustomerAgent(nd) for nd in custNodes]
    newRoute = lambda : RouteAgent(edges, centNodes[0], chargeChoice)
    
    planner = PlannerAgent(centNodes[0], custAgents, newRoute)
    planner.get_initial_solution()
    #planner.check_solution()
    #planner.print_solution(r'.\solution.txt')
    for i in range(calculate_times):
        planner.init_movePool()
        planner.p_best_move_selection()
        if (i % 3 == 0):
            planner.p_route_optimization()
        planner.check_solution()
    
    planner.find_charging_station()
    planner.check_solution()
    planner.print_solution(outputFile)

def init_best_station():
    edges = inputEdge.initEdges(edgeFile)
    centNodes, custNodes, statNodes = inputNode.initNodes(nodeFile)
    file = open(initFile, "w")
    BestStation.init_best_station(edges, statNodes, \
        len(centNodes) + len(custNodes), constants.charge_tm, file)
    

if __name__ == "__main__":
    #s = input("init best station for customers(1)/do calculation(0)\n")
    #if(int(s) == 1):
    #    init_best_station()
    #else:
        calculate()
    
