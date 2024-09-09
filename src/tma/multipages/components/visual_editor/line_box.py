from typing import List

import solara
from solara import Div, Reactive

from tma.multipages.components.graphic_elements.plot_appearance_settings import PlotAppearanceSettings


@solara.component
def LineBox(config: Reactive[List[PlotAppearanceSettings]], plot_index: int, is_cooling_curve: bool, trigger_update):
    def render_line_button(style_name, pattern):
        return solara.Button(
            style={
                "border": "1px solid black",
                "background": "white",
                "position": "relative",
                "overflow": "hidden",
                "margin": "5px",
                'align-items': 'center'
            },
            on_click=lambda: on_line_click(style_name),
            children=[
                Div(style={
                    "position": "absolute",
                    "left": 0,
                    "right": 0,
                    "height": "2px",
                    "background": pattern,
                    "border-radius": "1.5px"
                })
            ]
        )

    def on_line_click(line_type):
        set_chosen_line(chosen_line)

        if is_cooling_curve:
            config.value[plot_index].update_cooling_settings(line_dash=line_type)
        else:
            config.value[plot_index].update_heating_settings(line_dash=line_type)
        trigger_update()  # Trigger re-rendering

    def on_line_width_change(width):
        set_line_width(width)
        if is_cooling_curve:
            config.value[plot_index].update_cooling_settings(line_width=width)
        else:
            config.value[plot_index].update_heating_settings(line_width=width)
        trigger_update()  # Trigger re-rendering

    line_styles = {
        "solid": "black",
        "dash": "repeating-linear-gradient(90deg, black 0 5px,#0000 0 7px)",
        "dot": "repeating-linear-gradient(90deg, black 0 2px,#0000 0 7px)",
        "dashdot": "radial-gradient(circle at center,#000 2px,transparent 2px) 5px 50%/20px 5px repeat-x, "
                   "repeating-linear-gradient(to right,#000,#000 10px,transparent 10px,transparent 20px) center/100% 3px",
    }
    chosen_line, set_chosen_line = solara.use_state(line_styles.get('solid'))
    line_width, set_line_width = solara.use_state(2)

    solara.SliderInt(label="Line width", value=line_width, min=1, max=10, on_value=on_line_width_change)
    solara.Div([
        Div([
            render_line_button(style_name, style_pattern) for (style_name, style_pattern) in line_styles.items()
        ], style={"display": "flex", "justify-content": "space-around", "padding": "10px"})
    ])
