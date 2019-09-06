from tbssUtil import FILEDIR, pjoin, isfile, ConfigParser, basename
from conversion import read_cases
from orderCases import orderCases
from glob import glob
import pandas as pd
from datetime import datetime
from loadFiles import read_time


def show_progress(outDir, verbose= False):

    config= ConfigParser()
    config.read(pjoin(outDir, 'log', 'config.ini'))
    modalities= [x for x in config['DEFAULT']['modalities'].split(',')]

    # read caselist
    cases = read_cases(pjoin(outDir, 'log', 'caselist.txt'))
    num_cases= len(cases)

    # read start time
    start_time_file= pjoin(outDir, 'log', 'start_time.txt')
    start_time= read_time(start_time_file)

    # read final time
    final_time_file= pjoin(outDir, 'log', 'final_time.txt')
    if isfile(final_time_file):
        final_time= read_time(final_time_file)

    else:
        final_time= datetime.now()


    print('Output directory:              ', outDir)
    print('Number of cases to process:    ', num_cases)
    for modality in modalities:
        modality_progress(outDir, modality, num_cases, verbose)


    # show duration
    duration_in_seconds= (final_time- start_time).total_seconds()

    days = divmod(duration_in_seconds, 86400)
    hours = divmod(days[1], 3600)  # Use remainder of days to calc hours
    minutes = divmod(hours[1], 60)  # Use remainder of hours to calc minutes
    seconds = divmod(minutes[1], 1)  # Use remainder of minutes to calc seconds
    print("\nTime taken so far: %d days, %d hours, %d minutes and %d seconds\n"
          % (days[0], hours[0], minutes[0], seconds[0]))


def glob_dir(num_cases, pattern):

    List= glob(pattern)
    List_actual= List.copy()

    if len(List)<num_cases:
        for i in range(num_cases-len(List)):
            List.append('-')

    return (List_actual, List)

def modality_progress(outDir, modality, num_cases, verbose):

    modDir= pjoin(outDir, modality)
    origDir= pjoin(modDir, 'origdata')
    preprocDir= pjoin(modDir, 'preproc')
    warpDir= pjoin(modDir, 'warped')
    skelDir= pjoin(modDir, 'skeleton')
    roiDir= pjoin(modDir, 'roi')


    # organize progress in a dataframe according to caseid
    print(f'\nProgress of {modality} TBSS:\n')
    df= pd.DataFrame(columns= ['origdata', 'preprocessed', 'warped', 'skeletonized', 'roi'])

    # origdata
    List_actual, List= glob_dir(num_cases, pjoin(origDir, '*.nii.gz'))
    print('origdata obtained:             ', len(List_actual))
    df['origdata']= [basename(imgPath).split('.')[0] for imgPath in List]

    # preproc
    List_actual, List= glob_dir(num_cases, pjoin(preprocDir, f'*{modality}.nii.gz'))
    print('pre-processed:                 ', len(List_actual))
    df['preprocessed']= [basename(imgPath).split('.')[0] for imgPath in List]

    # warped
    List_actual, List= glob_dir(num_cases, pjoin(warpDir, f'*{modality}_to_target.nii.gz'))
    print('registered to template space:  ', len(List_actual))
    df['warped']= [basename(imgPath).split('.')[0] for imgPath in List]

    # skeleton
    List_actual, List= glob_dir(num_cases, pjoin(skelDir, f'*{modality}_to_target_skel.nii.gz'))
    print('skeletonized:                  ', len(List_actual))
    df['skeletonized']= [basename(imgPath).split('.')[0] for imgPath in List]
    
    # roi
    List_actual, List= glob_dir(num_cases, (pjoin(roiDir, f'*{modality}_roi.csv')))
    print('roi-based stat calculated:     ', len(List_actual))
    df['roi']= [basename(imgPath).split('.')[0] for imgPath in List]

    if verbose:
        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            print('\nNOTE: Enlarge your terminal to have a better view of the dashboard\n')
            print(df)
