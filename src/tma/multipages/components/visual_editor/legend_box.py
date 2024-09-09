from typing import List

import solara
from solara import Reactive

from tma.multipages.components.graphic_elements.plot_appearance_settings import PlotAppearanceSettings
from tma.multipages.components.visual_editor.plot_settings_values import legend_positions


@solara.component
def LegendBox(config: Reactive[List[PlotAppearanceSettings]], layout, plot_index: int, is_cooling_curve: bool,
              trigger_update):
    legend_text = solara.use_reactive(None)
    show_in_legend = solara.use_reactive(True)
    legend_position = solara.use_reactive(legend_positions[1])
    legend_font_size = solara.use_reactive(12)
    xaxis_title = solara.use_reactive("X Axis")
    yaxis_title = solara.use_reactive("Y Axis")

    def on_legend_text_change(text):
        legend_text.set(text)
        update_settings()

    def on_show_in_legend_change(show):
        show_in_legend.set(show)
        update_settings()

    def on_legend_position_choose(position):
        legend_position.set(position)
        update_layout()

    def on_legend_font_size_change(size):
        legend_font_size.set(size)
        update_layout()

    def update_settings():
        settings = {
            'legend_text': legend_text.value,
            'show_in_legend': show_in_legend.value
        }

        if is_cooling_curve:
            config.value[plot_index].update_cooling_settings(**settings)
        else:
            config.value[plot_index].update_heating_settings(**settings)

        config.value = list(config.value)
        trigger_update()

    def update_layout():
        layout.value.update(legend_position=legend_position.value)
        trigger_update()

        layout.value.update(
            legend_position=legend_position.value,
            xaxis_title=xaxis_title.value,
            yaxis_title=yaxis_title.value,
            legend_font_size=legend_font_size.value
        )
        trigger_update()  # Trigger re-rendering

    with solara.Column():
        solara.InputText(label="Legend text", value=legend_text, on_value=on_legend_text_change)
        solara.Checkbox(label="Show curve in legend", value=show_in_legend, on_value=on_show_in_legend_change)
        solara.SliderInt("Font size", value=legend_font_size, min=8, max=24, on_value=on_legend_font_size_change)
        solara.Select(label='Legend position', values=legend_positions, value=legend_position,
                      on_value=on_legend_position_choose)
