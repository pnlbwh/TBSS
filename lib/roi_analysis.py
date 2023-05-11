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

from tbssUtil import load, ConfigParser, FILEDIR, pjoin, RAISE
import numpy as np
from conversion import parse_labels, num2str
import pandas as pd
from multiprocessing import Pool
import re

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


def subject_stat(imgPath, c, modality, label2name, commonLabels, labelMap, roiDir, avgFlag,skeletonMaskPeri):

    print('Creating ROI based statistics for', imgPath)
    img= load(imgPath).get_fdata()
    _imgNonzero= img>0

    df= pd.DataFrame(columns= ['Tract','Average','nVoxels'])

    _img_roi= img[_imgNonzero]
    df.loc[0]= [f'Average{modality}']+ [num2str(x) for x in [_img_roi.mean(), _img_roi.size]]

    stat_file= pjoin(roiDir, f'{c}_{modality}_roi.csv')
    avg_stat_file = pjoin(roiDir, f'{c}_{modality}_roi_avg.csv')

    for i ,intLabel in enumerate(label2name.keys()):
        roi = labelMap == int(intLabel)
        _roi = np.logical_and(_imgNonzero, roi)
        _img_roi= img[_roi]

        if _img_roi.size:
            df.loc[i+1]= [label2name[intLabel]]+ [num2str(x) for x in [_img_roi.mean(), _img_roi.size]]
        else:
            df.loc[i + 1] = [label2name[intLabel]] + ['0','0']
    
    roi= load(skeletonMaskPeri).get_fdata()
    _roi = np.logical_and(_imgNonzero, roi)
    _img_roi= img[_roi]
    end=len(df)
    if _img_roi.size:
        df.loc[end]=["Peri"]+ [num2str(x) for x in [_img_roi.mean(), _img_roi.size]]
    else:
         df.loc[end] = ["Peri"] + ['0','0']
            
    df.set_index('Tract').to_csv(stat_file)
    # FIXME: save unsorted df to match with that of ENIGMA?
    # df.sort_values(by='Tract').set_index('Tract').to_csv(stat_file)
    print('Made ', stat_file)


    if avgFlag:

        df_avg = pd.DataFrame(columns=['Tract', 'Average', 'nVoxels'])
        df_avg.loc[0] = df.loc[0].copy()
        df_avg.loc[1] = df.loc[end].copy()

        row= 2
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
                        df_avg.loc[row] = [common, num2str(np.average(dm, weights=num if np.sum(num) else [1,1])),
                                           str(int(np.sum(num)))]
                        row = row + 1
                        break
                
       
        # FIXME: save unsorted df_avg so Tract, Right-Tract, and Left-Tract are together?
        df_avg.sort_values(by='Tract').set_index('Tract').to_csv(avg_stat_file)
        print('Made ', avg_stat_file)


def roi_analysis(imgs, cases, args, roiDir, N_CPU):

    intLabels = load(args.labelMap).get_data()
    label2name = parse_labels(np.unique(intLabels)[1:], args.lut)
    commonLabels= average_labels(label2name.values())

    pool= Pool(N_CPU)
    for c, imgPath in zip(cases, imgs):

        # subject_stat(imgPath, c, args.modality, label2name, commonLabels, intLabels, roiDir, args.avg)
        pool.apply_async(func= subject_stat, args= (imgPath, c, args.modality, label2name, commonLabels, 
                                                    intLabels, roiDir, args.avg, args.skeletonMaskPeri), error_callback= RAISE)

    pool.close()
    pool.join()


    # combine csvs
    # stat_file= pjoin(roiDir, f'{c}_{modality}_roi.csv')
    # avg_stat_file= pjoin(roiDir, f'{c}_{modality}_roi_avg.csv')
    # read one stat_file, obtain headers
    df= pd.read_csv(pjoin(roiDir, f'{cases[0]}_{args.modality}_roi.csv'))
    df_comb= pd.DataFrame(columns= np.append(['Cases','Weighted_avg','Core_weighted_avg'], df['Tract'].values))
    print(df_comb)
    
    for i, c in enumerate(cases):
        df= pd.read_csv(pjoin(roiDir, f'{c}_{args.modality}_roi.csv'))
        core=df
        core=core.drop(core[core['Tract'] =='Peri'].index, inplace = False)
        # num2str() text formatting is for precision control
        total_vox=sum(df['nVoxels'].values)
        df['weight']=df['Average'].values*(df['nVoxels'].values/total_vox)
        weighted_avg=sum(df['weight'].values)

        total_core=sum(core['nVoxels'].values)
        core['weight']=core['Average'].values*(core['nVoxels'].values/total_core)
        core_weighted_avg=sum(core['weight'].values)
        print(np.append([c,weighted_avg,core_weighted_avg], np.array([num2str(x) for x in df['Average'].values])))
        df_comb.loc[i]= np.append([c,weighted_avg,core_weighted_avg], np.array([num2str(x) for x in df['Average'].values]))

    combined_stat= pjoin(args.statsDir, f'{args.modality}_combined_roi.csv')
    df_comb.sort_index(axis=1).set_index('Cases').to_csv(combined_stat)
    print('Made ', combined_stat)

    if args.avg:
        # read one avg_stat_file, obtain headers
        df_avg= pd.read_csv(pjoin(roiDir, f'{cases[0]}_{args.modality}_roi_avg.csv'))
        df_avg_comb= pd.DataFrame(columns= np.append(['Cases','Weighted_avg','Core_weighted_avg'], df_avg['Tract'].values))

        for i, c in enumerate(cases):
            df = pd.read_csv(pjoin(roiDir, f'{c}_{args.modality}_roi_avg.csv'))
            # num2str() text formatting is for precision control
            df_avg_comb.loc[i] = np.append([c,weighted_avg,core_weighted_avg], np.array([num2str(x) for x in df['Average'].values]))

        combined_avg_stat= pjoin(args.statsDir, f'{args.modality}_combined_roi_avg.csv')
        df_avg_comb.sort_index(axis=1).set_index('Cases').to_csv(combined_avg_stat)
        print('Made ', combined_avg_stat)


if __name__=='__main__':
    pass

