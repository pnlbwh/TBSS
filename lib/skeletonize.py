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

from tbssUtil import load, save_nifti, pjoin, check_call, environ, basename
import numpy as np

SKEL_THRESH= str(0.1)
SEARCH_RULE_MASK= pjoin(environ['FSLDIR'], 'data', 'standard', 'LowerCingulum_1mm.nii.gz')

def skeletonize(imgs, cases, modality, template, templateMask,
                skeleton, skeletonMask, skeletonMaskDst, outDir, skelDir, ANTS):

    target= load(template)
    targetData= target.get_data()
    X,Y,Z= targetData.shape[0], targetData.shape[1], targetData.shape[2]

    allFA= np.zeros((len(imgs), X, Y, Z), dtype= 'float32')
    for i, imgPath in enumerate(imgs):
        allFA[i,: ]= load(imgPath).get_data()

    save_nifti(pjoin(outDir, f'all_{modality}.nii.gz'), np.moveaxis(allFA, 0, -1), target.affine, target.header)

    meanFAdata = allFA.mean(0)
    meanFA = pjoin(outDir, 'mean_FA.nii.gz')

    # outdir should contain
    # all_{modality}.nii.gz
    # mean_FA.nii.gz
    # mean_FA_mask.nii.gz
    # mean_FA_skeleton.nii.gz
    # mean_FA_skeleton_mask.nii.gz
    # mean_FA_skeleton_mask_dst.nii.gz


    if modality=='FA':

        if not templateMask:
            meanFAmask= pjoin(outDir, 'mean_FA_mask.nii.gz')
            meanFAmaskData = (meanFAdata > 0) * 1
            save_nifti(meanFAmask, meanFAmaskData.astype('uint8'), target.affine, target.header)

            # essentially masking the created template
            meanFAdata = meanFAdata * meanFAmaskData
            save_nifti(meanFA, meanFAdata, target.affine, target.header)



        if not skeleton:
            # create all three of skeleton, skeletonMask, and skeletonMaskDst
            skeleton= pjoin(outDir, 'mean_FA_skeleton.nii.gz')
            skeletonMask = pjoin(outDir, 'mean_FA_skeleton_mask.nii.gz')
            skeletonMaskDst= pjoin(outDir, 'mean_FA_skeleton_mask_dst.nii.gz')

            check_call((' ').join(['tbss_skeleton',
                                  '-i', pjoin(outDir, 'mean_FA.nii.gz'),
                                  '-o', skeleton]),
                                  shell= True)

            # this way we wouldn't have to load the data in python
            check_call((' ').join(['fslmaths',
                                  skeleton, '-thr',
                                  SKEL_THRESH, '-bin',
                                  skeletonMask]),
                                  shell= True)

            check_call((' ').join(['fslmaths',
                                  meanFAmask, '-mul', '-1',
                                  '-add', '1',
                                  '-add', skeletonMask,
                                  skeletonMaskDst]),
                                  shell= True)


            check_call((' ').join(['distancemap',
                                  '-i', skeletonMaskDst,
                                  '-o', skeletonMaskDst]),
                                  shell=True)

    '''
    Part of FSL (ID: 5.0.11)
    tbss_skeleton (Version 1.03)
    Copyright(c) 2005-2007, University of Oxford (Stephen Smith)

    Usage: 
    tbss_skeleton -i <inputimage> -o <skeleton>
    tbss_skeleton -i <inputimage> -p <skel_thresh> <distancemap> <search_rule_mask> <4Ddata> <projected_4Ddata> [-a <alt_4D>] [-s <alt_skeleton>]}

    Compulsory arguments (You MUST set one or more of):
        -i,--in	input image

    Optional arguments (You may optionally specify one or more of):
        -o,--out	output image
        -p <skel_thresh> <distancemap> <search_rule_mask> <4Ddata> <projected_4Ddata>
        -a	alternative 4Ddata (e.g. L1)
        -s	alternative skeleton
        -h,--help	display this message
        -d,--debug	switch on debugging image outputs
        -D,--debug2 <skelpoints>	de-project <skelpoints> points on skeleton back to all_FA space
    '''


    # TODO
    # what to use with -i when ANTS/ENIGMA
    # do we need -s when ANTS

    # projecting all {modality} data onto skeleton
    for c, imgPath in zip(cases, imgs):

        modImgSkel = pjoin(skelDir, f'{c}_{modality}_to_target_skel.nii.gz')

        if modality != 'FA':
            # masking again shouldn't be necessary
            # because whatever method has created FA, the same method should create MD, AD, RD
            # therefore, provided mask should have been considered already

            if ANTS:
                check_call((' ').join(['tbss_skeleton',
                                      '-i', meanFA,
                                      '-p', SKEL_THRESH, skeletonMaskDst, SEARCH_RULE_MASK,
                                      pjoin(outDir, 'FA', 'warped', f'{c}_FA_to_target.nii.gz'),
                                      modImgSkel, '-a', imgPath]),
                                      shell= True)

            else:
                check_call((' ').join(['tbss_skeleton',
                                      '-i', meanFA,
                                      '-p', SKEL_THRESH, skeletonMaskDst, SEARCH_RULE_MASK,
                                      pjoin(outDir, 'FA', 'warped', f'{c}_FA_to_target.nii.gz'),
                                      modImgSkel, '-a', imgPath,
                                      '-s', skeletonMask]),
                                      shell= True)


        else:
            #
            check_call((' ').join(['tbss_skeleton',
                                  '-i', meanFA,
                                  '-p', SKEL_THRESH, skeletonMaskDst, SEARCH_RULE_MASK,
                                  imgPath, modImgSkel]),
                                  shell= True)

