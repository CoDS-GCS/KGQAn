from matplotlib import rcParams
import matplotlib.pyplot as plt
import pandas as pd

plt.rcParams['pdf.fonttype'] = 42

fig, ax = plt.subplots(figsize=(9,7)) 
size = 16
# Define Data

df = pd.DataFrame(dict(
    #EDGQA
    x1=[88,57,92, 96], #FAILED
    x2=[44,33,49,57], #QU FAILED
    
    #gAnswer
    x3=[128,65,98, 100],
    x4=[54, 28,83, 90],
    
    #KGQAn
    x5=[88, 32, 46, 47],
    x6=[36, 8, 10, 4]))


x_label = [0, 1, 2, 3]
x2_label = [0.2, 1.2, 2.2,3.2]
x_finalnames = [0.1, 1.1, 2.1,3.1]
# Stacked grouped bar chart

#Central bar
c = plt.bar(x_label, df.x1, align='edge', width= 0.2,color='gainsboro', edgecolor='black',label = 'Failed due to other reasons')
c1 = plt.bar(x_label, df.x2, align='edge', width= 0.2,color='coral', edgecolor='black')
c2 = plt.bar(x_label, df.x1-df.x2,bottom = df.x2, align='edge', width= 0.2,color='grey', edgecolor='black', label = 'Failed due to Q.U.')
c2 = plt.bar(x_label, df.x1-df.x2,bottom = df.x2, align='edge', width= 0.2,color='wheat', edgecolor='black')

#Left bar
l = plt.bar(x_label, df.x3, align='edge',width= -0.2,color='grey',edgecolor='black')
l1 = plt.bar(x_label, df.x4, align='edge',width= -0.2,color='steelblue',edgecolor='black')
l2 = plt.bar(x_label, df.x3-df.x4, bottom = df.x4, align='edge',width= -0.2,color='lightsteelblue',edgecolor='black')

#Right bar
r = plt.bar(x2_label,df.x5, align='edge',width= 0.2,color='grey',edgecolor='black')
r1 = plt.bar(x2_label,df.x6, align='edge',width= 0.2,color='tab:green',edgecolor='black')
r2 = plt.bar(x2_label, df.x5-df.x6, bottom = df.x5-(df.x5-df.x6), align='edge',width= 0.2,color='lightgreen',edgecolor='black')

def autolabel(rects, textcolor, weight):
  for rect in rects:
    h = rect.get_height()
    ax.text(rect.get_x()+rect.get_width()/2, h, int(h), ha='center', verticalalignment='bottom', fontsize = size, color = textcolor, fontweight = weight)

autolabel(c1, "black", "medium")
autolabel(l1, "black", "medium")
autolabel(r1, "black", "medium")

autolabel(c, "black", "medium")
autolabel(l, "black", "medium")
autolabel(r, "black", "medium")

ax.set_axisbelow(True)
ax.grid(color='gray', linestyle='dashed', axis = 'y')


ax.set_ylabel('Number of Failing Questions', fontsize = size)

x_fnames = [-0.1, 0.1, 0.3,   0.9,1.1,1.3,      1.9,2.1,2.3,    2.9,3.1,3.3]

y_ticks=[0,20,40,60, 80,100, 120]
ax.set_yticklabels(y_ticks, rotation=0, fontsize= size)

ax.set_xticks(x_fnames)
ax.set_xticklabels(("G", "E", "K","G", "E", "K","G", "E", "K", "G", "E", "K"), fontsize = size)
  
ax.set_xlabel('QALD-9                            YAGO                             DBLP                         MAG', labelpad=10., fontsize = size)
ax.legend(fontsize = 15)
fig.tight_layout()

plt.subplots_adjust(left=0.2, bottom=0.2, right=1.35)
plt.savefig('failedQuestions.pdf', bbox_inches = 'tight')  