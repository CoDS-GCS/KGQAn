from traitlets.traitlets import Long
import matplotlib.pyplot as plt
import numpy as np
from extract_values import read_values_from_file

plt.rcParams['pdf.fonttype'] = 42


def autolabel(rects):
  for rect in rects:
    h = rect.get_height()
    ax.text(rect.get_x() + rect.get_width() / 2, h, float(h), ha='center', verticalalignment='bottom',
            fontsize=size)


def get_linking_values():
    result = list()
    benchmark_evaluation = read_values_from_file()
    entity_linking = benchmark_evaluation['Entity Linking']
    entity_values = [round(value, 1) for value in entity_linking]
    relation_linking = benchmark_evaluation['Relation Linking']
    relation_values = [round(value, 1)for value in relation_linking]

    result.extend(entity_values)
    result.extend(relation_values)
    return result


def get_lcquad_F1():
    benchmark_evaluation = read_values_from_file()
    lcquad = benchmark_evaluation['LCQUAD']
    return lcquad[2]

labels = ["Precision", "Recall", "F1 Major", "Precision", "Recall", "F1 Major"]
size = 16
GAnswer = [19.7, 20.0, 19.5, 8.1, 8.2, 7.8]
EDGQA = [73.8, 68.7, 71.2, 59.4, 53.9, 56.6]
# KGQAn = [59.9, 50.5, 53.7, 7.3, 41.0, 10.9]
KGQAn = get_linking_values()

x = np.arange(len(labels))  # the label locations
width = 0.28  # the width of the bars

fig, ax = plt.subplots(figsize=(9, 7))

rects1 = ax.bar(x - 0.28, GAnswer, color='steelblue', edgecolor='black', width=width, label='gAnswer')
rects2 = ax.bar(x, EDGQA, color='coral', edgecolor='black', width=width, label='EDGQA')
rects3 = ax.bar(x + 0.28, KGQAn, edgecolor='black', color='tab:green', width=width, label='KGQAn')

plt.axhline(y=8.18, color='steelblue')
plt.axhline(y=53.10, color='coral')
kgqan_line = get_lcquad_F1()
plt.axhline(y=kgqan_line, color='tab:green')


autolabel(rects1)
autolabel(rects2)
autolabel(rects3)
ax.set_ylabel('Score (out of 100)', fontsize=size)
ax.set_axisbelow(True)
ax.grid(color='gray', linestyle='dashed', axis='y')

y_ticks = [0, 10, 20, 30, 40, 50, 60, 70]
ax.set_yticklabels(y_ticks, rotation=0, fontsize=size)

ax.set_xticks(x)
ax.set_xticklabels(("Precision", "Recall", "F1", "Precision", "Recall", "F1"), fontsize=size)
fig.tight_layout()
ax.legend(fontsize=15)

ax.set_xlabel('Entity Linking                                                 Relation Linking', labelpad=10.,
              fontsize=size)

plt.subplots_adjust(left=0.2, bottom=0.2, right=1.35)
plt.savefig('linkingComparison.pdf', bbox_inches='tight')
