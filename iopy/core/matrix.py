"""  Created on 03/10/2022::
------------- matrix -------------
**Authors**: W. Wakker

"""
import numpy as np


class Matrix(np.ndarray):

    def __new__(cls, info, input_array, rows, columns):
        obj = np.asarray(input_array).view(cls)
        assert len(obj.shape) == 2, "Array must be 2-dimensional"
        assert obj.shape == (len(rows), len(columns)), "Rows and columns do not have the shape of the array"
        obj.info = info
        obj.rows = rows
        obj.columns = columns
        return obj

    def __array_finalize__(self, obj):
        self.info = getattr(obj, 'info', None)
        self.rows = getattr(obj, 'rows', None)
        self.columns = getattr(obj, 'columns', None)

    @property
    def I(self):
        """Invert matrix

        Returns:
            Inverted matrix
        """
        return np.linalg.inv(self)

    @property
    def T(self):
        """Transpose rows and columns

        Returns:
            Transposed Matrix
        """
        m = self.copy()
        m.rows, m.columns = m.columns, m.rows
        return np.transpose(m)

    def transpose(self):
        """Transpose rows and columns

        Returns:
            Transposed Matrix
        """
        m = self.copy()
        m.rows, m.columns = m.columns, m.rows
        return np.transpose(m)

    def flatten(self):
        """Convert to flattened numpy array

        Returns:
            flattened numpy array
        """
        m = np.array(self)
        return m.flatten()

    def to_numpy(self):
        """Convert to numpy array

        Returns:
            numpy array
        """
        return np.asarray(self)
