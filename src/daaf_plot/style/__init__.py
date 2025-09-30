import matplotlib
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib import scale as mscale

from daaf_plot.scale.linlogp import LinLogPressureScale


def set_font_size(small=8, medium=10, large=12):
    # controls default text sizes
    plt.rc('font', size=small)
    # font size of the axes title
    plt.rc('axes', titlesize=small)
    # font size of the x and y labels
    plt.rc('axes', labelsize=medium)
    # font size of the tick labels
    plt.rc('xtick', labelsize=small)
    # font size of the tick labels
    plt.rc('ytick', labelsize=small)
    # legend font size
    plt.rc('legend', fontsize=small)
    # font size of the figure title
    plt.rc('figure', titlesize=large)


def hex_to_rgb_colour(hex_colour):
    h = hex_colour.lstrip('#')
    c = [int(h[i : i + 2], 16) / 255 for i in (0, 2, 4)] + [1]
    return tuple(c)


def get_deep_colors():
    return [
        hex_to_rgb_colour(h)
        for h in [
            '4C72B0',
            'DD8452',
            '55A868',
            'C44E52',
            '8172B3',
            '937860',
            'DA8BC3',
            '8C8C8C',
            'CCB974',
            '64B5CD',
        ]
    ]


# register custom scales
mscale.register_scale(LinLogPressureScale)


# standard list of scales
scale_list = [
    'linear',
    'log',
    'symlog',
    'asinh',
    'logit',
    'linlogp',
]


# register 'deep' cmap
cmap = mcolors.ListedColormap(get_deep_colors(), name='deep')
matplotlib.colormaps.register(cmap)
matplotlib.colormaps.register(cmap.reversed())


# standard list of continuous cmaps
continuous_cmap_list = [
    'viridis',
    'RdBu',
    'twilight',
    'twilight_shifted',
]


# standard list of discrete cmaps
discrete_cmap_list = continuous_cmap_list + [
    'deep',
    'Paired',
]
