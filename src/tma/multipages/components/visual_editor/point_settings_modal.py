import solara

from tma.multipages.components.visual_editor.color_box import ColorBox
from tma.multipages.components.visual_editor.plot_settings_values import markers


@solara.component
def PointSettingsModal(current_point_settings, set_current_point_settings):
    def on_color_click(color):
        set_current_point_settings(
            {**current_point_settings, "color": color})

    def on_border_line_color_click(color):
        set_current_point_settings({**current_point_settings, "marker_line_color": color})

    with solara.Column():
        with solara.Column():
            ColorBox(on_color_click, label='Choose marker color')
            custom_name = current_point_settings.get("custom_name", "")
            solara.InputText(
                label='Marker Name',
                value=(custom_name if custom_name != "" else current_point_settings.get("name", "")),
                on_value=lambda v: set_current_point_settings({**current_point_settings, "custom_name": v}))
            solara.Select(label="Choose marker type", values=markers, value=current_point_settings.get("symbol", ""),
                          on_value=lambda v: set_current_point_settings(
                              {**current_point_settings, "symbol": v}))
            solara.SliderInt(label='Choose marker size', min=4, max=20, value=current_point_settings.get("size", 8),
                             on_value=lambda v: set_current_point_settings(
                                 {**current_point_settings, "size": v}))
            ColorBox(on_border_line_color_click, label='Choose borderline color')
            solara.SliderInt(label="Marker Line Width",
                             value=current_point_settings.get("marker_line_width", 0), min=0, max=10,
                             on_value=lambda v: set_current_point_settings(
                                 {**current_point_settings, "marker_line_width": v}))
