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
from .util import *

OUT_DIR= pjoin(FILEDIR,'enigmaTemplateOutput')
REF_DIR= pjoin(TEST_DATA_DIR,'enigma_res')

class TestPipeline(unittest.TestCase):

    print('Test ENIGMA branch results')

    def test_enigma_FA(self):

        print('FA equivalence test')
        # read output csv
        dfo= pd.read_csv(pjoin(OUT_DIR,'FA','FA_combined_roi_avg.csv'))


        # read ground truth csv
        dfg= pd.read_csv(pjoin(REF_DIR,'FA_combined_roi_avg.csv'))
        
        
        # check equivalence
        dfg.equals(dfo)


    def test_enigma_MD(self):

        print('MD equivalence test')
        # read output csv
        dfo= pd.read_csv(pjoin(OUT_DIR,'MD','MD_combined_roi_avg.csv'))


        # read ground truth csv
        dfg= pd.read_csv(pjoin(REF_DIR,'MD_combined_roi_avg.csv'))
        
        
        # check equivalence
        dfg.equals(dfo)



    def test_enigma_AD(self):

        print('AD equivalence test')
        # read output csv
        dfo= pd.read_csv(pjoin(OUT_DIR,'AD','AD_combined_roi_avg.csv'))


        # read ground truth csv
        dfg= pd.read_csv(pjoin(REF_DIR,'AD_combined_roi_avg.csv'))
        
        
        # check equivalence
        dfg.equals(dfo)


    def test_enigma_RD(self):

        print('RD equivalence test')
        # read output csv
        dfo= pd.read_csv(pjoin(OUT_DIR,'RD','RD_combined_roi_avg.csv'))


        # read ground truth csv
        dfg= pd.read_csv(pjoin(REF_DIR,'RD_combined_roi_avg.csv'))
        
        
        # check equivalence
        dfg.equals(dfo)



if __name__ == '__main__':
    unittest.main()
