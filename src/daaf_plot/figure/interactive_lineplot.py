import numpy as np
import matplotlib.pyplot as plt
import ipywidgets as widgets

from daaf_plot.figure.abstract_interactive_figure import AbstractInteractiveFigure
import daaf_plot.style


class InteractiveLinePlot(AbstractInteractiveFigure):
    def __init__(
        self,
        da_data,
        x_dim,
        line_dim,
        facet_dim=None,
        open_figure_kwargs=None,
        flatten_order='C',
    ):
        super().__init__(
            da_data,
            exclude_dims=(x_dim, line_dim),
            open_figure_kwargs=open_figure_kwargs,
            facet_dim=facet_dim,
            flatten_order=flatten_order,
        )
        self.x_dim = x_dim
        self.line_dim = line_dim
        self.open_figure_kwargs |= dict(x_label=self.x_dim, colorbar=None)
        self.map_legend_to_ax = dict()
        if 'legend' not in self.open_figure_kwargs:
            self.open_figure_kwargs['legend'] = 'vertical'

    def create_widgets(self):
        self.create_selection_widgets(smoothing=len(self.da_data[self.x_dim]))
        self.create_style_widgets()
        self.create_xy_scale_widgets()
        self.figure['figure'].canvas.mpl_connect('pick_event', self.on_pick)

    def plot_lines(self, ax, da_data):
        return [
            ax.plot(
                da_data[self.x_dim],
                da_data.isel(**{self.line_dim: i}),
                label=self.format_dim(self.line_dim, i),
            )[0]
            for i in range(len(da_data[self.line_dim]))
        ]

    def update_lines(self, lines, da_data):
        for i in range(len(da_data[self.line_dim])):
            lines[i].set_ydata(da_data.isel(**{self.line_dim: i}))

    def initialise_plot(self):
        da_data = self.get_first_data()
        self.figure['lines'] = []
        for ax, title, facet_data in zip(
            self.figure['axes'], self.facet_titles(), self.facet_data(da_data)
        ):
            ax.set_title(title)
            self.figure['lines'].append(self.plot_lines(ax, facet_data))
        self.figure['fake_lines'] = [
            self.figure['legend_ax'].plot(
                [], [], label=self.format_dim(self.line_dim, i)
            )[0]
            for i in range(len(da_data[self.line_dim]))
        ]
        self.figure['title'] = plt.suptitle('tmp title')
        self.figure['legend_ax'].tick_params(
            left=None, bottom=None, labelleft=None, labelbottom=None
        )
        self.figure['legend_ax'].spines[['left', 'top', 'right', 'bottom']].set_visible(
            False
        )

    def update_selection(self, *, smoothing, **kwargs):
        da_data = self.get_data(**kwargs)
        if smoothing > 0:
            da_data = da_data.rolling(**{self.x_dim: smoothing}, center=True).mean()
        title = self.get_title(**kwargs)
        self.figure['title'].set_text(title)
        for lines, facet_data in zip(self.figure['lines'], self.facet_data(da_data)):
            self.update_lines(lines, facet_data)
        self.figure['figure'].canvas.draw_idle()

    def create_style_widgets(self):
        new_widgets = dict(
            cmap=widgets.Dropdown(
                options=daaf_plot.style.discrete_cmap_list,
                value='deep',
                description='cmap:',
            ),
            num_colors=widgets.IntText(
                value=10,
                description='num. colors:',
            ),
            reverse=widgets.Checkbox(
                value=False,
                description='reverse',
            ),
            legend=widgets.Checkbox(
                value=True,
                description='show legend',
            ),
            grid=widgets.Checkbox(
                value=True,
                description='show grid',
            ),
            y_label=widgets.Text(value='', description='y label:'),
        )
        container_cmap = widgets.HBox((
            new_widgets['cmap'],
            new_widgets['num_colors'],
            new_widgets['reverse'],
        ))
        container_other = widgets.HBox((
            new_widgets['legend'],
            new_widgets['grid'],
            new_widgets['y_label'],
        ))
        container = widgets.VBox((container_cmap, container_other))
        self.tabs['children'].append(container)
        self.tabs['titles'].append('style')
        self.all_widgets['style'] = new_widgets

    def update_style(self, **kwargs):
        cmap = plt.get_cmap(kwargs['cmap'])
        num_colors = kwargs['num_colors']
        cmap = cmap.resampled(num_colors) if num_colors < cmap.N else cmap
        cmap = cmap.reversed() if kwargs['reverse'] else cmap
        cmap = cmap(np.linspace(0, 1, cmap.N))
        for lines in self.figure['lines'] + [self.figure['fake_lines']]:
            for i, line in enumerate(lines):
                colour = cmap[i % cmap.shape[0]]
                line.set_color(colour)
        if kwargs['legend']:
            plt.sca(self.figure['legend_ax'])
            self.figure['legend'] = plt.legend()
            self.figure['legend'].set_draggable(True)
            for lines in self.figure['lines'] + [self.figure['fake_lines']]:
                for legend_line, ax_line in zip(
                    self.figure['legend'].get_lines(), lines
                ):
                    pick_radius = 5  # in pt
                    legend_line.set_picker(pick_radius)
                    if legend_line not in self.map_legend_to_ax:
                        self.map_legend_to_ax[legend_line] = []
                    self.map_legend_to_ax[legend_line].append(ax_line)
        else:
            self.figure['legend_ax'].get_legend().remove()
            self.map_legend_to_ax = dict()
        for ax in self.figure['axes']:
            ax.grid(kwargs['grid'])
        for ax in self.figure['y_label_axes']:
            ax.set_ylabel(kwargs['y_label'])
        self.figure['figure'].canvas.draw_idle()

    def on_pick(self, event):
        legend_line = event.artist
        if legend_line not in self.map_legend_to_ax:
            return
        for ax_line in self.map_legend_to_ax[legend_line]:
            visible = not ax_line.get_visible()
            ax_line.set_visible(visible)
            legend_line.set_alpha(1.0 if visible else 0.2)
        self.figure['figure'].canvas.draw_idle()
