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

from tbssUtil import load, save_nifti, pjoin, check_call, environ, basename, Pool
import numpy as np
from project_skeleton import project_skeleton


def _create_skeleton(meanFA, skeleton):
    # create skeleton
    check_call((' ').join(['tbss_skeleton',
                          '-i', meanFA,
                          '-o', skeleton]),
                          shell= True)


def _create_skeletonMask(skeleton, SKEL_THRESH, skeletonMask):
    # create skeletonMask
    check_call((' ').join(['fslmaths',
                          skeleton, '-thr',
                          SKEL_THRESH, '-bin',
                          skeletonMask]),
                          shell= True)


def _create_skeletonMaskDst(templateMask, skeletonMask, skeletonMaskDst):
    # create skeletonMaskDst
    check_call((' ').join(['fslmaths',
                          templateMask, '-mul', '-1',
                          '-add', '1',
                          '-add', skeletonMask,
                          skeletonMaskDst]),
                          shell= True)

    check_call((' ').join(['distancemap',
                          '-i', skeletonMaskDst,
                          '-o', skeletonMaskDst]),
                          shell=True)


def calc_mean(imgs, shape, qc):

    # computing and saving allFA is a computational overhead
    # making it optional
    allFAdata= None
    if qc:
        allFAdata= np.zeros((len(imgs), shape[0], shape[1], shape[2]), dtype= 'float32')
    cumsumFA= np.zeros(shape, dtype= 'float32')

    
    for i, imgPath in enumerate(imgs):
        data= load(imgPath).get_data().clip(min= 0.)
        cumsumFA+= data
        if qc:
            allFAdata[i,: ]= data

    return (allFAdata, cumsumFA)


