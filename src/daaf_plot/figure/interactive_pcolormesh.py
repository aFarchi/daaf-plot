import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import matplotlib.colors as m_colors
import ipywidgets as widgets

from daaf_plot.figure.abstract_interactive_figure import AbstractInteractiveFigure
from daaf_plot.style.pcolormesh_hover_formatter import PColorMeshHoverFormatter
import daaf_plot.style


class InteractivePColorMesh(AbstractInteractiveFigure):
    def __init__(
        self,
        da_data,
        x_dim,
        y_dim,
        facet_dim=None,
        open_figure_kwargs=None,
        flatten_order='C',
        colorbar_groups_dim=None,
    ):
        super().__init__(
            da_data,
            exclude_dims=(x_dim, y_dim),
            open_figure_kwargs=open_figure_kwargs,
            facet_dim=facet_dim,
            flatten_order=flatten_order,
        )
        self.x_dim = x_dim
        self.y_dim = y_dim
        self.earth_map = open_figure_kwargs.get('projection', None) is not None
        self.update_colorbar_lock = False
        self.open_figure_kwargs |= dict(x_label=self.x_dim, y_label=self.y_dim)
        self.colorbar_groups_dim = colorbar_groups_dim or []
        self.colorbar_settings = dict()
        if 'colorbar' not in self.open_figure_kwargs:
            self.open_figure_kwargs['colorbar'] = 'horizontal'

    def create_widgets(self):
        self.create_selection_widgets(smoothing=0)
        self.create_xy_scale_widgets()
        self.create_colorbar_widgets()

    def initialise_plot(self):
        da_data = self.get_first_data()

        pcm_kwargs = dict()
        norm = m_colors.Normalize(vmin=da_data.min(), vmax=da_data.max())
        pcm_kwargs['norm'] = norm
        if self.earth_map:
            pcm_kwargs['transform'] = ccrs.PlateCarree()

        self.figure['pcm'] = []
        cb_kwargs = dict(
            orientation=self.open_figure_kwargs['colorbar'], cax=self.figure['cb_ax']
        )

        for ax, title, facet_data in zip(
            self.figure['axes'], self.facet_titles(), self.facet_data(da_data)
        ):
            ax.set_title(title)
            x = da_data[self.x_dim]
            y = da_data[self.y_dim]
            z = facet_data
            pcm = ax.pcolormesh(x, y, z, **pcm_kwargs)
            ax.format_coord = PColorMeshHoverFormatter(ax, pcm, **cb_kwargs)
            self.figure['pcm'].append(pcm)

        self.figure['title'] = plt.suptitle('tmp title')

        self.figure['cb'] = self.figure['figure'].colorbar(
            self.figure['pcm'][0],
            extend='both',
            extendfrac=0.025,
            **cb_kwargs,
        )
        self.figure['cb_ax'].set_autoscale_on(False)
        self.figure['cb_ax'].callbacks.connect(
            'xlim_changed'
            if cb_kwargs['orientation'] == 'horizontal'
            else 'ylim_changed',
            self.update_colorbar_from_events,
        )

    def update_selection(self, **kwargs):
        da_data = self.get_data(**kwargs)
        title = self.get_title(**kwargs)
        self.figure['title'].set_text(title)
        cb_kwargs = dict(
            orientation=self.open_figure_kwargs['colorbar'], cax=self.figure['cb_ax']
        )
        for ax, pcm, facet_data in zip(
            self.figure['axes'], self.figure['pcm'], self.facet_data(da_data)
        ):
            pcm.set_array(facet_data.to_numpy().flatten())
            ax.format_coord = PColorMeshHoverFormatter(ax, pcm, **cb_kwargs)
        self.update_colorbar_from_settings()
        self.figure['figure'].canvas.draw_idle()

    def create_colorbar_widgets(self):
        new_widgets = dict(
            cmap_type=widgets.Dropdown(
                options=('continuous', 'discrete'),
                value='continuous',
                description='cmap type:',
            ),
            continuous_cmap_name=widgets.Dropdown(
                options=daaf_plot.style.continuous_cmap_list,
                value='viridis',
                description='cmap name:',
            ),
            discrete_cmap_name=widgets.Dropdown(
                options=daaf_plot.style.discrete_cmap_list,
                value='viridis',
                description='cmap name:',
            ),
            discrete_cmap_num_colors=widgets.IntText(
                value=10,
                description='num. colors:',
            ),
            cmap_reverse=widgets.Checkbox(
                value=False,
                description='reverse',
            ),
            scheme=widgets.Dropdown(
                options=('free', 'sequential', 'divergent'),
                value='free',
                description='v lim scheme:',
            ),
            free_vmin=widgets.FloatText(
                value=0,
                description='v min:',
            ),
            free_vmax=widgets.FloatText(
                value=0,
                description='v max:',
            ),
            seq_vmin=widgets.FloatText(
                value=0,
                description='v min:',
            ),
            seq_vmax=widgets.FloatText(
                value=0,
                description='v max:',
            ),
            div_vcentre=widgets.FloatText(
                value=0,
                description='v centre:',
            ),
            div_vmax=widgets.FloatText(
                value=0,
                description='v max:',
            ),
        )
        button = widgets.Button(description='auto rescale')
        stack = widgets.Stack(
            [
                widgets.HBox((new_widgets['continuous_cmap_name'],)),
                widgets.HBox((
                    new_widgets['discrete_cmap_name'],
                    new_widgets['discrete_cmap_num_colors'],
                )),
            ],
            selected_index=0,
        )
        widgets.jslink((new_widgets['cmap_type'], 'index'), (stack, 'selected_index'))
        container_cmap = widgets.HBox((
            new_widgets['cmap_type'],
            stack,
            new_widgets['cmap_reverse'],
        ))
        stack = widgets.Stack(
            [
                widgets.HBox((new_widgets['free_vmin'], new_widgets['free_vmax'])),
                widgets.HBox((new_widgets['seq_vmin'], new_widgets['seq_vmax'])),
                widgets.HBox((new_widgets['div_vcentre'], new_widgets['div_vmax'])),
            ],
            selected_index=0,
        )
        widgets.jslink((new_widgets['scheme'], 'index'), (stack, 'selected_index'))
        container_vlim = widgets.HBox((new_widgets['scheme'], stack))
        container = widgets.VBox((container_cmap, container_vlim, button))
        self.tabs['children'].append(container)
        self.tabs['titles'].append('colorbar')
        self.all_widgets['colorbar'] = new_widgets
        button.on_click(self.auto_rescale_colorbar)

    def acquire_colorbar_lock(self):
        if self.update_colorbar_lock:
            return False
        else:
            self.update_colorbar_lock = True
            return True

    def release_colorbar_lock(self):
        assert self.update_colorbar_lock
        self.update_colorbar_lock = False

    def update_colorbar_generic(
        self, from_widgets=False, event_vlim=None, auto_rescale=False
    ):
        multi_index = self.current_colorbar_selection()
        colorbar_settings = self.colorbar_settings.get(multi_index, dict())
        if from_widgets:
            colorbar_settings |= {
                key: value.value
                for (key, value) in self.all_widgets['colorbar'].items()
            }
        colorbar_autoscale = self.precompute_colorbar_autoscale(colorbar_settings)
        colorbar_settings = self.parse_colorbar_settings(
            colorbar_settings | colorbar_autoscale,
            event_vlim=event_vlim,
            auto_rescale=auto_rescale,
        )
        self.apply_colorbar_settings(colorbar_settings)
        self.update_colorbar_widgets(colorbar_settings)
        self.colorbar_settings[multi_index] = colorbar_settings
        self.figure['figure'].canvas.draw_idle()

    def current_colorbar_selection(self):
        return tuple(
            self.all_widgets['selection'][d].value for d in self.colorbar_groups_dim
        )

    def precompute_colorbar_autoscale(self, colorbar_settings):
        pcm_vmin = (
            colorbar_settings['pcm_vmin']
            if 'pcm_vmin' in colorbar_settings
            else min((pcm.get_array().min() for pcm in self.figure['pcm']))
        )
        pcm_vmax = (
            colorbar_settings['pcm_vmax']
            if 'pcm_vmax' in colorbar_settings
            else max((pcm.get_array().max() for pcm in self.figure['pcm']))
        )
        return dict(
            pcm_vmin=pcm_vmin,
            pcm_vmax=pcm_vmax,
            pcm_vcentre=(pcm_vmin + pcm_vmax) / 2,
        )

    @staticmethod
    def parse_colorbar_settings(colorbar_settings, event_vlim, auto_rescale):
        parsed_colorbar_settings = dict()

        cmap = None
        parsed_colorbar_settings['cmap_type'] = colorbar_settings.get(
            'cmap_type', 'continuous'
        )
        match parsed_colorbar_settings['cmap_type']:
            case 'continuous':
                cmap_name = colorbar_settings.get('continuous_cmap_name', 'viridis')
                cmap = plt.get_cmap(cmap_name)
                parsed_colorbar_settings['continuous_cmap_name'] = cmap_name
                parsed_colorbar_settings['discrete_cmap_name'] = cmap_name
                parsed_colorbar_settings['discrete_cmap_num_colors'] = (
                    colorbar_settings.get(
                        'discrete_cmap_num_colors',
                        10,
                    )
                )
            case 'discrete':
                cmap_name = colorbar_settings.get('discrete_cmap_name', 'viridis')
                num_colors = colorbar_settings.get('discrete_cmap_num_colors', 10)
                cmap = plt.get_cmap(cmap_name).resampled(num_colors)
                parsed_colorbar_settings['continuous_cmap_name'] = (
                    cmap_name
                    if cmap_name in daaf_plot.style.continuous_cmap_list
                    else colorbar_settings.get('continuous_cmap_name', 'viridis')
                )
                parsed_colorbar_settings['discrete_cmap_name'] = cmap_name
                parsed_colorbar_settings['discrete_cmap_num_colors'] = (
                    colorbar_settings.get(
                        'discrete_cmap_num_colors',
                        10,
                    )
                )
            case _:
                raise ValueError(
                    f'unknown cmap type: {parsed_colorbar_settings["cmap_type"]}'
                )
        parsed_colorbar_settings['cmap_reverse'] = colorbar_settings.get(
            'cmap_reverse', False
        )
        cmap = cmap.reversed() if parsed_colorbar_settings['cmap_reverse'] else cmap
        parsed_colorbar_settings['finalised_cmap'] = cmap

        vmin = None
        vmax = None
        vcentre = None
        parsed_colorbar_settings['scheme'] = colorbar_settings.get('scheme', 'free')
        match parsed_colorbar_settings['scheme']:
            case 'free':
                if event_vlim is not None:
                    vmin, vmax = event_vlim
                elif auto_rescale:
                    vmin = colorbar_settings['pcm_vmin']
                    vmax = colorbar_settings['pcm_vmax']
                else:
                    vmin = colorbar_settings.get(
                        'free_vmin', colorbar_settings['pcm_vmin']
                    )
                    vmax = colorbar_settings.get(
                        'free_vmax', colorbar_settings['pcm_vmax']
                    )
                vcentre = (vmin + vmax) / 2
            case 'sequential':
                if event_vlim is not None:
                    vmin = colorbar_settings.get(
                        'seq_vmin', colorbar_settings['pcm_vmin']
                    )
                    _, vmax = event_vlim
                elif auto_rescale:
                    vmin = colorbar_settings.get(
                        'seq_vmin', colorbar_settings['pcm_vmin']
                    )
                    vmax = colorbar_settings['pcm_vmax']
                else:
                    vmin = colorbar_settings.get(
                        'seq_vmin', colorbar_settings['pcm_vmin']
                    )
                    vmax = colorbar_settings.get(
                        'seq_vmax', colorbar_settings['pcm_vmax']
                    )
                vcentre = (vmin + vmax) / 2
            case 'divergent':
                if event_vlim is not None:
                    vcentre = colorbar_settings.get(
                        'div_vcentre', colorbar_settings['pcm_vcentre']
                    )
                    _, vmax = event_vlim
                elif auto_rescale:
                    vcentre = colorbar_settings.get(
                        'div_vcentre', colorbar_settings['pcm_vcentre']
                    )
                    vmax = max(
                        vcentre - colorbar_settings['pcm_vmin'],
                        colorbar_settings['pcm_vmax'] - vcentre,
                    )
                else:
                    vcentre = colorbar_settings.get(
                        'div_vcentre', colorbar_settings['pcm_vcentre']
                    )
                    vmax = colorbar_settings.get(
                        'div_vmax', colorbar_settings['pcm_vmax']
                    )
                vmin = 2 * vcentre - vmax
            case _:
                raise ValueError(
                    f'unknown scheme: {parsed_colorbar_settings["scheme"]}'
                )
        parsed_colorbar_settings['free_vmin'] = vmin
        parsed_colorbar_settings['free_vmax'] = vmax
        parsed_colorbar_settings['seq_vmin'] = vmin
        parsed_colorbar_settings['seq_vmax'] = vmax
        parsed_colorbar_settings['div_vcentre'] = vcentre
        parsed_colorbar_settings['div_vmax'] = vmax
        parsed_colorbar_settings['finalised_vlim'] = (vmin, vmax)
        parsed_colorbar_settings['pcm_vmin'] = colorbar_settings['pcm_vmin']
        parsed_colorbar_settings['pcm_vmax'] = colorbar_settings['pcm_vmax']
        parsed_colorbar_settings['pcm_vcentre'] = colorbar_settings['pcm_vcentre']
        return parsed_colorbar_settings

    def apply_colorbar_settings(self, colorbar_settings):
        for pcm in self.figure['pcm']:
            pcm.cmap = colorbar_settings['finalised_cmap']
            pcm.set_clim(*colorbar_settings['finalised_vlim'])

    def update_colorbar_widgets(self, colorbar_settings):
        for key, value in self.all_widgets['colorbar'].items():
            value.value = colorbar_settings[key]

    def update_colorbar(self, **_kwargs):
        if not self.acquire_colorbar_lock():
            return
        self.update_colorbar_generic(from_widgets=True)
        self.release_colorbar_lock()

    def update_colorbar_from_settings(self):
        if not self.acquire_colorbar_lock():
            return
        self.update_colorbar_generic()
        self.release_colorbar_lock()

    def update_colorbar_from_events(self, ax):
        if not self.acquire_colorbar_lock():
            return
        self.update_colorbar_generic(event_vlim=ax.get_xlim())
        self.release_colorbar_lock()

    def auto_rescale_colorbar(self, *_args, **_kwargs):
        if not self.acquire_colorbar_lock():
            return
        self.update_colorbar_generic(auto_rescale=True)
        self.release_colorbar_lock()
