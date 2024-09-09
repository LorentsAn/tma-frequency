from typing import List, Callable

import solara
from solara import Div, Reactive

from tma.multipages.components.graphic_elements.plot_appearance_settings import PlotAppearanceSettings
from tma.multipages.components.visual_editor.plot_settings_values import markers_styles, colors


@solara.component
def ColorBox(on_color_click: Callable, label: str = None):
    is_color_selection_panel_open, set_color_selection_panel_open = solara.use_state(False)
    chosen_color, set_chosen_color = solara.use_state(markers_styles[0])

    def render_color_box(color):
        return solara.Button(
            style={
                "background": color,
                "flex-grow": "1",
                "flex-shrink": "1",
                "border": "none",
                "margin-bottom": "10px",
                "margin-right": "5px",
                "border-radius": "0"
            },
            on_click=lambda: on_color_choose(color)
        )

    def on_color_choose(color):
        set_chosen_color(color)
        on_color_click(color)

    def close_color_selection_panel():
        set_color_selection_panel_open(False)

    def open_color_selection_panel():
        set_color_selection_panel_open(True)

    with solara.Card(
        style={"display": "flex", "align-items": "center"},
    ):
        solara.Div(
            children=[
                solara.Text(
                    label if label is not None else "Color Choose",
                    style={
                        "flex": "1",
                        "font-size": "16px",
                        "font-weight": "bold",
                    },
                ),
                solara.IconButton(
                    icon_name="mdi-menu-up" if is_color_selection_panel_open else "mdi-menu-down",
                    style={
                        "font-size": "12px",
                        "margin-left": "auto",
                    },
                    on_click=close_color_selection_panel if is_color_selection_panel_open else open_color_selection_panel,
                ),
            ],
            style={"display": "flex", "align-items": "center"},
        )
        if is_color_selection_panel_open:
            Div([
                Div([
                    render_color_box(color) for color in pallet[:-1]
                ], style={"display": "static", "justify-content": "space-between", 'margin-bottom': '10px',
                          "border-bottom": "2px solid #D3D3D3"}) for pallet in colors
            ])
