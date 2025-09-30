import numpy as np
from matplotlib import transforms as mtransforms
from numpy import ma


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
