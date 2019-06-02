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

# convert NRRD to NIFTI on the fly
from conversion import nifti_write
def nrrd2nifti(imgPath):
    if imgPath.endswith('.nrrd') or imgPath.endswith('.nhdr'):
        niftiImgPrefix = imgPath.split('.')[0]
        nifti_write(imgPath, niftiImgPrefix)

        return niftiImgPrefix + '.nii.gz'
    else:
        return imgPath