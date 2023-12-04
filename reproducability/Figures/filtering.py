from traitlets.traitlets import Long
import matplotlib.pyplot as plt
import numpy as np
from extract_values import read_values_from_file

plt.rcParams['pdf.fonttype'] = 42


def autolabel(rects):
    for rect in rects:
        h = rect.get_height()
        ax.text(rect.get_x() + rect.get_width() / 2, h, round(h, 1), ha='center', verticalalignment='bottom',
                fontsize=14)


def get_values():
    benchmark_evaluation = read_values_from_file()
    # No filteration
    qald_no_filtering = benchmark_evaluation['QALD-NO-Filtration']
    lcquad_no_filtering = benchmark_evaluation['LCQUAD-NO-Filtration']
    kgqan_no_filtering = list()
    kgqan_no_filtering.extend(qald_no_filtering)
    kgqan_no_filtering.extend(lcquad_no_filtering)

    # Withfilteration
    qald = benchmark_evaluation['QALD']
    lcquad = benchmark_evaluation['LCQUAD']
    kgqan = list()
    kgqan.extend(qald)
    kgqan.extend(lcquad)

    return kgqan_no_filtering, kgqan


labels = ["Precision", "Recall", "F1 Major", "Precision", "Recall", "F1 Major"]
size = 16
# KGQAnwoFiltering = [28.43, 43.14, 34.27, 48.14, 49.73, 48.92]
# KGQAnFiltering = [51.13, 38.72, 44.07, 58.71, 46.11, 51.65]
KGQAnwoFiltering, KGQAnFiltering = get_values()

x = np.arange(len(labels))  # the label locations
width = 0.3  # the width of the bars

fig, ax = plt.subplots(figsize=(9, 7))

rects2 = ax.bar(x, KGQAnwoFiltering, color='lightgreen', edgecolor='black', width=width,
                label='KGQAn without Filtration')
rects3 = ax.bar(x + 0.3, KGQAnFiltering, edgecolor='black', color='tab:green', width=width, label='KGQAn')

# autolabel(rects1)
autolabel(rects2)
autolabel(rects3)
ax.set_ylabel('Score (out of 100)', fontsize=size)

y_ticks = [0, 10, 20, 30, 40, 50, 60]
ax.set_yticklabels(y_ticks, rotation=0, fontsize=size)

ax.set_axisbelow(True)
ax.grid(color='gray', linestyle='dashed', axis='y')

ax.set_xticks(x + 0.125)
ax.set_xticklabels(("Precision", "Recall", "F1", "Precision", "Recall", "F1"), fontsize=size)

fig.tight_layout()

ax.legend(loc='upper left', fontsize=13)
ax.set_xlabel('QALD-9                                                        LC-QuAD 1.0', labelpad=10., fontsize=size)

plt.subplots_adjust(left=0.2, bottom=0.2, right=1.35)
plt.savefig('filteringFigure.pdf', bbox_inches='tight')
