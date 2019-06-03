from tool import inputEdge, inputNode, sortNode
from agent import PlannerAgent, CustomerAgent, RouteAgent
from agent.constants import unload_tm

if __name__ == "__main__":
    edges = inputEdge.initEdges(r'.\tool\input_distance-time.txt')
    centNodes, custNodes, statNodes = inputNode.initNodes(r'.\tool\input_node.xlsx')
    
    sortNode.sort_nodes(centNodes[0], custNodes)
    custAgents = [CustomerAgent(nd) for nd in custNodes]
    newRoute = lambda : RouteAgent(edges)
    
    planner = PlannerAgent(centNodes[0], custAgents, newRoute)
    planner.get_initial_solution()
    planner.check_solution()
