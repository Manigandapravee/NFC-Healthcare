from matplotlib import pyplot as plt
import numpy as np

# Data for Sprint 2 (adjusted as per user request)
categories = ['Sprint 2']
committed = [4]   # 4 user stories committed
completed = [3.6] # 90% completed (90% of 4 = 3.6)

x = np.arange(len(categories))  # the label locations
width = 0.35  # width of the bars

# Create figure and axis
fig, ax = plt.subplots(figsize=(8, 6))

# New color scheme
bars1 = ax.bar(x - width/2, committed, width, label='Committed', color='darkgreen')
bars2 = ax.bar(x + width/2, completed, width, label='Completed', color='orange')

# Labels, Title, and Custom x-axis tick labels
ax.set_ylabel('Number of User Stories')
ax.set_title('Committed vs Completed User Stories (Sprint 2)')
ax.set_xticks(x)
ax.set_xticklabels(categories)
ax.legend()

# Attach a label on top of each bar
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.1f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')

# Save the figure
plt.tight_layout()
plt.savefig('/mnt/data/sprint2_committed_vs_completed.jpg')
plt.show()

