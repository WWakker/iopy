"""  Created on 03/10/2022::
------------- test_matrix -------------
**Authors**: W. Wakker

"""
from iopy.core.matrix import Matrix
import pandas as pd
import numpy as np
import pytest
from iopy.core.utils import ALPHA3_TO_ALPHA2


def process_df(df):
    if df.shape[0] > 1 and df.shape[1] > 1:
        return (df,
                [(ALPHA3_TO_ALPHA2[r] if r in ALPHA3_TO_ALPHA2 else r, s) for r, s in df.index.str.split('_')],
                [(ALPHA3_TO_ALPHA2[r] if r in ALPHA3_TO_ALPHA2 else r, s) for r, s in df.columns.str.split('_')])
    elif df.shape[0] == 1:
        return (df,
                df.index.to_list(),
                [(ALPHA3_TO_ALPHA2[r] if r in ALPHA3_TO_ALPHA2 else r, s) for r, s in df.columns.str.split('_')])
    else:
        return (df,
                [(ALPHA3_TO_ALPHA2[r] if r in ALPHA3_TO_ALPHA2 else r, s) for r, s in df.index.str.split('_')],
                df.columns.to_list())


df_13 = pd.DataFrame([1, 2, 3], index=['a_a', 'b_b', 'c_c'], columns=['a_a']).T
df_31 = pd.DataFrame([1, 2, 3], index=['a_a', 'b_b', 'c_c'], columns=['a_a'])
df_33 = pd.DataFrame(np.array([[0, -3, -2], [1, -4, -2], [-3, 4, 1]]), index=['a_a', 'b_b', 'c_c'], columns=['a_a', 'b_b', 'c_c'])

m13, m31, m33 = Matrix('something', *process_df(df_13)), Matrix('something', *process_df(df_31)), Matrix('something', *process_df(df_33))


class TestMatrix:

    def test1(self):
        for df in [df_13, df_31, df_33]:
            Matrix('something', *process_df(df))

    def test2(self):
        with pytest.raises(AssertionError):
            Matrix('something', [1, 2, 3], ['something'], ['something'])

    def testI(self):
        assert np.array_equal(np.array(m33.I), np.linalg.inv(df_33.to_numpy()))

    def testT(self):
        assert np.array_equal(np.array(m33.T), df_33.to_numpy().T)

    def test_transpose(self):
        assert np.array_equal(np.array(m33.transpose()), df_33.to_numpy().transpose())

    def test_flatten(self):
        assert np.array_equal(m33.flatten(), df_33.to_numpy().flatten())