def skeletonize(imgs, cases, args, statsDir, skelDir, miFile):

    target= load(args.template)
    targetData= target.get_data()
    X,Y,Z= targetData.shape[0], targetData.shape[1], targetData.shape[2]

    # provide the user with allFA sequence so he knows which volume he is looking at while scrolling through allFA
    seqFile = pjoin(statsDir, 'allFAsequence.txt')
    with open(seqFile, 'w') as f:
        f.write('index,caseid\n')
        for i, c in enumerate(cases):
            f.write(f'{i},{c}\n')

    
    print(f'Calculating mean {args.modality} over all the cases ...')
    allFAdata, cumsumFA= calc_mean(imgs, (X,Y,Z), args.qc)

    if args.qc:
        allFA= pjoin(statsDir, f'all_{args.modality}.nii.gz')
        save_nifti(allFA, np.moveaxis(allFAdata, 0, -1), target.affine, target.header)

        print(f'''\n\nQC the warped {args.modality} images: {allFA}, view {seqFile} for index of volumes in all_FA.nii.gz. 
You may use fsleyes/fslview to load {allFA}.

MI metric b/w the warped images and target are stored in {miFile}

It might be helpful to re-run registration for warped images that are bad.

Moving images are   :   {args.outDir}/preproc/
Target is           :   {args.template}
Transform files are :   {args.xfrmDir}/
Warped images are   :   {args.outDir}/warped/

Save any re-registered images in {args.outDir}/warped/ with the same name as before

For re-registration of any subject, output the transform files to a temporary directory:
        
        mkdir /tmp/badRegistration/
        
        antsRegistrationSyNQuick.sh -d 3 \\
        -f TEMPLATE \\
        -m FA/preproc/caseid_FA.nii.gz \\
        -o /tmp/badRegistration/caseid_FA
        
        antsApplyTransforms -d 3 \\
        -i FA/preproc/caseid_FA.nii.gz \\
        -o FA/warped/caseid_[FA/MD/AD/RD]_to_target.nii.gz \\
        -r TEMPLATE \\
        -t /tmp/badRegistration/caseid_FA1Warp.nii.gz /tmp/badRegistration/caseid_FA0GenericAffine.mat
    
Finally, if wanted, you can copy the transform files to {args.xfrmDir}/ directory.

Note: Replace all the above directories with absolute paths.\n\n''')

        while input('Press Enter when you are done with QC/re-registration: '):
            pass

        allFAdata, cumsumFA= calc_mean(imgs, targetData.shape, args.qc)


    meanFAdata = cumsumFA/len(imgs)
    meanFA = pjoin(statsDir, 'mean_FA.nii.gz')

    # outDir should contain
    # all_{modality}.nii.gz
    # mean_FA.nii.gz
    # mean_FA_mask.nii.gz
    # mean_FA_skeleton.nii.gz
    # mean_FA_skeleton_mask.nii.gz
    # mean_FA_skeleton_mask_dst.nii.gz


    if args.modality=='FA':

        if not args.templateMask:
            print('Creating template mask ...')
            args.templateMask= pjoin(statsDir, 'mean_FA_mask.nii.gz')
            meanFAmaskData = (meanFAdata > 0) * 1
            save_nifti(args.templateMask, meanFAmaskData.astype('uint8'), target.affine, target.header)

        else:
            meanFAmaskData= load(args.templateMask).get_data()


        meanFAdata = meanFAdata * meanFAmaskData
        save_nifti(meanFA, meanFAdata, target.affine, target.header)


        # if skeleton is not given:
        #     create all three of skeleton, skeletonMask, and skeletonMaskDst

        # if skeleton is given and (neither skeletonMask nor skeletonMaskDst is given):
        #     create skeletonMask and skeletonMaskDst

        # if skeleton and skeletonMask is given and skeletonMaskDst is not given:
        #     create skeletonMaskDst


        if not args.skeleton:
            print('Creating all three of skeleton, skeletonMask, and skeletonMaskDst ...')
            args.skeleton= pjoin(statsDir, 'mean_FA_skeleton.nii.gz')
            args.skeletonMask = pjoin(statsDir, 'mean_FA_skeleton_mask.nii.gz')
            args.skeletonMaskDst= pjoin(statsDir, 'mean_FA_skeleton_mask_dst.nii.gz')

            _create_skeleton(meanFA, args.skeleton)
            _create_skeletonMask(args.skeleton, args.SKEL_THRESH, args.skeletonMask)
            _create_skeletonMaskDst(args.templateMask, args.skeletonMask, args.skeletonMaskDst)


        if args.skeleton and not (args.skeletonMask or args.skeletonMaskDst):
            print('Creating skeletonMask and skeletonMaskDst ...')
            args.skeletonMask = pjoin(statsDir, 'mean_FA_skeleton_mask.nii.gz')
            args.skeletonMaskDst= pjoin(statsDir, 'mean_FA_skeleton_mask_dst.nii.gz')

            _create_skeletonMask(args.skeleton, args.SKEL_THRESH, args.skeletonMask)
            _create_skeletonMaskDst(args.templateMask, args.skeletonMask, args.skeletonMaskDst)


        if args.skeleton and not args.skeletonMask and args.skeletonMaskDst:
            print('Creating skeletonMask ...')
            args.skeletonMask = pjoin(statsDir, 'mean_FA_skeleton_mask.nii.gz')

            _create_skeletonMask(args.skeleton, args.SKEL_THRESH, args.skeletonMask)


        if (args.skeleton and args.skeletonMask) and not args.skeletonMaskDst:
            print('Creating skeletonMaskDst ...')
            args.skeletonMaskDst = pjoin(statsDir, 'mean_FA_skeleton_mask_dst.nii.gz')

            _create_skeletonMaskDst(args.templateMask, args.skeletonMask, args.skeletonMaskDst)


    # mask allFA, this step does not seem to have any effect on the pipeline, it should help the user to visualize only
    if args.qc:
        check_call((' ').join(['fslmaths',
                               allFA, '-mas', args.templateMask, allFA]),
                               shell=True)



    # projecting all {modality} data onto skeleton
    res=[]
    allFAskeletonizedData= np.zeros((len(imgs), X, Y, Z), dtype= 'float32')
    pool= Pool(args.ncpu)
    for c, imgPath in zip(cases, imgs):

        res.append(pool.apply_async(project_skeleton, (c, imgPath, args, meanFA, skelDir)))


    for i,r in enumerate(res):
        # res contains data in the same order imgs was passed
        allFAskeletonizedData[i,: ]= r.get()

    pool.close()
    pool.join()

    allFAskeletonized= pjoin(statsDir, f'all_{args.modality}_skeletonized.nii.gz')
    print('Creating ', allFAskeletonized)
    save_nifti(allFAskeletonized, np.moveaxis(allFAskeletonizedData, 0, -1), target.affine, target.header)
    print(f'Created {allFAskeletonized} and corresponding index file: {seqFile}')

    return args
