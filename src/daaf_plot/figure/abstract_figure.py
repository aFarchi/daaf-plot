import abc
import logging
from itertools import starmap

import matplotlib.pyplot as plt
import pandas as pd

from daaf_plot.geometry import open_figure

logger = logging.getLogger(__name__)


class AbstractFigure(abc.ABC):
    def __init__(
        self,
        da_data,
        *,
        exclude_dims,
        open_figure_kwargs,
        facet_dim,
        flatten_order,
    ):
        self.da_data = da_data
        self.exclude_dims = exclude_dims or []
        self.exclude_dims = list(self.exclude_dims)
        self.open_figure_kwargs = open_figure_kwargs or {}
        self.figure = None
        self.facet_dim = facet_dim
        self.flatten_order = flatten_order
        self.num_blank_axes = 0
        self.is_open = False
        self.parse_facet_dim()

    def parse_facet_dim(self):
        match self.facet_dim:
            case None:
                self.parse_facet_none()
            case str():
                self.parse_facet_str()
            case None, str():
                self.parse_facet_none_str()
            case str(), None:
                self.parse_facet_str_none()
            case str(), str():
                self.parse_facet_str_str()
            case _:
                message = f'incorrect "facet_dim": {self.facet_dim}'
                raise ValueError(message)

    def parse_facet_none(self):
        if self.open_figure_kwargs.get('num_rows', 1) != 1:
            logger.warning('ignoring "num_rows" because "facet_dim" is None')
        if self.open_figure_kwargs.get('num_cols', 1) != 1:
            logger.warning('ignoring "num_cols" because "facet_dim" is None')
        self.open_figure_kwargs |= {'num_rows': 1, 'num_cols': 1}

    def parse_facet_str(self):
        num_facets = len(self.da_data[self.facet_dim])
        if (
            'num_rows' not in self.open_figure_kwargs
            and 'num_cols' not in self.open_figure_kwargs
        ):
            num_rows = 1
            num_cols = num_facets
        else:
            num_rows = self.open_figure_kwargs.get('num_rows', 1)
            num_cols = self.open_figure_kwargs.get('num_cols', 1)
        if num_rows * num_cols < num_facets:
            num_facets = num_rows * num_cols
            logger.warning('cropping facet dim to %s', num_facets)
            self.da_data = self.da_data.isel(**{
                self.facet_dim: slice(None, num_facets),
            })
        elif num_facets < num_rows * num_cols:
            self.num_blank_axes = num_rows * num_cols - num_facets
            logger.warning(
                'too many axes, %s of them will be blank',
                self.num_blank_axes,
            )
        self.open_figure_kwargs |= {'num_rows': num_rows, 'num_cols': num_cols}
        self.exclude_dims.append(self.facet_dim)

    def parse_facet_none_str(self):
        self.facet_dim = self.facet_dim[1]
        num_facets = len(self.da_data[self.facet_dim])
        if self.open_figure_kwargs.get('num_cols', 1) != 1:
            logger.warning('ignoring "num_cols" because "facet_dim[0]" is None')
        num_rows = self.open_figure_kwargs.get('num_rows', num_facets)
        self.open_figure_kwargs |= {'num_rows': num_rows, 'num_cols': 1}
        self.parse_facet_dim()

    def parse_facet_str_none(self):
        self.facet_dim = self.facet_dim[0]
        num_facets = len(self.da_data[self.facet_dim])
        if self.open_figure_kwargs.get('num_rows', 1) != 1:
            logger.warning('ignoring "num_rows" because "facet_dim[1]" is None')
        num_cols = self.open_figure_kwargs.get('num_cols', num_facets)
        self.open_figure_kwargs |= {'num_rows': 1, 'num_cols': num_cols}
        self.parse_facet_dim()

    def parse_facet_str_str(self):
        num_facets_x = len(self.da_data[self.facet_dim[0]])
        num_facets_y = len(self.da_data[self.facet_dim[1]])
        num_rows = self.open_figure_kwargs.get('num_rows', num_facets_y)
        num_cols = self.open_figure_kwargs.get('num_cols', num_facets_x)
        self.exclude_dims.append(self.facet_dim[0])
        self.exclude_dims.append(self.facet_dim[1])
        if num_cols < num_facets_x:
            num_facets_x = num_cols
            logger.warning('cropping x facet dim to %s', num_facets_x)
            self.da_data = self.da_data.isel(**{
                self.facet_dim[0]: slice(None, num_facets_x),
            })
        elif num_facets_x < num_cols:
            num_cols = num_facets_x
            logger.warning('cropping num_cols to %s', num_cols)
        if num_rows < num_facets_y:
            num_facets_y = num_rows
            logger.warning('cropping y facet dim to %s', num_facets_y)
            self.da_data = self.da_data.isel(**{
                self.facet_dim[1]: slice(None, num_facets_y),
            })
        elif num_facets_y < num_rows:
            num_rows = num_facets_y
            logger.warning('cropping num_rows to %s', num_rows)
        if self.flatten_order is not None and self.flatten_order != 'C':
            logger.warning('overwriting flatting order to "C"')
            self.flatten_order = 'C'
        self.open_figure_kwargs |= {'num_rows': num_rows, 'num_cols': num_cols}

    def open_figure(self):
        self.figure = open_figure(**self.open_figure_kwargs)
        self.figure['ylabel_axes'] = self.figure['axes'][:, 0]
        self.figure['axes'] = self.figure['axes'].flatten(order=self.flatten_order)
        if self.num_blank_axes > 0:
            for ax in self.figure['axes'][-self.num_blank_axes :]:
                ax.set_visible(False)

    @abc.abstractmethod
    def initialise_plot(self): ...

    def show(self):
        if not self.is_open:
            self.open_figure()
            self.initialise_plot()
            self.is_open = True
        plt.show()

    def close(self):
        plt.close(self.figure['figure'])

    def get_data(self, **kwargs):
        return self.da_data.isel(**kwargs).load()

    def get_first_data(self):
        selection = {
            dim: 0 for dim in self.da_data.dims if dim not in self.exclude_dims
        }
        return self.get_data(**selection)

    def format_dim(self, key, value):
        match key:
            case 'window':
                ts = pd.Timestamp(self.da_data.window.to_numpy()[value])
                return ts.strftime('window = %Y/%m/%d %H:%M')
            case 'month':
                ts = pd.date_range(start='2010-01-01', end='2010-12-31', freq='MS')[
                    value
                ]
                return ts.strftime('month = %B')
            case 'step' | 'hour':
                dt = pd.Timedelta(self.da_data[key].to_numpy()[value])
                return f'{key} = {dt}'
            case _:
                value = self.da_data[key].to_numpy()[value]
                return f'{key} = {value}'

    def get_title(self, **kwargs):
        return ', '.join(list(starmap(self.format_dim, kwargs.items())))

    def facet_titles(self):
        match self.facet_dim:
            case None:
                return ['']
            case str():
                return [
                    self.format_dim(self.facet_dim, i)
                    for i in range(len(self.da_data[self.facet_dim]))
                ]
            case str(), str():
                return [
                    self.format_dim(self.facet_dim[0], i)
                    + '\n'
                    + self.format_dim(self.facet_dim[1], j)
                    for j in range(len(self.da_data[self.facet_dim[1]]))
                    for i in range(len(self.da_data[self.facet_dim[0]]))
                ]
            case _:
                message = f'incorrect "facet_dim": {self.facet_dim}'
                raise ValueError(message)

    def facet_data(self, da_data):
        match self.facet_dim:
            case None:
                return [da_data]
            case str():
                return [
                    da_data.isel(**{self.facet_dim: i})
                    for i in range(len(self.da_data[self.facet_dim]))
                ]
            case str(), str():
                return [
                    da_data.isel(**{self.facet_dim[0]: i, self.facet_dim[1]: j})
                    for j in range(len(self.da_data[self.facet_dim[1]]))
                    for i in range(len(self.da_data[self.facet_dim[0]]))
                ]
            case _:
                message = f'unknown facet dim: {self.facet_dim}'
                raise ValueError(message)
