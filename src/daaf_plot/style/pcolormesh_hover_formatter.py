import numpy as np


class PColorMeshHoverFormatter:
    def __init__(self, ax, pcm, *, orientation, cax):
        coordinates = pcm.get_coordinates()
        self.y_grid = coordinates[:, 0, 1]
        self.x_grid = coordinates[0, :, 0]
        self.z_grid = pcm.get_array().reshape((
            len(self.y_grid) - 1,
            len(self.x_grid) - 1,
        ))
        self.ax = ax
        self.orientation = orientation
        self.cax = cax

        monotonic_x = self.is_monotonic(self.x_grid)
        if monotonic_x == 'decreasing':
            self.x_grid = self.x_grid[::-1]
            self.z_grid = self.z_grid[:, ::-1]

        monotonic_y = self.is_monotonic(self.y_grid)
        if monotonic_y == 'decreasing':
            self.y_grid = self.y_grid[::-1]
            self.z_grid = self.z_grid[::-1]

        self.x_grid_centre = (self.x_grid[1:] + self.x_grid[:-1]) / 2
        self.y_grid_centre = (self.y_grid[1:] + self.y_grid[:-1]) / 2

    @staticmethod
    def is_monotonic(x):
        if (np.diff(x) > 0).all():
            return 'increasing'
        elif (np.diff(x) < 0).all():
            return 'decreasing'
        else:
            raise ValueError('coordinate is not monotonic')

    def __call__(self, x, y):
        if (
            x < self.x_grid[0]
            or x > self.x_grid[-1]
            or y < self.y_grid[0]
            or y > self.y_grid[-1]
        ):
            return f'cursor position: x = {x}, y = {y}'
        i = np.searchsorted(self.y_grid, y) - 1
        j = np.searchsorted(self.x_grid, x) - 1
        nearest_y = self.y_grid_centre[i]
        nearest_x = self.x_grid_centre[j]
        nearest_z = self.z_grid[i, j]
        if self.orientation == 'horizontal':
            nearest_z = self.cax.format_xdata(nearest_z)
        else:
            nearest_z = self.cax.format_ydata(nearest_z)
        return 'cursor position: x = {x}, y = {y} — data: x = {nx}, y = {ny}, z={nz}'.format(
            x=self.ax.format_xdata(x),
            y=self.ax.format_ydata(y),
            nx=self.ax.format_xdata(nearest_x),
            ny=self.ax.format_ydata(nearest_y),
            nz=nearest_z,
        )
