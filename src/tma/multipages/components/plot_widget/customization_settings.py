import solara


class CustomizationSettings:
    def __init__(self):
        self.line_style = "solid"
        self.point_shape = "circle"
        self.color_scheme = "#0000FF"
        self.show_legend = True
        self.title_text = 'Thermomagnetic Plot'

    def apply_customizations(self, layout):
        if 'title_text' not in layout or layout.get('title_text') == '':
            updated_layout = {**layout, 'title_text': self.title_text, 'showlegend': self.show_legend,
                              'plot_bgcolor': 'white'}
        else:
            updated_layout = {**layout, 'showlegend': self.show_legend, 'plot_bgcolor': 'white'}

        # updated_config = {
        #     **config,
        #     'line': {'dash': self.line_style},
        #     'marker': {'symbol': self.point_shape, 'color': self.color_scheme},
        #     # 'title_text': self.title_text,
        # }

        return updated_layout
