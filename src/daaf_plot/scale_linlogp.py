#!/usr/bin/env python

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
        return self.LinLogPressureTransform(self.threshold)

    def set_default_locators_and_formatters(self, axis):
        axis.set(major_locator=FixedLocator([1, 10, 100, 400, 700, 1000]))

    def limit_range_for_scale(self, vmin, vmax, minpos):
        return max(vmin, self.threshold), max(vmax, self.threshold)

    class LinLogPressureTransform(mtransforms.Transform):
        input_dims = output_dims = 1

        def __init__(self, threshold):
            mtransforms.Transform.__init__(self)
            self.threshold = threshold

        def transform_non_affine(self, p):
            masked = ma.masked_where(p < self.threshold, p)
            if masked.mask.any():
                return ma.where(
                    p >= 100,
                    2 + 3 * (p - 100) / (1000 - 100),
                    ma.log10(p),
                )
            return np.where(
                p >= 100,
                2 + 3 * (p - 100) / (1000 - 100),
                np.log10(p),
            )

        def inverted(self):
            return LinLogPressureScale.InvertedLinLogPressureTransform(self.threshold)

    class InvertedLinLogPressureTransform(mtransforms.Transform):
        input_dims = output_dims = 1

        def __init__(self, threshold):
            mtransforms.Transform.__init__(self)
            self.threshold = threshold

        def transform_non_affine(self, y):
            return np.where(
                y >= 2,
                100 + (y - 2) * (1000 - 100) / 3,
                np.power(10, y),
            )

        def inverted(self):
            return LinLogPressureScale.LinLogPressureTransform(self.threshold)
