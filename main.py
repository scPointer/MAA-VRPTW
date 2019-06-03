from tool import inputEdge, inputNode
from agent import PlannerAgent, CustomerAgent, RouteAgent
from agent.constants import unload_tm
from math import atan2

def sort_nodes(nodes, x0, y0):
    nodes.sort(key = lambda nd : atan2(nd.y - y0, nd.x - x0))

if __name__ == "__main__":
    edges = inputEdge.initEdges(r'.\tool\input_distance-time.txt')
    centNodes, custNodes, statNodes = inputNode.initNodes(r'.\tool\input_node.xlsx')
    
    sort_nodes(custNodes, centNodes[0].x, centNodes[0].y)
    custAgents = [CustomerAgent(nd) for nd in custNodes]
    newRoute = lambda : RouteAgent(edges)
    
    planner = PlannerAgent(centNodes[0], custAgents, newRoute)
    planner.get_initial_solution()
    planner.check_solution()
