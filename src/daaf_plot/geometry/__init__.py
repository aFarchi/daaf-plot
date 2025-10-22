from matplotlib import pyplot as plt

from daaf_plot.geometry.matplotlib_figure_geometry import MatplotlibFigureGeometry


def open_figure(
    colorbar=None,
    vcb_w=0.5,
    pad_w_ax_vcb=0.5,
    hcb_h=0.2,
    pad_h_ax_hcb=0.5,
    legend=None,
    vertical_legend_w=2,
    pad_w_ax_vertical_legend=0.5,
    horizontal_legend_h=2,
    pad_h_ax_horizontal_legend=0.5,
    **kwargs,
):
    match (colorbar, legend):
        case None, None:
            kwargs |= dict(
                pad_w_ax_vertical_aux=0,
                vertical_aux_w=0,
                pad_h_ax_horizontal_aux=0,
                horizontal_aux_h=0,
            )
        case 'horizontal', None:
            kwargs |= dict(
                pad_w_ax_vertical_aux=0,
                vertical_aux_w=0,
                pad_h_ax_horizontal_aux=pad_h_ax_hcb,
                horizontal_aux_h=hcb_h,
                horizontal_aux_ax_name='cb_ax',
            )
        case 'vertical', None:
            kwargs |= dict(
                pad_w_ax_vertical_aux=pad_w_ax_vcb,
                vertical_aux_w=vcb_w,
                pad_h_ax_horizontal_aux=0,
                horizontal_aux_h=0,
                vertical_aux_ax_name='cb_ax',
            )
        case None, 'horizontal':
            kwargs |= dict(
                pad_w_ax_vertical_aux=0,
                vertical_aux_w=0,
                pad_h_ax_horizontal_aux=pad_h_ax_horizontal_legend,
                horizontal_aux_h=horizontal_legend_h,
                horizontal_aux_ax_name='legend_ax',
            )
        case None, 'vertical':
            kwargs |= dict(
                pad_w_ax_vertical_aux=pad_w_ax_vertical_legend,
                vertical_aux_w=vertical_legend_w,
                pad_h_ax_horizontal_aux=0,
                horizontal_aux_h=0,
                vertical_aux_ax_name='legend_ax',
            )
        case _:
            raise ValueError('cannot have at the same time colorbar and legend')
    geometry = MatplotlibFigureGeometry(**kwargs)
    with plt.ioff():
        figure = geometry.open_figure()
    return figure
