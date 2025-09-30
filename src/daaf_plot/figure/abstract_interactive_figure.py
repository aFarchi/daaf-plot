import abc

import ipywidgets as widgets
from IPython.display import display

from daaf_plot.figure.abstract_figure import AbstractFigure
from daaf_plot.style import scale_list


class AbstractInteractiveFigure(AbstractFigure, abc.ABC):
    def __init__(
        self,
        da_data,
        *,
        exclude_dims,
        open_figure_kwargs,
        facet_dim,
        flatten_order,
    ):
        super().__init__(
            da_data,
            exclude_dims=exclude_dims,
            open_figure_kwargs=open_figure_kwargs,
            facet_dim=facet_dim,
            flatten_order=flatten_order,
        )
        self.all_widgets = {}
        self.tabs = dict(children=[], titles=[])
        self.main_widget = None
        self.is_interactive_open = False
        self.current_scales = dict(x=None, y=None)

    def interactive_show(self):
        if not self.is_open:
            self.open_figure()
            self.initialise_plot()
            self.is_open = True
        if not self.is_interactive_open:
            self.create_widgets()
            self.create_tabs()
            self.enable_interaction()
            self.is_interactive_open = True
        display(self.main_widget)

    @abc.abstractmethod
    def create_widgets(self): ...

    def create_tabs(self):
        widget_tabs = widgets.Tab(
            children=self.tabs['children'],
            titles=self.tabs['titles'],
        )
        self.main_widget = widgets.VBox((widget_tabs, self.figure['figure'].canvas))

    def enable_interaction(self):
        for name, the_widgets in self.all_widgets.items():
            widgets.interactive_output(
                getattr(self, f'update_{name}'),
                self.all_widgets[name],
            )

    def create_selection_widgets(self, smoothing):
        new_widgets = dict()
        for dim in self.da_data.dims:
            if dim not in self.exclude_dims:
                if isinstance(self.da_data[dim].to_numpy()[0], str):
                    new_widgets[dim] = widgets.Dropdown(
                        options=[
                            (s, i) for (i, s) in enumerate(self.da_data[dim].to_numpy())
                        ],
                        value=0,
                        description=f'{dim}:',
                    )
                else:
                    new_widgets[dim] = widgets.IntSlider(
                        value=0,
                        min=0,
                        max=len(self.da_data[dim]) - 1,
                        step=1,
                        description=f'{dim}:',
                    )
        if smoothing > 0:
            new_widgets['smoothing'] = widgets.IntSlider(
                value=0,
                min=0,
                max=smoothing,
                step=1,
                description='smoothing:',
            )
        container = widgets.VBox(list(new_widgets.values()))
        self.tabs['children'].append(container)
        self.tabs['titles'].append('selection')
        self.all_widgets['selection'] = new_widgets

    @abc.abstractmethod
    def update_selection(self, **kwargs): ...

    def create_xy_scale_widgets(self):
        new_widgets = dict(
            x_scale=widgets.Dropdown(
                options=scale_list,
                value='linear',
                description='x scale:',
            ),
            x_inverted=widgets.Checkbox(
                value=False,
                description='invert x axis',
            ),
            y_scale=widgets.Dropdown(
                options=scale_list,
                value='linear',
                description='y scale:',
            ),
            y_inverted=widgets.Checkbox(
                value=False,
                description='invert y axis',
            ),
        )
        button_x = widgets.Button(description='auto rescale x')
        button_y = widgets.Button(description='auto rescale y')
        button_xy = widgets.Button(description='auto rescale xy')
        container_x = widgets.HBox((new_widgets['x_scale'], new_widgets['x_inverted']))
        container_y = widgets.HBox((new_widgets['y_scale'], new_widgets['y_inverted']))
        container_b = widgets.HBox((button_x, button_y, button_xy))
        container = widgets.VBox((container_x, container_y, container_b))
        self.tabs['children'].append(container)
        self.tabs['titles'].append('xy_scale')
        self.all_widgets['xy_scale'] = new_widgets
        button_x.on_click(self.auto_rescale_x)
        button_y.on_click(self.auto_rescale_y)
        button_xy.on_click(self.auto_rescale_xy)

    def auto_rescale_x(self, *_args, **_kwargs):
        for ax in self.figure['axes']:
            ax.relim(visible_only=True)
        for ax in self.figure['axes']:
            ax.autoscale(axis='x')
        self.figure['figure'].canvas.draw_idle()

    def auto_rescale_y(self, *_args, **_kwargs):
        for ax in self.figure['axes']:
            ax.relim(visible_only=True)
        for ax in self.figure['axes']:
            ax.autoscale(axis='y')
        self.figure['figure'].canvas.draw_idle()

    def auto_rescale_xy(self, *_args, **_kwargs):
        for ax in self.figure['axes']:
            ax.relim(visible_only=True)
        for ax in self.figure['axes']:
            ax.autoscale()
        self.figure['figure'].canvas.draw_idle()

    def update_xy_scale(self, **kwargs):
        for ax in self.figure['axes']:
            ax.set_xscale(kwargs['x_scale'])
            ax.set_yscale(kwargs['y_scale'])
            ax.xaxis.set_inverted(kwargs['x_inverted'])
            ax.yaxis.set_inverted(kwargs['y_inverted'])
        for which in ('x', 'y'):
            if kwargs[f'{which}_scale'] != self.current_scales[which]:
                for ax in self.figure['axes']:
                    ax.autoscale(axis=which)
                self.current_scales[which] = kwargs[f'{which}_scale']
        self.figure['figure'].canvas.draw_idle()
