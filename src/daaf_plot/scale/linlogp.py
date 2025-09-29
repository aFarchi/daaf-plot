from matplotlib import scale as mscale
from matplotlib.ticker import FixedLocator

from daaf_plot.transforms.linlogp import LinLogPressureTransform


class LinLogPressureScale(mscale.ScaleBase):
    """Hybrid linear-logarithmic axis scale to represent pressure.

    Attributes:
        threshold: lower bound for pressure.
    """

    name = 'linlogp'

    def __init__(self, axis, *, threshold=1e-5):
        """Initialise the scale.

        Args:
            axis: matplotlib axis.
            threshold: lower bound for pressure.
        """
        super().__init__(axis)
        if threshold <= 0:
            raise ValueError('threshold must be positive')
        self.threshold = threshold

    def get_transform(self):
        """Construct the forward transformation.

        Returns:
            Associated hybrid linear-logarithmic transformation.
        """
        return LinLogPressureTransform(self.threshold)

    def set_default_locators_and_formatters(self, axis):
        """Set default tick locators and formatters.

        Args:
            axis: matplotlib axis.
        """
        axis.set(major_locator=FixedLocator([1, 10, 100, 400, 700, 1000]))

    def limit_range_for_scale(self, vmin, vmax, minpos):
        """Limit the range for the given axis.

        Args:
            vmin: minimum pressure value to plot.
            vmax: maximum pressure value to plot.
            minpos: ignored.

        Returns:
            Tuple (vmin, vmax) after applying the threshold.
        """
        return max(vmin, self.threshold), max(vmax, self.threshold)
