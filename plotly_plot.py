import plotly.express as px


def plotly_plot(
    trend_pivot,
    upper_legend: bool = True,
    output_html: str | None = None,
    output_static: str | None = None,
):
    """
    Interactive Plotly line chart showing genre share (%) by year.

    Parameters
    ----------
    trend_pivot : pd.DataFrame
        index = year, columns = genre, values = percent (0-100)
    upper_legend : bool
        Place legend in upper-left corner (mirrors previous behaviour).
    output_html : str | None
        If given, writes an interactive HTML file.
    output_static : str | None
        If given, writes a static PNG/PDF/SVG (needs `kaleido`).
    """
    # convert wide → long so Plotly gets one trace per genre
    df_long = trend_pivot.reset_index(names="year").melt(
        id_vars="year", var_name="genre", value_name="percent"
    )

    fig = px.line(
        df_long,
        x="year",
        y="percent",
        color="genre",
        markers=True,
        title="Genre Trends Over Years",
    )

    # styling parity with the old plot
    fig.update_layout(
        yaxis_title="Percent",
        legend_title_text=None,
        yaxis_range=[trend_pivot.min().min(), trend_pivot.max().max() * 1.2],
    )
    if upper_legend:
        fig.update_layout(legend=dict(y=1.02, x=0, xanchor="left"))

    # optional exports
    if output_html:
        fig.write_html(output_html)
    if output_static:
        fig.write_image(output_static)  # needs kaleido

    fig.show()
    return fig
