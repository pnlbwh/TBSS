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

from tbssUtil import *
config = ConfigParser()
config.read(pjoin(FILEDIR,'config.ini'))
N_proc= config['DEFAULT']['N_CPU']

def antsMult(caselist, outPrefix):

    check_call((' ').join(['antsMultivariateTemplateConstruction2.sh',
                           '-d', '3',
                           '-g', '0.2',
                           '-t', "BSplineSyN[0.1,26,0]",
                           '-r', '1',
                           '-c', '2',
                           '-j', str(N_proc),
                           '-f', '8x4x2x1',
                           '-o', outPrefix,
                           caselist]), shell= True)
