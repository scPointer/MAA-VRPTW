import sys
sys.path.append('../')
from tool.inputNode import CustomerNode

class CustomerAgent(CustomerNode):
    belong_to = None
    served_tm = None
    def __init__(self, d):
        CustomerNode.__init__(self, d.id, d.x, d.y, d.weight, d.volume, d.first_tm, d.last_tm)
    
    def set_cond(self, belong_to, served_tm):
        self.belong_to, self.served_tm = belong_to, served_tm
