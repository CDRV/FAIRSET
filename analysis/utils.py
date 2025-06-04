from typing import Dict

import matplotlib.pyplot as plt
import numpy as np

from analysis.data.datatypes import Age, DiscreteFactorEnum, Sex, Skintone


def display_demog_box_plot(data: Dict[DiscreteFactorEnum, np.ndarray], demographic_factor: DiscreteFactorEnum):
    factors = list(data.keys())
    values = [data[f] for f in factors]
    colors = [f.color for f in factors]
    labels = [f.figure_label for f in factors]

    fig, ax = plt.subplots(figsize=(1.5 * len(factors), 6))

    bp = ax.boxplot(
        values,
        patch_artist=True,
        boxprops={"linestyle": "-", "linewidth": 2},
        medianprops={"linestyle": "-", "linewidth": 2, "color": "black"},
        showmeans=True,
        meanline=True,
        meanprops={"linestyle": "--", "linewidth": 2, "color": "black"},
        showfliers=False,
    )

    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)

    for i, vals in enumerate(values):
        mean = np.mean(vals)
        median = np.median(vals)
        ax.text(i + 1, mean, f"Mean: {mean:.2f}", ha="center", va="bottom", fontsize=9, color="black")
        ax.text(i + 1, median, f"Median: {median:.2f}", ha="center", va="top", fontsize=9, color="black")

    ax.set_xticks(range(1, len(labels) + 1))
    ax.set_xticklabels(labels)
    ax.set_ylabel("Normalized Mean Error (NME)")
    ax.set_title(f"{demographic_factor.get_property_str().capitalize()} Distributions")

    legend_handles = [plt.Line2D([0], [0], color=color, lw=8, label=label) for color, label in zip(colors, labels)]
    ax.legend(handles=legend_handles, title="Legend", loc="upper right")

    plt.tight_layout()
    plt.show()
