from typing import List

import solara
from solara import Reactive

from tma.multipages.components.graphic_elements.plot_appearance_settings import PlotAppearanceSettings
from tma.multipages.components.visual_editor.plot_settings_values import markers, markers_styles, modes_with_markers


@solara.component
def MarkerBox(config: Reactive[List[PlotAppearanceSettings]], plot_index: int, is_cooling_curve: bool, trigger_update):
    chosen_marker_name = solara.use_reactive(markers[0])
    displayed_chosen_marker_name = solara.use_reactive(markers[0])
    chosen_marker_style = solara.use_reactive(markers_styles[0])
    chosen_mode = solara.use_reactive(modes_with_markers[0])
    chosen_marker_size = solara.use_reactive(6)

    def on_marker_type_choose(marker_name):
        chosen_marker_name.set(marker_name)
        displayed_chosen_marker_name.set(marker_name)
        chosen_mode.set('lines+markers')
        if marker_name == 'none':
            chosen_mode.set('lines')
        update_settings()

    def on_marker_style_choose(marker_style):
        chosen_marker_style.set(marker_style)
        update_settings()

    def on_mode_choose(mode):
        chosen_mode.set(mode)
        update_settings()

    def on_marker_size_choose(size):
        chosen_marker_size.set(size)
        update_settings()

    def update_settings():
        if chosen_marker_name.value == 'none':
            mode = 'lines'
            marker_symbol = None
            marker_size = None
        else:
            mode = chosen_mode.value
            marker_symbol = chosen_marker_name.value
            if chosen_marker_style.value != '-basic':
                marker_symbol += chosen_marker_style.value
            marker_size = chosen_marker_size.value

        if is_cooling_curve:
            config.value[plot_index].update_cooling_settings(
                mode=mode, marker_symbol=marker_symbol, marker_size=marker_size)
        else:
            config.value[plot_index].update_heating_settings(
                mode=mode, marker_symbol=marker_symbol, marker_size=marker_size)

        config.value = list(config.value)
        trigger_update()  # Trigger re-rendering

    solara.Select(label="Choose marker type", values=markers, value=displayed_chosen_marker_name,
                  on_value=on_marker_type_choose)

    if chosen_marker_name.value != 'none':
        solara.Select(label='Choose marker style', values=markers_styles, value=chosen_marker_style,
                      on_value=on_marker_style_choose)
        solara.Select(label='Choose mode', values=modes_with_markers, value=chosen_mode, on_value=on_mode_choose)
        solara.SliderInt(label='Choose marker size', min=4, max=20, value=chosen_marker_size,
                         on_value=on_marker_size_choose)
