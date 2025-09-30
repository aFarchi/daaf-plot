import logging

from matplotlib import pyplot as plt
import numpy as np

logger = logging.getLogger(__name__)


class MatplotlibFigureGeometry:
    def __init__(
        self,
        num_rows,
        num_cols,
        figure_w=None,
        axes_w=None,
        figure_h=None,
        axes_h=None,
        h_ratio_axes=None,
        pad_w_left=0.5,
        pad_w_in=0.3,
        pad_w_ax_vertical_aux=0.5,
        pad_w_right=0.5,
        vertical_aux_w=0.2,
        pad_h_top=0.5,
        pad_h_in=0.3,
        pad_h_ax_horizontal_aux=0.5,
        pad_h_bot=0.5,
        horizontal_aux_h=0.2,
        projection=None,
        x_label=None,
        y_label=None,
        vertical_aux_ax_name=None,
        horizontal_aux_ax_name=None,
    ):
        self.num_rows = num_rows
        self.num_cols = num_cols

        self.figure_w = figure_w
        self.axes_w = axes_w

        self.figure_h = figure_h
        self.axes_h = axes_h
        self.h_ratio_axes = h_ratio_axes

        self.pad_w_left = pad_w_left
        self.pad_w_in = pad_w_in
        self.pad_w_ax_vertical_aux = pad_w_ax_vertical_aux
        self.pad_w_right = pad_w_right
        self.vertical_aux_w = vertical_aux_w

        self.pad_h_top = pad_h_top
        self.pad_h_in = pad_h_in
        self.pad_h_ax_horizontal_aux = pad_h_ax_horizontal_aux
        self.pad_h_bot = pad_h_bot
        self.horizontal_aux_h = horizontal_aux_h

        self.projection = projection
        self.x_label = x_label
        self.y_label = y_label
        self.vertical_aux_ax_name = vertical_aux_ax_name
        self.horizontal_aux_ax_name = horizontal_aux_ax_name

    def tolist(
        self,
        scalar_or_iterable: list[float] | np.ndarray[float] | float | int,
        length: int,
    ):
        match scalar_or_iterable:
            case list():
                if len(scalar_or_iterable) == length:
                    return scalar_or_iterable
                raise ValueError(
                    f'inconsistent length: expected {length}, got {len(scalar_or_iterable)}'
                )
            case np.ndarray():
                return self.tolist(scalar_or_iterable.tolist(), length)
            case float() | int():
                return [scalar_or_iterable for _ in range(length)]
            case _:
                raise ValueError(
                    f'unable to convert type {type(scalar_or_iterable)} to list'
                )

    def compute_padding_w(self):
        pad_w_in = self.tolist(self.pad_w_in, self.num_cols - 1)
        return np.array([
            self.pad_w_left,
            *pad_w_in,
            self.pad_w_ax_vertical_aux + self.vertical_aux_w + self.pad_w_right,
        ])

    def compute_padding_h(self):
        pad_h_in = self.tolist(self.pad_h_in, self.num_rows - 1)
        return np.array([
            self.pad_h_ax_horizontal_aux + self.horizontal_aux_h + self.pad_h_bot,
            *pad_h_in,
            self.pad_h_top,
        ])

    def compute_figure_w(self, padding_w):
        match self.figure_w, self.axes_w:
            case None, _:
                logger.debug('using "axes_w"')
                axes_w = self.tolist(self.axes_w, self.num_cols)
                axes_w = np.array([0, *axes_w])
                figure_w = padding_w.sum() + axes_w.sum()
                return figure_w, axes_w
            case _, None:
                logger.debug('using "figure_w"')
                figure_w = self.figure_w
                axes_w = (figure_w - padding_w.sum()) / self.num_cols
                axes_w = self.tolist(axes_w, self.num_cols)
                axes_w = np.array([0, *axes_w])
                return figure_w, axes_w
            case None, None:
                raise ValueError('one of "figure_w" or "axes_w" must be provided')
            case _:
                raise ValueError(
                    'cannot provide at the same time "figure_w" and "axes_w"'
                )

    def compute_figure_h(self, axes_w, padding_h):
        match self.figure_h, self.axes_h, self.h_ratio_axes:
            case None, None, _:
                logger.debug('using "h_ratio_axes"')
                axes_h = self.h_ratio_axes * axes_w[1:].mean()
                axes_h = self.tolist(axes_h, self.num_rows)
                axes_h = np.array([0, *axes_h])
                figure_h = padding_h.sum() + axes_h.sum()
                return figure_h, axes_h
            case None, _, None:
                logger.debug('using "axes_h"')
                axes_h = self.tolist(self.axes_h, self.num_rows)
                axes_h = np.array([0, *axes_h])
                figure_h = padding_h.sum() + axes_h.sum()
                return figure_h, axes_h
            case _, None, None:
                logger.debug('using "figure_h"')
                figure_h = self.figure_h
                axes_h = (figure_h - padding_h.sum()) / self.num_rows
                axes_h = self.tolist(axes_h, self.num_rows)
                axes_h = np.array([0, *axes_h])
                return figure_h, axes_h
            case None, None, None:
                raise ValueError(
                    'one of "figure_h", "axes_h", or "h_ratio_axes" must be provided'
                )
            case _:
                raise ValueError(
                    'cannot provide at the same time "figure_h", "axes_h", and "h_ratio_axes"'
                )

    @staticmethod
    def axes_wh_to_extent(padding_w, padding_h, figure_w, axes_w, figure_h, axes_h):
        axes_x = (axes_w[:-1] + padding_w[:-1]).cumsum() / figure_w
        axes_y = (axes_h[:-1] + padding_h[:-1]).cumsum() / figure_h
        axes_dx = axes_w[1:] / figure_w
        axes_dy = axes_h[1:] / figure_h
        axes_x, axes_y = np.meshgrid(axes_x, axes_y, indexing='ij')
        axes_dx, axes_dy = np.meshgrid(axes_dx, axes_dy, indexing='ij')
        return np.array((axes_x, axes_y, axes_dx, axes_dy)).transpose(1, 2, 0)

    def get_axes_extent(self):
        padding_w = self.compute_padding_w()
        padding_h = self.compute_padding_h()
        figure_w, axes_w = self.compute_figure_w(padding_w)
        figure_h, axes_h = self.compute_figure_h(axes_w, padding_h)
        return (
            figure_w,
            figure_h,
            self.axes_wh_to_extent(
                padding_w, padding_h, figure_w, axes_w, figure_h, axes_h
            ),
        )

    def vertical_aux_extent(self, figure_w, figure_h):
        x = 1 - (self.vertical_aux_w + self.pad_w_right) / figure_w
        y = (
            self.pad_h_bot + self.horizontal_aux_h + self.pad_h_ax_horizontal_aux
        ) / figure_h
        dx = self.vertical_aux_w / figure_w
        dy = (
            1
            - (
                self.pad_h_top
                + self.pad_h_bot
                + self.horizontal_aux_h
                + self.pad_h_ax_horizontal_aux
            )
            / figure_h
        )
        return x, y, dx, dy

    def horizontal_aux_extent(self, figure_w, figure_h):
        x = self.pad_w_left / figure_w
        y = self.pad_h_bot / figure_h
        dx = (
            1
            - (
                self.pad_w_left
                + self.pad_w_right
                + self.vertical_aux_w
                + self.pad_w_ax_vertical_aux
            )
            / figure_w
        )
        dy = self.horizontal_aux_h / figure_h
        return x, y, dx, dy

    def open_ax(self, figure, axes_extent, ix, iy, share_x, share_y):
        ax = figure.add_axes(
            axes_extent[ix, iy],
            projection=self.projection,
            sharex=share_x,
            sharey=share_y,
        )
        share_x = share_x or ax
        share_y = share_y or ax
        if ix > 0:
            ax.tick_params(labelleft=False)
        elif self.y_label is not None:
            ax.set_ylabel(self.y_label)
        if iy > 0:
            ax.tick_params(labelbottom=False)
        elif self.x_label is not None:
            ax.set_xlabel(self.x_label)
        return share_x, share_y, ax

    def open_figure(self):
        figure_w, figure_h, axes_extent = self.get_axes_extent()

        # create figure
        figure = plt.figure(figsize=(figure_w, figure_h))
        figure.canvas.header_visible = False

        # add main axes
        axes = []
        share_x = None
        share_y = None
        for iy in range(self.num_rows - 1, -1, -1):
            axes_inner = []
            for ix in range(self.num_cols):
                share_x, share_y, ax = self.open_ax(
                    figure, axes_extent, ix, iy, share_x, share_y
                )
                axes_inner.append(ax)
            axes.append(axes_inner)
        axes = np.array(axes)

        # add aux axes
        aux_axes = {}
        if self.vertical_aux_w > 0:
            vertical_aux_extent = self.vertical_aux_extent(figure_w, figure_h)
            aux_axes[self.vertical_aux_ax_name] = figure.add_axes(vertical_aux_extent)
        if self.horizontal_aux_h > 0:
            horizontal_aux_extent = self.horizontal_aux_extent(figure_w, figure_h)
            aux_axes[self.horizontal_aux_ax_name] = figure.add_axes(
                horizontal_aux_extent
            )

        return {'figure': figure, 'axes': axes} | aux_axes
