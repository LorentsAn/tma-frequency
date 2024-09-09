import plotly.express as px

from tma.multipages.components.visual_editor.markers_symbol import get_markers_names, get_markers_style

colors = [
    px.colors.cyclical.HSV,
    px.colors.cyclical.mrybm,
    px.colors.cyclical.Phase,
    px.colors.sequential.gray
]

legend_positions = ['top-left', 'top-right', 'bottom-left', 'bottom-right', 'inside', 'outside', 'outside-right',
                    'outside-left']
modes_with_markers = ['lines+markers', 'markers']

markers = ['none'] + get_markers_names()
markers_styles = get_markers_style()
