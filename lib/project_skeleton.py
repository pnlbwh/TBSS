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

from tbssUtil import pjoin, load, check_call

def project_skeleton(c, imgPath, args, skelDir):

    '''
    Part of FSL (ID: 5.0.11)
    tbss_skeleton (Version 1.03)
    Copyright(c) 2005-2007, University of Oxford (Stephen Smith)

    Usage:
    tbss_skeleton -i <inputimage> -o <skeleton>
    tbss_skeleton -i <inputimage> -p <skel_thresh> <distancemap> <search_rule_mask> <4Ddata> <projected_4Ddata> [-a <alt_4D>] [-s <alt_skeleton>]}

    Compulsory arguments (You MUST set one or more of):
        -i,--in	    input image

    Optional arguments (You may optionally specify one or more of):
        -o,--out	output image
        -p          <skel_thresh> <distancemap> <search_rule_mask> <4Ddata> <projected_4Ddata>
        -a	        alternative 4Ddata (e.g. L1)
        -s	        alternative skeleton
        -h,--help	display this message
        -d,--debug	switch on debugging image outputs
        -D,--debug2 <skelpoints>	de-project <skelpoints> points on skeleton back to all_FA space
    '''

    # FIXME: what to use with -i when ANTS/ENIGMA, look into tbss_skeleton.cc code

    print(f'projecting {imgPath} on skeleton ...')
    modImgSkel = pjoin(skelDir, f'{c}_{args.modality}_to_target_skel.nii.gz')

    if args.modality == 'FA':

        cmd=(' ').join(['tbss_skeleton',
                        '-i', imgPath,
                        '-p', args.SKEL_THRESH, args.skeletonMaskDst, args.SEARCH_RULE_MASK,
                        imgPath, modImgSkel,
                        '-s', args.skeletonMask])

        # check_call(cmd, shell= True)
        
        # use Popen() so we can wait()
        p = Popen(cmd, shell=True)
        p.wait()


    else:
        
        cmd= (' ').join(['tbss_skeleton',
                         '-i', imgPath,
                         '-p', args.SKEL_THRESH, args.skeletonMaskDst, args.SEARCH_RULE_MASK,
                         pjoin(args.outDir, 'FA', 'warped', f'{c}_FA_to_target.nii.gz'),
                         modImgSkel, '-a', imgPath,
                         '-s', args.skeletonMask])
        
        
        # check_call(cmd, shell= True)

        # use Popen() so we can wait()       
        p = Popen(cmd, shell=True)
        p.wait()


