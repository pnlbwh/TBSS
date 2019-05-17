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

from tbssUtil import load, ConfigParser, FILEDIR, pjoin
import numpy as np
from conversion import parse_labels, num2str
import pandas as pd
from multiprocessing import Pool
import re

config = ConfigParser()
config.read(pjoin(FILEDIR,'config.ini'))
N_CPU = int(config['DEFAULT']['N_CPU'])


def average_labels(labels):

    commonLabels=[]

    for label in labels:

        labelSplit= label.lower().split('-')
        prefix= labelSplit[0]
        suffix= labelSplit[-1]

        if suffix=='l' or suffix=='r':
            commonName= label[ :-2]
        elif suffix=='left':
            commonName= label[ :-5]
        elif suffix == 'right':
            commonName = label[ :-6]
        elif prefix=='l' or prefix=='r':
            commonName= label[2: ]
        elif prefix=='left':
            commonName= label[5: ]
        elif prefix == 'right':
            commonName = label[6:]
        else:
            commonName= label

        commonLabels.append(commonName)

    return np.unique(commonLabels)


def subject_stat(imgPath, c, modality, label2name, commonLabels, labelMap, roiDir, avgFlag):

    print('Creating ROI based statistics for', imgPath)
    img= load(imgPath).get_data()

    df= pd.DataFrame(columns= ['Tract','Average','nVoxels'])
    df.loc[0]= [f'Average{modality}']+ [num2str(x) for x in [img[img>0].mean(), len(np.where(img>0)[0])]]

    stat_file= pjoin(roiDir, f'{c}_{modality}_roi.csv')
    avg_stat_file = pjoin(roiDir, f'{c}_{modality}_roi_avg.csv')

    for i ,intLabel in enumerate(label2name.keys()):
        roi = labelMap == int(intLabel)
        _roi = np.where(roi>0)

        img_roi= img*roi

        # FIXME: check correctness of ROI mean
        df.loc[i+1]= [label2name[intLabel]]+ [num2str(x) for x in [img_roi[_roi].mean(), len(_roi[0])]]

    # FIXME: save unsorted df to match with that of ENIGMA?
    df.sort_values(by='Tract').set_index('Tract').to_csv(stat_file)
    print('Made ', stat_file)


    if avgFlag:

        df_avg = pd.DataFrame(columns=['Tract', 'Average', 'nVoxels'])
        df_avg.loc[0] = df.loc[0].copy()

        row= 1
        for common in commonLabels:
            dm=[]
            num=[]

            for i, label in enumerate(label2name.values()):
                # label.split('-') to avoid confusion between CP being in both CP-R and ICP-R
                if re.search(r'\b' + common + r'\b', label):

                    df_avg.loc[row]= df.loc[i+1].copy() # Right or Left value
                    row += 1
                    dm.append(float(df.loc[i+1][1]))
                    num.append(int(df.loc[i+1][2]))

                    # since we are averaging over R/L only, len(dm) <= 2
                    if len(dm)==2:
                        # average of R/L
                        df_avg.loc[row] = [common, num2str(np.mean(dm)), str(int(np.mean(num)))]
                        row = row + 1
                        break

        # FIXME: save unsorted df_avg so Tract, Right-Tract, and Left-Tract are together?
        df_avg.sort_values(by='Tract').set_index('Tract').to_csv(avg_stat_file)
        print('Made ', avg_stat_file)


def roi_analysis(imgs, cases, args, statsDir, roiDir):

    intLabels = load(args.labelMap).get_data()
    label2name = parse_labels(np.unique(intLabels)[1:], args.lut)
    commonLabels= average_labels(label2name.values())


    pool= Pool(N_CPU)
    for c, imgPath in zip(cases, imgs):

        # subject_stat(imgPath, c, args.modality, label2name, commonLabels, intLabels, roiDir, args.avg)
        pool.apply_async(func= subject_stat, args= (imgPath, c, args.modality, label2name, commonLabels, intLabels,
                                                    roiDir, args.avg))

    pool.close()
    pool.join()


    # combine csvs
    # stat_file= pjoin(roiDir, f'{c}_{modality}_roi.csv')
    # avg_stat_file= pjoin(roiDir, f'{c}_{modality}_roi_avg.csv')
    # read one stat_file, obtain headers
    df= pd.read_csv(pjoin(roiDir, f'{cases[0]}_{args.modality}_roi.csv'))
    df_comb= pd.DataFrame(columns= np.append('Cases', df['Tract'].values))

    for i, c in enumerate(cases):
        df= pd.read_csv(pjoin(roiDir, f'{c}_{args.modality}_roi.csv'))
        # num2str() text formatting is for precision control
        df_comb.loc[i]= np.append(c, np.array([num2str(x) for x in df['Average'].values]))

    combined_stat= pjoin(statsDir, f'{args.modality}_combined_roi.csv')
    df_comb.sort_index(axis=1).set_index('Cases').to_csv(combined_stat)
    print('Made ', combined_stat)

    if args.avg:
        # read one avg_stat_file, obtain headers
        df_avg= pd.read_csv(pjoin(roiDir, f'{cases[0]}_{args.modality}_roi_avg.csv'))
        df_avg_comb= pd.DataFrame(columns= np.append('Cases', df_avg['Tract'].values))

        for i, c in enumerate(cases):
            df = pd.read_csv(pjoin(roiDir, f'{c}_{args.modality}_roi_avg.csv'))
            # num2str() text formatting is for precision control
            df_avg_comb.loc[i] = np.append(c, np.array([num2str(x) for x in df['Average'].values]))

        combined_avg_stat= pjoin(statsDir, f'{args.modality}_combined_roi_avg.csv')
        df_avg_comb.sort_index(axis=1).set_index('Cases').to_csv(combined_avg_stat)
        print('Made ', combined_avg_stat)


if __name__=='__main__':
    pass