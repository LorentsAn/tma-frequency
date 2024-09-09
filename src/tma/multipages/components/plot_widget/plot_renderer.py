import solara
import plotly.graph_objects as go

from tma.multipages.components.graphic_elements.graphic_element import GraphicElement


@solara.component
def PlotRenderer(data: [[go.Scatter]], graphic_elements: [GraphicElement], layout=None, on_click=None,
                 add_axes_lines=True):
    fig = go.Figure()

    for plot in data:
        for curve in plot:
            fig.add_trace(curve)

    fig.update_layout(layout)
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgb(224, 224, 223)')
    fig.update_xaxes(minor=dict(ticklen=4, tickcolor="black"))

    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgb(224, 224, 223)')
    fig.update_yaxes(minor=dict(ticklen=4, tickcolor="black"))

    fig.update_xaxes(showline=True, linewidth=1, linecolor='black')
    fig.update_yaxes(showline=True, linewidth=1, linecolor='black')

    for element in graphic_elements:
        fig = element.draw(fig)

    if add_axes_lines:
        fig.add_hline(y=0, line_dash="dash", line_color="rgb(224, 224, 223)", line_width=1)
        fig.add_vline(x=0, line_dash="dash", line_color="rgb(224, 224, 223)", line_width=1)

    solara.FigurePlotly(
        fig,
        on_click=on_click,
    )
