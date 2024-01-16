# Import Library
from matplotlib import pyplot as plt, font_manager as fm
import pandas as pd
from matplotlib.ticker import FormatStrFormatter
from extract_values import get_response_time_per_benchmark

plt.rcParams['pdf.fonttype'] = 42
fig, ax = plt.subplots(figsize=(9,7)) 
size = 16

# Define Data

def autolabel(rects, textcolor):
  for rect in rects:
    h = rect.get_height()
    ax.text(rect.get_x()+rect.get_width()/2, h, float(round(h,1)),ha='center', c = textcolor,verticalalignment='bottom', fontsize = size)



benchmarks = get_response_time_per_benchmark()
understanding = benchmarks['Question Understanding']
linking = benchmarks['Linking']
execution = benchmarks['Execution']

df = pd.DataFrame(dict(
    #EDGQA
    x1=[0.21,0.17,0.20, 0.23,0.19], #Understanding
    x2=[3.78,6.00,3.80, 8.05,3.24], #Linking 
    x3=[4.89,3.27,3.22, 5.36,2.59], #E&F
    
    #gAnswer
    x4=[0.99, 10.22, 1.17,3.59, 3.19],
    x5=[0.27, 1.45, 0.15, 0.24,0.73],
    x6=[1.94, 4.16, 3.07, 2.01,0.51],

    #KGQAn
    x7=understanding.values,
    x8=linking.values,
    x9=execution.values))
    # x7=[1.69, 2.39, 1.65, 2.22, 1.66],
    # x8=[0.27, 0.16, 0.23, 0.15, 0.45],
    # x9=[0.21, 0.74, 0.16, 0.15, 1.33]))

x_label = [0, 1, 2, 3, 4]
x2_label = [0.25, 1.25, 2.25, 3.25, 4.25]
# Stacked grouped bar chart


#New colors


#Central bar for the legend
c1 = plt.bar(x_label, df.x1+df.x2+df.x3, align='edge', width = 0.25,color='lightgrey', edgecolor='black',label = 'E&F')
c2 = plt.bar(x_label, df.x1+df.x2, align='edge', width= 0.25,color='dimgrey', edgecolor='black', label = 'Linking')
c3 = plt.bar(x_label, df.x1, align='edge', width= 0.25, edgecolor='black', color='black', label = 'Q.U.')

#Actual Central bar
c1 = plt.bar(x_label, df.x1+df.x2+df.x3, align='edge', width = 0.25,color='coral', edgecolor='black')
c2 = plt.bar(x_label, df.x1+df.x2, align='edge', width= 0.25,color='wheat', edgecolor='black')

c3 = plt.bar(x_label, df.x1, align='edge', width= 0.25, edgecolor='black', color='papayawhip')

#Left bar
l1 = plt.bar(x_label, df.x4+df.x5+df.x6, align='edge',width= -0.25, color='steelblue',edgecolor='black')
l2 = plt.bar(x_label, df.x4+df.x5, align='edge',width= -0.25,color='lightsteelblue',edgecolor='black')
l3 = plt.bar(x_label, df.x4, align='edge',width= -0.25,color='lightcyan',edgecolor='black')

#Right bar
r1 = plt.bar(x2_label, df.x7+df.x8+df.x9, align='edge',width= 0.25, color='tab:green',edgecolor='black')
r2= plt.bar(x2_label, df.x7+df.x8, align='edge',width= 0.25,color='chartreuse',edgecolor='black')
r3 = plt.bar(x2_label, df.x7, align='edge',width= 0.25,color='lightgreen',edgecolor='black')





autolabel(c1,'black')
autolabel(l1,'black')
autolabel(r1,'black')

ax.set_axisbelow(True)
ax.grid(color='gray', linestyle='dashed', axis = 'y')

y_ticks=[0,2,4,6, 8,10, 12, 14, 16]
ax.set_yticklabels(y_ticks, rotation=0, fontsize= size)

ax.set_ylabel('Latency (s)', fontsize = size)

x_fnames = [-0.13, 0.13, 0.35,   0.85,1.13,1.35,      1.85,2.13,2.35,   2.85,3.13,3.35,   3.85,4.13,4.35]
ax.set_xticks(x_fnames)
ax.set_xticklabels(("G", "E", "K","G", "E", "K","G", "E", "K","G", "E", "K","G", "E", "K"), fontsize = size)

ax.set_xlabel('QALD-9          LC-QuAD 1.0                  YAGO                   DBLP                     MAG', labelpad=10., fontsize = size)
# # Show
ax.legend(fontsize = 15)
fig.tight_layout()

plt.subplots_adjust(left=0.2, bottom=0.2, right=1.35)
plt.savefig('stepTiming.pdf', bbox_inches = 'tight')  