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

    for nd in reversed(custAgents):
        insert_pos, extra_cost = None, None
        for route in routes:
            insert_pos, extra_cost = route.find_insert_pos(nd)
            if(insert_pos != None):
                route.insert(nd, (insert_pos, extra_cost))
                break
        if(insert_pos == None):
            routes.append(RouteAgent(edges))
            routes[-1].insert(nd, routes[-1].find_insert_pos(nd))
            
    print("route counts", len(routes))
    print("first route")
    routes[0].print()
    count = 0
    for r in routes:
        count += len(r.cList) - 2
    print(count)
    #for r in routes:
    #    print(len(r.cList), r.volume, r.weight)