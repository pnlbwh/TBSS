from tbssUtil import pjoin, RAISE, environ
from plumbum.cmd import antsRegistration, MeasureImageSimilarity, head, cut
from plumbum import FG
from multiprocessing import Pool

# determine ANTS_VERSION
# $ antsRegistration --version
#   ANTs Version: 2.2.0.dev233-g19285
#   Compiled: Sep  2 2018 23:23:33

antsVerFile='/tmp/ANTS_VERSION_'+environ['USER']
if not antsVerFile:
    (antsRegistration['--version'] > antsVerFile) & FG

with open(antsVerFile) as f:
      content=f.read().split('\n')
      ANTS_VERSION= content[0].split()[-1]

def computeMI(target, img, miFile):

    if ANTS_VERSION <= '2.1.0':
        (MeasureImageSimilarity['3', '2', target, img] | head['-n', '-2'] | cut['-d ', '-f6'] > miFile)()

    else:
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
