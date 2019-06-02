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
verbose= int(config['DEFAULT']['verbose'])


def antsMult(caselist, outPrefix, logDir):

    if verbose:
        f= sys.stdout
    else:
        logFile= pjoin(logDir, 'template_construct.log')
        f= open(logFile, 'w')
        print(f'See {logFile} for details of template construction')


    check_call((' ').join(['antsMultivariateTemplateConstruction2.sh',
                           '-d', '3',
                           '-g', '0.2',
                           '-t', "BSplineSyN[0.1,26,0]",
                           '-r', '1',
                           '-c', '2',
                           '-j', str(N_proc),
                           '-f', '8x4x2x1',
                           '-o', outPrefix,
                           caselist]), shell= True, stdout= f, stderr= sys.stdout)


def antsReg(fixedImg, movingImg, outPrefix, logDir):

    if verbose:
        f= sys.stdout
    else:
        logFile= pjoin(logDir, basename(outPrefix)+ '_ANTs.log')
        f= open(logFile, 'w')

    print(f'fixedImage: {fixedImg}, movingImage: {movingImg}')
    check_call((' ').join(['antsRegistrationSyNQuick.sh',
                           '-d', '3',
                           '-f', fixedImg,
                           '-m', movingImg,
                           '-o', outPrefix,
                           '-n', '8']), shell=True, stdout= f, stderr= sys.stdout)

