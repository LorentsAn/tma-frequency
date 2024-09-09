class LayoutSettings:
    def __init__(self, legend_position='outside-right', xaxis_title='X Axis', yaxis_title='Y Axis',
                 legend_font_size=12):
        self.legend_position = legend_position
        self.xaxis_title = xaxis_title
        self.yaxis_title = yaxis_title
        self.legend_font_size = legend_font_size

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def to_dict(self):
        if self.legend_position == 'outside':
            legend_dict = {
                'orientation': 'h',
                'xanchor': 'center',
                'x': 0.5,
                'yanchor': 'top',
                'y': -0.2,
                'font': {'size': self.legend_font_size}
            }
        elif self.legend_position == 'outside-right':
            legend_dict = {
                'xanchor': 'left',
                'x': 1.02,
                'yanchor': 'top',
                'y': 1,
                'font': {'size': self.legend_font_size}
            }
        elif self.legend_position == 'outside-left':
            legend_dict = {
                'xanchor': 'right',
                'x': -0.02,
                'yanchor': 'top',
                'y': 1,
                'font': {'size': self.legend_font_size}
            }
        else:
            x, y, xanchor, yanchor = 1, 1, 'right', 'top'
            if self.legend_position in ['top-left', 'bottom-left']:
                x = 0
                xanchor = 'left'
            if self.legend_position in ['bottom-left', 'bottom-right']:
                y = 0
                yanchor = 'bottom'

            legend_dict = {
                'x': x,
                'y': y,
                'xanchor': xanchor,
                'yanchor': yanchor,
                'font': {'size': self.legend_font_size}
            }

        return {
            'legend': legend_dict,
            'xaxis': {
                'title': self.xaxis_title
            },
            'yaxis': {
                'title': self.yaxis_title
            }
        }
