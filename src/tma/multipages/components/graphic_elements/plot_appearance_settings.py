class CurveSettings:
    def __init__(self, color='red', line_width=2, line_dash='solid', marker_symbol='circle', marker_size=6,
                 mode='lines',
                 legend_text=None, show_in_legend=True, legend_position='outside-right'):
        self.color = color
        self.line_width = line_width
        self.line_dash = line_dash
        self.marker_symbol = marker_symbol
        self.marker_size = marker_size
        self.mode = mode
        self.legend_text = legend_text
        self.show_in_legend = show_in_legend
        self.legend_position = legend_position

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def to_dict(self, x, y, name):
        legend_name = name if self.legend_text is None else self.legend_text
        return {
            'x': x,
            'y': y,
            'mode': self.mode,
            'name': legend_name if self.show_in_legend else None,
            'line': {'color': self.color, 'width': self.line_width, 'dash': self.line_dash},
            'marker': {'symbol': self.marker_symbol, 'size': self.marker_size},
            'showlegend': self.show_in_legend
        }


class PlotAppearanceSettings:
    def __init__(self, legend_text: str = None):
        heating_text = f'{legend_text} Heating' if legend_text else None
        cooling_text = f'{legend_text} Cooling' if legend_text else None
        self.heating_settings = CurveSettings(color='red', legend_text=heating_text)
        self.cooling_settings = CurveSettings(color='#0072B2', legend_text=cooling_text)

    def update_heating_settings(self, **kwargs):
        self.heating_settings.update(**kwargs)

    def update_cooling_settings(self, **kwargs):
        self.cooling_settings.update(**kwargs)
