from plumbum import FG


def _fslmask(imgPath, FAmask, preprocMod):
    
    from plumbum.cmd import fslmaths

    print('Processing ', imgPath) 

    fslmaths[imgPath, '-mas', FAmask, preprocMod] & FG
    

def _antsApplyTransforms(imgPath, output, template, warp2tmp, trans2tmp, warp2space= None, trans2space= None):
    
    from plumbum.cmd import antsApplyTransforms
    
    if not (warp2space or trans2space):
        print(f'Warping {imgPath} to template space ...')
        antsApplyTransforms['-d', '3', 
                            '-i', imgPath,
                            '-o', output,
                            '-r', template,
                            '-t', warp2tmp, '-t', trans2tmp] & FG

    
    else:
        print(f'Warping {imgPath} to template-->standard space ...')
        antsApplyTransforms['-d', '3', 
                            '-i', imgPath,
                            '-o', output,
                            '-r', template,
                            '-t', warp2space, '-t', trans2space, '-t', warp2tmp, '-t', trans2tmp] & FG
        


