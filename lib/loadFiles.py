from tbssUtil import isfile, basename, pjoin
import numpy as np
from glob import glob
from datetime import datetime


def read_imgs(file, n):

    imgs=[]
    with open(file) as f:
        content = f.read().strip()

        for line, row in enumerate(content.split('\n')):
            temp = [element.strip() for element in row.split(',') if element]  # handling w/space

            if len(temp) != n:
                raise FileNotFoundError(f'Columns don\'t have same number of entries: check line {line} in {file}')

            for img in temp:
                if not isfile(img):
                    raise FileNotFoundError(f'{img} does not exist: check line {line} in {file}')

            imgs.append(temp)

    return np.array(imgs)


def write_caselist(logDir, List=None, Dir=None):

    if Dir is not None:
        imgs= glob(pjoin(Dir, '*.nii.gz'))
        imgs.sort()

    elif List is not None:
        try:
        # if List.shape[1]>1:
            imgs= List[ :,0]
        except:
            imgs= List

    caselist=pjoin(logDir,'caselist.txt')
    cases=[]
    with open(caselist, 'w') as f:
        for img in imgs:
            caseid= basename(img).split('.')[0]
            cases.append(caseid)
            f.write(caseid+'\n')

    return (caselist,cases)


properties= ['year', 'month', 'day', 'day', 'hour', 'minute', 'second', 'microsecond']

def write_time(filename, obj):

    values=[]
    with open(filename, 'w') as f:
        for prop in properties:
            values.append(eval(f'obj.{prop}'))

        f.write((' ').join([str(v) for v in values]))


def read_time(filename):

    with open(filename) as f:
        values= [int(x) for x in f.read().strip().split()]

    return datetime(values[0], values[1], values[2], values[4], values[5], values[6])


def checkDuplicity(imgs, cases):

    # for c1 in cases:
    #     count=0
    #     for c2 in cases:
    #         if c1==c2:
    #             count+=1
    #     if count>1:
    #         warn(f'Caseid {c1} is not unique, '
    #                'it exists multiple times or occurs as a substring in multiple caseids')


    print('\nChecking for duplicity of caseids in input images')

    for c in cases:
        dupPath=[]

        for imgPath in imgs:
            if c in imgPath:
                dupPath.append(basename(imgPath))

        if len(dupPath)>1:
            print(f'One (or some) of the caseids don\'t uniquely represent input images. '
                  f'For example, caseid {c} exists as a substring in multiple images: ', dupPath)
            raise ValueError('Either remove conflicting imgs/cases or provide --input IMAGELIST.csv')


if __name__=='__main__':
    pass
