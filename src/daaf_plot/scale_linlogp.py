import numpy as np
from matplotlib import scale as mscale
from matplotlib import transforms as mtransforms
from matplotlib.ticker import FixedLocator
from numpy import ma


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


class LinLogPressureTransform(mtransforms.Transform):
    input_dims = 1
    output_dims = 1

    def __init__(self, threshold):
        mtransforms.Transform.__init__(self)
        self.threshold = threshold

    def transform_non_affine(self, pressure):
        masked = ma.masked_where(pressure < self.threshold, pressure)
        if masked.mask.any():
            return ma.where(
                pressure >= 100,
                2 + 3 * (pressure - 100) / (1000 - 100),
                ma.log10(pressure),
            )
        return np.where(
            pressure >= 100,
            2 + 3 * (pressure - 100) / (1000 - 100),
            np.log10(pressure),
        )

    def inverted(self):
        return InvertedLinLogPressureTransform(self.threshold)


class InvertedLinLogPressureTransform(mtransforms.Transform):
    input_dims = 1
    output_dims = 1

    def __init__(self, threshold):
        mtransforms.Transform.__init__(self)
        self.threshold = threshold

    def transform_non_affine(self, y_coordinate):
        return np.where(
            y_coordinate >= 2,
            100 + (y_coordinate - 2) * (1000 - 100) / 3,
            np.power(10, y_coordinate),
        )

    def inverted(self):
        return LinLogPressureTransform(self.threshold)
