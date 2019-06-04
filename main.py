from tool import inputEdge, inputNode
from agent import PlannerAgent, CustomerAgent, RouteAgent
from agent.constants import unload_tm
from math import atan2

calculate_times = 50
edgeFile = r'.\tool\input_distance-time.txt'
nodeFile = r'.\tool\input_node.xlsx'
outputFile = r'.\solution0.txt'

def sort_nodes(nodes, x0, y0):
    nodes.sort(key = lambda nd : atan2(nd.y - y0, nd.x - x0))

if __name__ == "__main__":
    edges = inputEdge.initEdges(edgeFile)
    centNodes, custNodes, statNodes = inputNode.initNodes(nodeFile)
    
    sort_nodes(custNodes, centNodes[0].x, centNodes[0].y)
    custAgents = [CustomerAgent(nd) for nd in custNodes]
    newRoute = lambda : RouteAgent(edges)
    
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
        
    planner.print_solution(outputFile)
