import matplotlib.pyplot as plt


def xkcd_plot(trend_pivot, upper_legend=True):
    with plt.xkcd():
        trend_pivot.plot(kind="line", marker="o", title="Genre Trends Over Years")
        plt.ylabel("Percent")
        if upper_legend:
            plt.legend(loc="upper left", ncol=len(trend_pivot.columns))
            plt.ylim(trend_pivot.min().min(), trend_pivot.max().max() * 1.2)
        plt.show()


def simple_plot(trend_pivot, upper_legend=True):
    trend_pivot.plot(kind="line", marker="o", title="Genre Trends Over Years")
    plt.ylabel("Percent")
    if upper_legend:
        plt.legend(loc="upper left", ncol=len(trend_pivot.columns))
        plt.ylim(trend_pivot.min().min(), trend_pivot.max().max() * 1.2)
    plt.show()
