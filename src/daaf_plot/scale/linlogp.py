from matplotlib import scale as mscale
from matplotlib.ticker import FixedLocator

from daaf_plot.transforms.linlogp import LinLogPressureTransform


class LinLogPressureScale(mscale.ScaleBase):
    name = 'linlogp'

    def __init__(self, axis, *, threshold=1e-5):
        super().__init__(axis)
        if threshold <= 0:
            raise ValueError('threshold must be positive')
        self.threshold = threshold

    def get_transform(self):
        return LinLogPressureTransform(self.threshold)

    def set_default_locators_and_formatters(self, axis):
        axis.set(major_locator=FixedLocator([1, 10, 100, 400, 700, 1000]))

    def limit_range_for_scale(self, vmin, vmax, minpos):
        return max(vmin, self.threshold), max(vmax, self.threshold)
