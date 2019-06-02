import xlrd
from datetime import date,datetime
import numpy as np
# from pandas import Series, DataFrame
import pandas as pd
import datetime
from ..tool import lnlagen
import dateutil
from dateutil import parser

df1 = pd.DataFrame(pd.read_excel('.\input_alldata_fea_0-649998.xlsx'))
df2=pd.DataFrame(pd.read_excel('.\input_alldata_fea_649999-end.xlsx'))
df=df1.append(df2)
df=df.set_index("ID", drop=False)   #读入数据

#dffea = df[~df['feasibility'].isin([-1])]
'''file_handle=open('.\handled_data.txt','w')
print(dffea,file=file_handle)
file_handle.close()'''   #测试已经删去



ini = open('.\initial_solution.txt','w')
sys.stdout = ini

n = 1000
sorted_angle = lnlagen.sortedlistgen()  # sorted_angle 是一个已经把notes按照与极轴角度（0,2pai）之间关系进行排序的list
for k in range(n):  # 以下是从极轴开始扫描
    if (k == n):    # 扫描到最后一个数据时，直接返回出发点0并结束
        print(sorted_angle[k])
        print(",0")
        break   

    if sorted_angle[k] > sorted_angle[k+1]:
            id = 1100 * sorted_angle[k] + sorted_angle[k+1] - 1
    elif sorted_angle[k] < sorted_angle[k+1]:
        id = 1100 * sorted_angle[k] + sorted_angle[k+1] # 见张嘉惠与刘相廷对于id的定义方法

    if df.loc['id','feasibility'] == 0: # 如果这条边是可行的，在当前行记录该node，并继续扫描下一个数据
        print(sorted_angle[k],",")  
    elif df.loc['id','feasibility'] == -1: # 如果这条边是不可行的，在当前行记录该node，换行，新开一条路径并继续扫描下一个数据
         print(sorted_angle[k],",0")
         print("/n")

    
