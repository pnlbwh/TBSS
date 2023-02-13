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

from tbssUtil import load, save_nifti, pjoin, check_call, basename, Pool, psplit, RAISE
import numpy as np
from project_skeleton import project_skeleton
from conversion import read_cases


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


def calc_mean(imgs, shape):
    
    cumsumFA= np.zeros(shape, dtype= 'float32')
    consecutiveFA= np.inf*np.ones((2,shape[0],shape[1],shape[2]))
    for i, imgPath in enumerate(imgs):
        data= load(imgPath).get_fdata().clip(min= 0.)
        cumsumFA+= data
        
        consecutiveFA[0,: ]= data
        dynminFA= consecutiveFA.min(axis=0)
        consecutiveFA[1,: ]= dynminFA

    return (cumsumFA, dynminFA)


def skeletonize(imgs, args, warpDir, skelDir, miFile):

    target= load(args.template)
    L= len(imgs)
    X,Y,Z= tuple(target.header['dim'][1:4])

    # this is the given caselist, unsorted
    cases = read_cases(args.caselist)
   
    print(f'Calculating mean {args.modality} over all the cases ...')
    cumsumFA, dynminFA= calc_mean(imgs, (X,Y,Z))

    if args.qc:
        # computing and saving allFA is a computational overhead
        # made it optional with --qc flag
        allFAdata= np.zeros((L,X,Y,Z), dtype= 'float32')
        for i, c in enumerate(cases):
            allFAdata[i,: ]= load(pjoin(warpDir, f'{c}_{args.modality}_to_target.nii.gz')).get_fdata()

        allFA= pjoin(args.statsDir, f'all_{args.modality}.nii.gz')
        save_nifti(allFA, np.moveaxis(allFAdata, 0, -1), target.affine, target.header)

        print(f'''\n\nQC the warped {args.modality} images: {allFA}, view {args.caselist} for index of volumes in all_FA.nii.gz. 
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

        cumsumFA, dynminFA= calc_mean(imgs, (X,Y,Z))


    meanFAdata = cumsumFA/len(imgs)
    meanFA = pjoin(args.statsDir, 'mean_FA.nii.gz')

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
            args.templateMask= pjoin(args.statsDir, 'mean_FA_mask.nii.gz')
            meanFAmaskData = (meanFAdata > 0) * 1
            save_nifti(args.templateMask, meanFAmaskData.astype('uint8'), target.affine, target.header)

        else:
            meanFAmaskData= load(args.templateMask).get_fdata()


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
            args.skeleton= pjoin(args.statsDir, 'mean_FA_skeleton.nii.gz')
            args.skeletonMask = pjoin(args.statsDir, 'mean_FA_skeleton_mask.nii.gz')
            args.skeletonMaskDst= pjoin(args.statsDir, 'mean_FA_skeleton_mask_dst.nii.gz')

            _create_skeleton(meanFA, args.skeleton)
            _create_skeletonMask(args.skeleton, args.SKEL_THRESH, args.skeletonMask)
            _create_skeletonMaskDst(args.templateMask, args.skeletonMask, args.skeletonMaskDst)


        if args.skeleton and not (args.skeletonMask or args.skeletonMaskDst):
            print('Creating skeletonMask and skeletonMaskDst ...')
            args.skeletonMask = pjoin(args.statsDir, 'mean_FA_skeleton_mask.nii.gz')
            args.skeletonMaskDst= pjoin(args.statsDir, 'mean_FA_skeleton_mask_dst.nii.gz')

            _create_skeletonMask(args.skeleton, args.SKEL_THRESH, args.skeletonMask)
            _create_skeletonMaskDst(args.templateMask, args.skeletonMask, args.skeletonMaskDst)


        if args.skeleton and not args.skeletonMask and args.skeletonMaskDst:
            print('Creating skeletonMask ...')
            args.skeletonMask = pjoin(args.statsDir, 'mean_FA_skeleton_mask.nii.gz')

            _create_skeletonMask(args.skeleton, args.SKEL_THRESH, args.skeletonMask)


        if (args.skeleton and args.skeletonMask) and not args.skeletonMaskDst:
            print('Creating skeletonMaskDst ...')
            args.skeletonMaskDst = pjoin(args.statsDir, 'mean_FA_skeleton_mask_dst.nii.gz')

            _create_skeletonMaskDst(args.templateMask, args.skeletonMask, args.skeletonMaskDst)


    # mask allFA, this step does not seem to have any effect on the pipeline, it should help the user to visualize only
    if args.qc:
        check_call((' ').join(['fslmaths',
                               allFA, '-mas', args.templateMask, allFA]),
                               shell=True)



    # projecting all {modality} data onto skeleton
    pool= Pool(args.ncpu)
    for c in cases:
            imgPath= pjoin(warpDir, f'{c}_{args.modality}_to_target.nii.gz')
            pool.apply_async(project_skeleton, (c, imgPath, args, skelDir), error_callback= RAISE)
            
    pool.close()
    pool.join()
    

    if not args.noAllSkeleton:

        allFAskeletonized= pjoin(args.statsDir, f'all_{args.modality}_skeletonized.nii.gz')
        print('Creating ', allFAskeletonized)

        # this loop has been moved out of multiprocessing block to prevent memroy error
        allFAskeletonizedData= np.zeros((L, X, Y, Z), dtype= 'float32')
        for i,c in enumerate(cases):
            allFAskeletonizedData[i,: ]= load(pjoin(skelDir, f'{c}_{args.modality}_to_target_skel.nii.gz')).get_fdata()

        save_nifti(allFAskeletonized, np.moveaxis(allFAskeletonizedData, 0, -1), target.affine, target.header)
        print(f'Created {allFAskeletonized} sequenced according to {args.caselist}')


    return args

