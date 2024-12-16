import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px


def xkcd_plot(trend_pivot):
    with plt.xkcd():
        trend_pivot.plot(kind="line", marker="o", title="Genre Trends Over Years")
        plt.legend(loc="upper left", ncol=len(trend_pivot.columns))
        plt.ylim(trend_pivot.min().min(), trend_pivot.max().max() * 1.2)
        plt.show()


def plot_plotly(trend_pivot):
    fig = px.line(
        trend_pivot,
        markers=True,
        template="plotly_dark",
        title="Genre Trends Over Years",
    )
    fig.show()


def plotly_scatter(trend_pivot):
    fig = px.scatter(
        trend_pivot,
        trendline="lowess",
        template="plotly_dark",
        title="Genre Trends Over Years",
    )
    fig.show()


def main():
    trend_pivot = pd.read_csv("trend_pivot.csv", index_col=0)
    # xkcd_plot(trend_pivot)
    # plot_plotly(trend_pivot)
    plotly_scatter(trend_pivot)


if __name__ == "__main__":
    main()
