#!/usr/bin/env python

import argparse
import numpy as np
from tbssUtil import load, median_otsu, save_nifti, read_bvals_bvecs


def dwiMask(dwImg, outPrefix, median_radius, num_pass):
    """See brain mask extraction documentaion at http://nipy.org/dipy/examples_built/brain_extraction_dwi.html"""

    inPrefix= dwImg.split('.')[0]
    img= load(dwImg)
    bvals, _= read_bvals_bvecs(inPrefix+'.bval', None)

    # extract the first b0
    ind= np.where(bvals<50)[0][0]
    _, mask= median_otsu(img.get_fdata()[...,ind], median_radius, num_pass)

    save_nifti(outPrefix+'_mask.nii.gz', mask.astype('uint8'), img.affine, img.header)


def main():
    """Mask a dwi image by extracting b0. The first volume corresponding to bvalues<50 is taken as b0.
    Uses dipy.segment.mask.median_otsu function"""

    parser = argparse.ArgumentParser(description='')

    parser.add_argument('-i', '--input', type=str, help='diffusion weighted image')
    parser.add_argument('-o', '--output', type=str, help='output prefix, mask is saved as prefix_mask.nii.gz')

    parser.add_argument('-r', '--radius', type=int, help='median radius', default= 2)
    parser.add_argument('-n', '--num', type=int, help='number of pass', default= 1)

    args= parser.parse_args()

    dwiMask(args.input, args.output, args.radius, args.num)

if __name__ == '__main__':
    main()

