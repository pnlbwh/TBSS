from tbssUtil import pjoin
from plumbum.cmd import MeasureImageSimilarity
from plumbum import FG
from multiprocessing import Pool
import numpy as np

def computeMI(target, img, miFile):
    (MeasureImageSimilarity['-d', '3',
                            '-m', 'MI[{},{},1,256]'.format(target, img)] > miFile) & FG


def measureSimilarity(imgs, cases, target, logDir, ncpu):

    pool = Pool(ncpu)
    for img,c in zip(imgs,cases):
        print(f'MI between {c} and target')
        miFile = pjoin(logDir, f'{c}.txt')
        pool.apply_async(func=computeMI, args=(target, img, miFile))

    pool.close()
    pool.join()

    summaryCsv = pjoin(logDir, 'similarity.csv')

    mis = []
    with open(summaryCsv, 'w') as fw:
        for c in cases:
                with open(pjoin(logDir, f'{c}.txt')) as f:
                    mi = f.read().strip()
                    fw.write(c+ ',' + mi + '\n')
                    mis.append(float(mi))


    # mis = []
    # for c in cases:
    #     with open(pjoin(logDir, f'{c}.txt')) as f:
    #         mi = f.read().strip()
    #         mis.append(float(mi))
    #
    # with open(summaryCsv, 'w') as fw:
    #     for i in np.argsort(mis):
    #         fw.write(cases[i] + ',' + str(mis[i]) + '\n')


    return summaryCsv
