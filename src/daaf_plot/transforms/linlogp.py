import numpy as np
from matplotlib import transforms as mtransforms
from numpy import ma


class LinLogPressureTransform(mtransforms.Transform):
    """Forward transformation for the hybrid linear-logarithmic axis scale.

    Attributes:
        threshold: lower bound for pressure.
    """

    input_dims = 1
    output_dims = 1

    def __init__(self, threshold):
        """Initialise the transformation.

        Args:
            threshold: lower bound for pressure.
        """
        mtransforms.Transform.__init__(self)
        self.threshold = threshold

    def transform_non_affine(self, pressure):
        """Apply the scale.

        Args:
            pressure: array of pressure values to transform.

        Returns:
            Array of transformed pressure. Values below the
            threshold are masked.
        """
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
        """Get the inverse transformation."""
        return InvertedLinLogPressureTransform(self.threshold)


class InvertedLinLogPressureTransform(mtransforms.Transform):
    """Inverse transformation for the hybrid linear-logarithmic axis scale.

    Attributes:
        threshold: lower bound for pressure.
    """

    input_dims = 1
    output_dims = 1

    def __init__(self, threshold):
        """Initialise the transformation.

        Args:
            threshold: lower bound for pressure.
        """
        mtransforms.Transform.__init__(self)
        self.threshold = threshold

    def transform_non_affine(self, y_coordinate):
        """Apply the scale.

        Args:
            y_coordinate: array of y-coordinates to inverse transform.

        Returns:
            Array of pressure, computed by inverting the y-coordinates.
        """
        return np.where(
            y_coordinate >= 2,
            100 + (y_coordinate - 2) * (1000 - 100) / 3,
            np.power(10, y_coordinate),
        )

    def inverted(self):
        """Get the inverse transformation."""
        return LinLogPressureTransform(self.threshold)
