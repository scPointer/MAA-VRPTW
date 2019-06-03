from tool import inputEdge, inputNode, sortNode
from agent.agents import CustomerAgent, RouteAgent

if __name__ == "__main__":
    edges = inputEdge.initEdges(r'.\tool\input_distance-time.txt')
    centNodes, custNodes, statNodes = inputNode.initNodes(r'.\tool\input_node.xlsx')
    sortNode.sort_nodes(centNodes[0], custNodes)
    """
    centNodes[0].print_pos()
    for i in range(10):
        custNodes[i].print_pos()
    """
    custAgents = [CustomerAgent(nd) for nd in custNodes]

    routes = [RouteAgent(edges)]
    rnow = routes[0]
    for nd in custAgents:
        insert_pos, extra_cost = rnow.find_insert_pos(nd)
        if(insert_pos == None):
            rnow = RouteAgent(edges)
            routes.append(rnow)
            insert_pos, extra_cost = rnow.find_insert_pos(nd)
        # check-before_insert(x, (insert_pos, extra_cost))
        rnow.insert(nd, (insert_pos, extra_cost))
    print("route counts", len(routes))
    print("first route")
    routes[0].print()
