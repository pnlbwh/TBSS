from dti import dti
from tbssUtil import pjoin, move

# convert NRRD to NIFTI on the fly
from conversion import nifti_write
def nrrd2nifti(imgPath):
    if imgPath.endswith('.nrrd') or imgPath.endswith('.nhdr'):
        niftiImgPrefix = imgPath.split('.')[0]
        nifti_write(imgPath, niftiImgPrefix)

        return niftiImgPrefix + '.nii.gz'
    else:
        return imgPath


def generate_diffusion_measures(dwImgPath, maskPath, caseId, outDir):

    dwImgPath= nrrd2nifti(dwImgPath)
    maskPath= nrrd2nifti(maskPath)

    inPrefix= dwImgPath.split('.')[0]
    outPrefix= pjoin('/tmp', caseId)
    dti(dwImgPath, maskPath, inPrefix, outPrefix)

    # organize diffusion measures into separate directories
    move(outPrefix+'_FA.nii.gz', pjoin(outDir, 'FA', caseId+'.nii.gz'))
    move(outPrefix+'_MD.nii.gz', pjoin(outDir, 'MD', caseId+'.nii.gz'))
    move(outPrefix+'_AD.nii.gz', pjoin(outDir, 'AD', caseId+'.nii.gz'))
    move(outPrefix+'_RD.nii.gz', pjoin(outDir, 'RD', caseId+'.nii.gz'))

