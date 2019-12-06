from tbssUtil import pjoin, RAISE, environ, isfile
from plumbum.cmd import antsRegistration, MeasureImageSimilarity, head, cut
from plumbum import FG
from multiprocessing import Pool
import numpy as np


def computeMI(target, img, miFile):

    (MeasureImageSimilarity['-d', '3', '-m', 'MI[{},{},1,256]'.format(target, img)] > miFile) & FG


def measureSimilarity(imgs, cases, target, logDir, ncpu):

    pool = Pool(ncpu)
    for img,c in zip(imgs,cases):
        print(f'MI between {c} and target')
        miFile = pjoin(logDir, f'{c}_MI.txt')
        pool.apply_async(func=computeMI, args=(target, img, miFile), error_callback= RAISE)

    pool.close()
    pool.join()

    summaryCsv = pjoin(logDir, 'similarity.csv')
    
    # loop for debugging
    # mis = []
    # with open(summaryCsv, 'w') as fw:
    #     for c in cases:
    #             with open(pjoin(logDir, f'{c}_MI.txt')) as f:
    #                 mi = f.read().strip()
    #                 fw.write(c+ ',' + mi + '\n')
    #                 mis.append(float(mi))


    print('The lower the MI, the better is the quality of registration. '
          f'Hence {summaryCsv} notes cases in ascending order of MI.')

    mis = []
    for c in cases:
        with open(pjoin(logDir, f'{c}_MI.txt')) as f:
            mi = f.read().strip()
            mis.append(float(mi))

    with open(summaryCsv, 'w') as fw:
        for i in np.argsort(mis):
            fw.write(cases[i] + ',' + str(mis[i]) + '\n')


    return summaryCsv

if __name__== '__main__':
    pass
