from math import atan2
from tool.inputNode import Nodes

class sortNode:
    def __init__(self, center):
        self.x0 = center.x
        self.y0 = center.y

    def get_angle(self, node):
        return atan2(node.y - self.y0, node.x - self.x0)

    def sort(self, custNodes):
        custNodes.sort(key = self.get_angle)

def sort_nodes(center, custNodes):
    sortNode(center).sort(custNodes)
        