# daaf-plot

[![PyPI version](https://badge.fury.io/py/daaf-plot.svg)](https://badge.fury.io/py/daaf-plot)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

`daaf-plot` is a python toolbox to make interactive plot in python notebooks.

## Installation

Install using `pip`:

    $ pip install daaf-plot

## Usage

The primary goal of the present toolbox is to help the creation of interactive plots.
Nevertheless, it also provides a function to open a `matplotlib` figure from a given list
of settings (number of rows and columns, padding, etc.) as well as some stylistic options
which can be used outside python notebooks.

### Interactive plots

To make an interactive plot, you need:
1. to enable the `%matplotlib widget` magic in a notebook;
2. an `xarray.DataArray` containing the data to plot.

Import `InteractiveLinePlot` or `InteractivePColorMesh` from `daaf_plot.figure`, instantiate with:

    >>> fig = InteractiveLinePlot(
    ...     data_array,
    ...     x_dim='the_x_dim',
    ...     line_dim='the_line_dim',
    ...     facet_dim=...,
    ...     open_figure_kwargs=dict(...),
    ... )

for a line plot and with:

    >>> fig = InteractivePColorMesh(
    ...     data_array,
    ...     x_dim='the_x_dim',
    ...     y_dim='the_y_dim',
    ...     facet_dim=...
    ...     open_figure_kwargs=dict(...),
    ... )

for a pcolormesh. This creates an abstract figure object, which you can then open using:

    >>> fig.interactive_show()

Have at look at the examples in the `examples/` repository!

### Open a matplotlib figure

The `daaf_plot.geometry.open_figure()` function can be used to open a `matplotlib` figure,
even outside python notebooks.

### Stylistic options

Some `matplotlib` stylistic options are provided when importing `daaf_plot.style`:
- scale `linlogp`;
- color map `deep` (from `seaborn`) and its reversed counterpart;
- a unified function `daaf_plot.style.set_font_size()` to set font size in figures;
- ...

In addition, my custom style sheet is stored in `src/daaf_plot/style/laptop.mplstyle`
and can be used as follows:

    >>> import matplotlib.pyplot as plt
    >>> plt.style.use('daaf_plot.style.laptop')

## Todo-list

- write docstrings
- write documentation
- add type hints
