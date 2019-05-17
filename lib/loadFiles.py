from tbssUtil import isfile, basename, pjoin
import numpy as np
from glob import glob
def read_imgs(file, n):

    imgs=[]
    with open(file) as f:

        content = f.read()
        for line, row in enumerate(content.split()):
            temp = [element for element in row.split(',') if element]  # handling w/space

            if len(temp) != n:
                raise FileNotFoundError(f'Columns don\'t have same number of entries: check line {line} in {file}')

            for img in temp:
                if not isfile(img):
                    raise FileNotFoundError(f'{img} does not exist: check line {line} in {file}')

            imgs.append(temp)

    return np.array(imgs)

def write_caselist(outDir, List=None, Dir=None):

    if Dir is not None:
        imgs= glob(pjoin(Dir, '*.nii.gz'))

    elif List is not None:
        try:
        # if List.shape[1]>1:
            imgs= List[ :,0]
        except:
            imgs= List

    caselist=pjoin(outDir,'caselist.txt')
    cases=[]
    with open(caselist, 'w') as f:
        for img in imgs:
            caseid= basename(img).split('.')[0]
            cases.append(caseid)
            f.write(caseid+'\n')

    return (caselist,cases)




if __name__=='__main__':
    imgs= read_imgs('/home/tb571/Documents/TBSS/local_tests/imagelist_double.txt',2)
    print('Wait')