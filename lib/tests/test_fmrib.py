#!/usr/bin/env python

# ===============================================================================
# tbss (2019) pipeline is written by-
#
# TASHRIF BILLAH
# Brigham and Women's Hospital/Harvard Medical School
# tbillah@bwh.harvard.edu
#
# ===============================================================================
# See details at https://github.com/pnlbwh/tbss
# Submit issues at https://github.com/pnlbwh/tbss/issues
# View LICENSE at https://github.com/pnlbwh/tbss/blob/master/LICENSE
# ===============================================================================

import pandas as pd
from util import *
import numpy as np

OUT_DIR= pjoin(FILEDIR,'fmribTemplateOutput','stats')
REF_DIR= pjoin(TEST_DATA_DIR,'fmrib_res')

class TestFmrib(unittest.TestCase):

    print('Test FMRIB branch results')

    def test_fmrib_FA(self):
        print('FA equivalence test')
        # read output csv
        dfo = pd.read_csv(pjoin(OUT_DIR, 'FA_combined_roi_avg.csv'))

        # read ground truth csv
        dfg = pd.read_csv(pjoin(REF_DIR, 'FA_combined_roi_avg.csv'))

        ### check equivalence ###

        # case equivalence (1st row)
        np.testing.assert_array_equal(dfg.values[:, 0], dfo.values[:, 0])

        # tract equivalence (1st col)
        np.testing.assert_array_equal(dfg.columns, dfo.columns)

        # value relative percentage difference (all values)
        rel_diff = 2 * abs(dfg.values[:, 1:] - dfo.values[:, 1:]).sum() / \
                   (dfg.values[:, 1:] + dfo.values[:, 1:]).sum() * 100
        print('Relative difference: ', rel_diff)
        np.testing.assert_array_less(rel_diff, REL_DIFF_THRESH)

    def test_fmrib_MD(self):
        print('MD equivalence test')
        # read output csv
        dfo = pd.read_csv(pjoin(OUT_DIR, 'MD_combined_roi_avg.csv'))

        # read ground truth csv
        dfg = pd.read_csv(pjoin(REF_DIR, 'MD_combined_roi_avg.csv'))

        ### check equivalence ###

        # case equivalence (1st row)
        np.testing.assert_array_equal(dfg.values[:, 0], dfo.values[:, 0])

        # tract equivalence (1st col)
        np.testing.assert_array_equal(dfg.columns, dfo.columns)

        # value relative percentage difference (all values)
        rel_diff = 2 * abs(dfg.values[:, 1:] - dfo.values[:, 1:]).sum() / \
                   (dfg.values[:, 1:] + dfo.values[:, 1:]).sum() * 100
        print('Relative difference: ', rel_diff)
        np.testing.assert_array_less(rel_diff, REL_DIFF_THRESH)

    def test_fmrib_AD(self):
        print('AD equivalence test')
        # read output csv
        dfo = pd.read_csv(pjoin(OUT_DIR, 'AD_combined_roi_avg.csv'))

        # read ground truth csv
        dfg = pd.read_csv(pjoin(REF_DIR, 'AD_combined_roi_avg.csv'))

        ### check equivalence ###

        # case equivalence (1st row)
        np.testing.assert_array_equal(dfg.values[:, 0], dfo.values[:, 0])

        # tract equivalence (1st col)
        np.testing.assert_array_equal(dfg.columns, dfo.columns)

        # value relative percentage difference (all values)
        rel_diff = 2 * abs(dfg.values[:, 1:] - dfo.values[:, 1:]).sum() / \
                   (dfg.values[:, 1:] + dfo.values[:, 1:]).sum() * 100
        print('Relative difference: ', rel_diff)
        np.testing.assert_array_less(rel_diff, REL_DIFF_THRESH)

    def test_fmrib_RD(self):
        print('RD equivalence test')
        # read output csv
        dfo = pd.read_csv(pjoin(OUT_DIR, 'RD_combined_roi_avg.csv'))

        # read ground truth csv
        dfg = pd.read_csv(pjoin(REF_DIR, 'RD_combined_roi_avg.csv'))

        ### check equivalence ###

        # case equivalence (1st row)
        np.testing.assert_array_equal(dfg.values[:, 0], dfo.values[:, 0])

        # tract equivalence (1st col)
        np.testing.assert_array_equal(dfg.columns, dfo.columns)

        # value relative percentage difference (all values)
        rel_diff = 2 * abs(dfg.values[:, 1:] - dfo.values[:, 1:]).sum() / \
                   (dfg.values[:, 1:] + dfo.values[:, 1:]).sum() * 100
        print('Relative difference: ', rel_diff)
        np.testing.assert_array_less(rel_diff, REL_DIFF_THRESH)


if __name__ == '__main__':
    unittest.main()
