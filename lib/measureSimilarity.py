from tbssUtil import pjoin, RAISE
from plumbum.cmd import MeasureImageSimilarity, head, cut
from plumbum import FG
from multiprocessing import Pool

def computeMI(target, img, miFile):
    # $ antsRegistration --version
    # 2.2.0
    (MeasureImageSimilarity['-d', '3',
                            '-m', 'MI[{},{},1,256]'.format(target, img)] > miFile) & FG


    # $ antsRegistration --version
    # 2.1.0
    # (MeasureImageSimilarity['3', '2', target, img] | head['-n', '-2'] | cut['-d ', '-f6'] > miFile)()

def measureSimilarity(imgs, cases, target, logDir, ncpu):

    pool = Pool(ncpu)
    for img,c in zip(imgs,cases):
        print(f'MI between {c} and target')
        miFile = pjoin(logDir, f'{c}_MI.txt')
        pool.apply_async(func=computeMI, args=(target, img, miFile), error_callback= RAISE)

    pool.close()
    pool.join()

    summaryCsv = pjoin(logDir, 'similarity.csv')

    mis = []
    with open(summaryCsv, 'w') as fw:
        for c in cases:
                with open(pjoin(logDir, f'{c}_MI.txt')) as f:
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

if __name__== '__main__':
    pass
