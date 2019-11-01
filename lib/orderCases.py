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

def orderCases(imgs, cases, masks=None):

    # order imgs, masks according to cases
    
    n_c= len(cases)
    n_i= len(imgs)
    if n_c!=n_i:
        raise AttributeError(f'Number of images {n_i}  and cases {n_c} are not same')

    orderedImgs= imgs.copy()
    if masks:
        orderedMasks= masks.copy()

    for i, c in enumerate(cases):

        if c not in imgs[i]:

            FOUND= False
            for j in range(len(imgs)):
                if c in imgs[j]:
                    FOUND = True
                    break

            if not FOUND:
                raise FileNotFoundError(f'imgPath corresponding to case {c} not found in input list/directory, '
                                        'imgPath should have caseId in it')

            else:
                # print(f'Mismatch at case {c}, reordering ...')
                # swap i,j th entries ?
                # FIXME: pass now, but this sorting can be optimized

                orderedImgs[i]= imgs[j]
                if masks:
                    orderedMasks[i]= masks[j]


    if masks:
        return (orderedImgs, orderedMasks)
    else:
        return orderedImgs

