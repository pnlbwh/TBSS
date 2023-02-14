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
from plumbum import FG
tool= getenv('DTIFIT_TOOL','DIPY')
cost_func= getenv('COST_FUNC','LS')

def dti(imgPath, maskPath, inPrefix, outPrefix):
       
    vol = load(imgPath)

    if tool=='DIPY':
        print('DIPY dtifit ', imgPath)

        mask= load(maskPath)
        bvals, bvecs= read_bvals_bvecs(inPrefix + '.bval', inPrefix + '.bvec')
        masked_vol = applymask(vol.get_fdata(), mask.get_fdata())

        gtab= gradient_table(bvals, bvecs)
        dtimodel= dipyDti.TensorModel(gtab, fit_method= cost_func)
        dtifit= dtimodel.fit(masked_vol)
        fa= dtifit.fa
        md= dtifit.md
        ad= dtifit.ad
        rd= dtifit.rd

        save_nifti(outPrefix + '_FA.nii.gz', fa, vol.affine, vol.header)
        save_nifti(outPrefix + '_MD.nii.gz', md, vol.affine, vol.header)
        save_nifti(outPrefix + '_AD.nii.gz', ad, vol.affine, vol.header)
        save_nifti(outPrefix + '_RD.nii.gz', rd, vol.affine, vol.header)

    elif tool=='FSL':

        print('FSL dtifit ', imgPath)

        if cost_func=='WLS':
            fslDti['-k', imgPath,
                   '-m', maskPath,
                   '-r', inPrefix + '.bvec',
                   '-b', inPrefix + '.bval',
                   '-w',
                   '-o', outPrefix
            ] & FG

        else:
            fslDti['-k', imgPath,
                   '-m', maskPath,
                   '-r', inPrefix + '.bvec',
                   '-b', inPrefix + '.bval',
                   '-o', outPrefix
            ] & FG


        # AD
        copyfile(outPrefix+'_L1.nii.gz', outPrefix+'_AD.nii.gz')

        # RD
        L2= load(outPrefix+'_L2.nii.gz').get_fdata()
        L3= load(outPrefix+'_L3.nii.gz').get_fdata()
        rd= (L2+L3)/2.

        save_nifti(outPrefix + '_RD.nii.gz', rd, vol.affine, vol.header)

        # remove other diffusion measures
        for i in range(1,4):
            remove(outPrefix+f'_V{i}.nii.gz')

        # remove other diffusion measures
        for i in range(1,4):
            remove(outPrefix+f'_L{i}.nii.gz')

        remove(outPrefix + f'_MO.nii.gz')
        remove(outPrefix + f'_S0.nii.gz')


if __name__ == '__main__':
    pass
