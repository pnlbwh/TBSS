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


from tbssUtil import pjoin, move, isfile, makeDirectory, check_call, chdir, getcwd, Pool, RAISE, basename, listdir
from conversion import read_cases
from antsTemplate import antsReg
from orderCases import orderCases
from glob import glob
from measureSimilarity import measureSimilarity
from skeletonize import skeletonize
from roi_analysis import roi_analysis
from antsTemplate import antsMult
from shellCmds import _fslmask, _antsApplyTransforms
from fillHoles import fillHoles

def process(args):

    cases= read_cases(args.caselist)

    # organize images into different directories ===========================================================

    # outDir
    #    |
    # ------------------------------------------------------------------------------------------------------
    #    |           |             |                |        |       |                   |           |
    #    |           |             |                |        |       |                   |           |
    # transform   template        FA                MD       AD      RD                 log        stats
    #                              |       (same inner file structure as that of FA)
    #                              |
    #                 ----------------------------------------
    #                  |         |         |       |        |
    #                 preproc  origdata  warped  skeleton  roi
    #
    # copy all FA into FA directory
    # put all preprocessed data into preproc directory
    # keep all warp/affine in transform directory
    # output all warped images in warped directory
    # output all skeletons in skel directory
    # output ROI based analysis files in roi directory
    # save all ROI statistics, mean, and combined images


    # define directories
    modDir = pjoin(args.outDir, f'{args.modality}')
    # args.xfrmDir = pjoin(args.outDir, 'transform')
    # args.statsDir = pjoin(args.outDir, 'stats')
    templateDir = pjoin(args.outDir, 'template/')  # trailing slash is important for antsMultivariate*.sh
    preprocDir= pjoin(modDir, 'preproc')
    warpDir= pjoin(modDir, 'warped')
    skelDir= pjoin(modDir, 'skeleton')
    roiDir= pjoin(modDir, 'roi')

    # force creation of inner directories
    makeDirectory(warpDir, True)
    makeDirectory(skelDir, True)
    makeDirectory(roiDir, True)


    # modality can be one of [FA,MD,AD,RD]
    # we could use just listdir(), but the following would be more strict and safe
    modImgs = glob(pjoin(modDir, '*.nii.gz'))
    modImgs = orderCases(modImgs, cases)


    for c, imgPath in zip(cases, modImgs):
        if imgPath is not f'{c}.nii.gz':
            move(imgPath, pjoin(modDir, f'{c}.nii.gz'))

    modImgs = glob(pjoin(modDir, '*.nii.gz'))
    modImgs = orderCases(modImgs, cases)



    # fill holes in all modality images
    # caveat: origdata no longer remain origdata, become hole filled origdata
    # pool= Pool(args.ncpu)
    # pool.map_async(fillHoles, modImgs, error_callback= RAISE)
    # pool.close()
    # pool.join()


    # preprocessing ========================================================================================
    if args.modality=='FA':
        print('Preprocessing FA images: eroding them and zeroing the end slices ...')
        modDir= pjoin(args.outDir, args.modality)
        CURRDIR= getcwd()
        chdir(modDir)
        check_call('tbss_1_preproc *.nii.gz', shell= True) # creates 'FA' and 'origdata' folders
        chdir(CURRDIR)
        print('Index file location has changed, see ', pjoin(preprocDir, 'slicesdir', 'index.html'))

        # rename args.modality/FA to args.modality/preproc
        move(pjoin(modDir, 'FA'), preprocDir)
    else:
        print(f'Preprocessing {args.modality} images using FA mask (eroding them and zeroing the end slices) ...')
        modDir = pjoin(args.outDir, args.modality)

        # force creation of inner directories
        makeDirectory(pjoin(modDir, 'origdata'), True)
        makeDirectory(pjoin(modDir, 'preproc'), True)

        pool= Pool(args.ncpu)
        for c, imgPath in zip(cases, modImgs):
            FAmask= pjoin(args.outDir, 'FA', 'preproc', f'{c}_FA_mask.nii.gz')
            preprocMod= pjoin(preprocDir, f'{c}_{args.modality}.nii.gz')

            pool.apply_async(_fslmask, (imgPath, FAmask, preprocMod), error_callback= RAISE)


        pool.close()
        pool.join()

        check_call((' ').join(['mv', pjoin(modDir, '*.nii.gz'), pjoin(modDir, 'origdata')]), shell= True)

    modImgs = glob(pjoin(preprocDir, f'*{args.modality}.nii.gz'))
    modImgs = orderCases(modImgs, cases)

    # create template ======================================================================================
    if not args.template and args.modality=='FA':
        print('Creating study specific template ...')
        # we could pass modImgs directly to antsMult(), instead saving them to a .txt file for logging
        # modImgs = glob(pjoin(preprocDir, f'*{args.modality}*.nii.gz'))

        makeDirectory(templateDir, args.force)

        antsMultCaselist = pjoin(args.logDir, 'antsMultCaselist.txt')
        with open(antsMultCaselist, 'w') as f:
            for imgPath in modImgs:
                f.write(imgPath+'\n')

        # ATTN: antsMultivariateTemplateConstruction2.sh requires '/' at the end of templateDir
        antsMult(antsMultCaselist, templateDir, args.logDir, args.ncpu, args.verbose)
        # TODO: rename the template
        args.template= pjoin(templateDir, 'template0.nii.gz')
        check_call(f'ln -s {args.template} {args.statsDir}', shell= True)

        # warp and affine to template0.nii.gz have been created for each case during template construction
        # so template directory should be the transform directory
        args.xfrmDir= templateDir

    # register each image to the template ==================================================================
    elif args.template:
        # find warp and affine of FA image to args.template for each case
        if args.modality=='FA':
            print(f'Registering FA images to {args.template} space ..')
            makeDirectory(args.xfrmDir, True)
            pool= Pool(args.ncpu)
            for c, imgPath in zip(cases, modImgs):
                pool.apply_async(antsReg, (args.template, imgPath, pjoin(args.xfrmDir, f'{c}_FA'), args.logDir, args.verbose),
                                error_callback= RAISE)

            pool.close()
            pool.join()


    # register template to a standard space ================================================================
    # useful when you would like to do ROI based analysis using an atlas
    # project the created/specified template to the space of atlas
    if args.space:
        outPrefix = pjoin(args.xfrmDir, 'tmp2space')
        warp2space = outPrefix + '1Warp.nii.gz'
        trans2space = outPrefix + '0GenericAffine.mat'
        if not isfile(warp2space):
            print(f'Registering {args.template} to the space of {args.space} ...')
            antsReg(args.space, args.template, outPrefix, args.logDir, args.verbose)

        # TODO: rename the template
        args.template = outPrefix + 'Warped.nii.gz'
        if basename(args.template) not in listdir(args.statsDir):
            check_call(f'ln -s {args.template} {args.statsDir}', shell= True)
        
    pool= Pool(args.ncpu)
    for c, imgPath in zip(cases, modImgs):
        # generalize warp and affine
        warp2tmp= glob(pjoin(args.xfrmDir, f'{c}_FA*[!Inverse]Warp.nii.gz'))[0]
        trans2tmp= glob(pjoin(args.xfrmDir, f'{c}_FA*GenericAffine.mat'))[0]
        output= pjoin(warpDir, f'{c}_{args.modality}_to_target.nii.gz')

        if not args.space:
            # print(f'Warping {imgPath} to template space ...')
            pool.apply_async(_antsApplyTransforms, (imgPath, output, args.template, warp2tmp, trans2tmp),
                            error_callback= RAISE)


        else:
            # print(f'Warping {imgPath} to template-->standard space ...')
            pool.apply_async(_antsApplyTransforms, (imgPath, output, args.template, warp2tmp, trans2tmp, warp2space, trans2space),
                            error_callback= RAISE)


    pool.close()
    pool.join()
    

    # create skeleton for each subject
    modImgsInTarget= glob(pjoin(warpDir, f'*_{args.modality}_to_target.nii.gz'))
    modImgsInTarget= orderCases(modImgsInTarget, cases)

    miFile= None
    if args.modality=='FA':
        print(f'Logging MI between warped images {warpDir}/*.nii.gz and target {args.template} ...')
        miFile= measureSimilarity(modImgsInTarget, cases, args.template, args.logDir, args.ncpu)


    # obtain modified args from skeletonize() which will be used for other modalities than FA
    args= skeletonize(modImgsInTarget, cases, args, skelDir, miFile)

    skelImgsInSub= glob(pjoin(skelDir, f'*_{args.modality}_to_target_skel.nii.gz'))
    skelImgsInSub= orderCases(skelImgsInSub, cases)

    # roi based analysis
    if args.labelMap:
        roi_analysis(skelImgsInSub, cases, args, roiDir, args.ncpu)

    return args

if __name__=='__main__':
    pass
