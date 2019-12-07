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

from os.path import abspath, dirname, basename, isdir, isfile, exists, join as pjoin,  split as psplit
from os import mkdir, remove, listdir, chdir, getcwd, environ, getenv
from shutil import rmtree, copyfile, move, copytree
import unittest
from subprocess import check_call
import sys
from configparser import ConfigParser
from subprocess import check_call, Popen
from multiprocessing import Pool

FILEDIR= abspath(dirname(__file__))
LIBDIR= dirname(FILEDIR)
ROOTDIR= dirname(LIBDIR)

# sys.path.append(FILEDIR)
sys.path.append(LIBDIR)

from warnings import catch_warnings, filterwarnings, warn
filterwarnings("ignore", '.*size changed.*')

with catch_warnings():
    filterwarnings("ignore", category=FutureWarning)
    from nibabel import load, Nifti1Image
    from dipy.io.image import load_nifti
    from dipy.io import read_bvals_bvecs
    from dipy.core.gradients import gradient_table
    from dipy.segment.mask import applymask, median_otsu
    import dipy.reconst.dti as dipyDti

from plumbum.cmd import dtifit as fslDti

def save_nifti(fname, data, affine, hdr=None):
    if data.dtype.name=='uint8':
        hdr.set_data_dtype('uint8')
    else:
        hdr.set_data_dtype('float32')

    result_img = Nifti1Image(data, affine, header=hdr)
    result_img.to_filename(fname)


def makeDirectory(dir, force= False):

    if force and isdir(dir):
        warn(f'{dir} exists and will be overwritten')
        rmtree(dir)
        mkdir(dir)
    elif not force and isdir(dir):
        pass
        # warn(f'{dir} exists, --force not specified, continuing with existing directory')
    else:
        mkdir(dir)

def RAISE(ERR):
    raise ERR

