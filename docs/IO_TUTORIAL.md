![](./pnl-bwh-hms.png)

[![DOI](https://zenodo.org/badge/doi/10.5281/zenodo.2662497.svg)](https://doi.org/10.5281/zenodo.2662497) [![Python](https://img.shields.io/badge/Python-3.6-green.svg)]() [![Platform](https://img.shields.io/badge/Platform-linux--64%20%7C%20osx--64-orange.svg)]()

*TBSS* repository is developed by Tashrif Billah, Sylvain Bouix, and Ofer Pasternak, Brigham and Women's Hospital (Harvard Medical School).

If this repository is useful in your research, please cite as below: 

Billah, Tashrif; Bouix, Sylvain; Pasternak, Ofer; Generalized Tract Based Spatial Statistics (TBSS) pipeline,
https://github.com/pnlbwh/tbss, 2019, DOI: https://doi.org/10.5281/zenodo.2662497

See [documentation](./TUTORIAL.md) for details.

This software is also available as *Docker* and *Singularity* containers. See [tbss_containers](https://github.com/pnlbwh/tbss_containers) for details.


Table of Contents
=================

   * [What is PNL TBSS](#what-is-pnl-tbss)
   * [Bash setup](#bash-setup)
   * [Running TBSS](#running-tbss)
      * [Mandatory inputs](#mandatory-inputs)
         * [1. -i INPUT](#1--i-input)
         * [2. --modality MODALITY](#2---modality-modality)
         * [3. -C CASELIST](#3--c-caselist)
         * [4. -o OUTDIR](#4--o-outdir)
         * [5. Branch name](#5-branch-name)
      * [Examples](#examples)
         * [1. ENIGMA](#1-enigma)
         * [2. Study template](#2-study-template)
         * [3. TBSS with DWI image](#3-tbss-with-dwi-image)
      * [Status check](#status-check)
   * [Troubleshooting](#troubleshooting)
   * [Outlier analysis](#outlier-analysis)

Table of Contents created by [gh-md-toc](https://github.com/ekalinin/github-markdown-toc)


# What is PNL TBSS

* Combines and automates [various steps](https://github.com/pnlbwh/TBSS/blob/master/docs/TUTORIAL.md#overview)

* Gives user flexibility in terms of naming/organizing input data

* Consists of [various branches](https://github.com/pnlbwh/TBSS/blob/master/docs/TUTORIAL.md#branchestemplates)

    * enigma
    * fmrib
    * studyTemplate
    * user

* Produce structured outputs


# Bash setup

To be able to try the tutorial hands-on, we need you to setup your terminal first.

* Log in to `grx{04,05,06}.research.partners.org` using NoMachine

* Open a basic terminal
> mv ~/.bashrc ~/.bashrc.bak

* Set up environment

    * FSl>=5.0.11
    * Python>=3.6

> source /data/pnl/soft/pnlpipe3/bashrc3

* Define the following alias

```
cd /data/pnl/kcho/tbss_example
alias tudir="cd $PWD"
alias tbss_all=/data/pnl/soft/pnlpipe3/tbss/lib/tbss_all
```

* Observe the input data

```
ls FA_maps
ls FAt_maps
ls FW_maps
ls data/*
```

# Running TBSS

> tbss_all --help


## Mandatory inputs

```
-i INPUT
--modality MODALITY
-c CASELIST
-o OUTDIR
--enigma or --fmrib or --studyTemplate or yourOwnTemplates
--ncpu 16 # default is 4, using just bsub will not help unless you specify --ncpu
```

**NOTE** See [nonFA](https://github.com/pnlbwh/TBSS/blob/master/docs/TUTORIAL.md#3-nonfa-tbss) examples to know about what few arguments are required for nonFA TBSS.

### 1. -i INPUT

* [all modalities together](#all-modalities-together)
* [just FA](#just-fa)
* [separate nonFA or future nonFA](#separate-nonfa-or-future-nonfa)
* [Imagelist creation](#imagelist-creation)
   * [one modality](#one-modality)
   * [multiple modalities](#multiple-modalities)
   

#### all modalities together

(i) directory as input
```
-i FA_maps,FAt_maps,FW_maps # 3 directories corresponding to 3 modalities, first directory is of FA images
--modality FA,FAt,FW        # first modality FA is case-sensitive, rest can be any
```

(ii) image list as input

Useful when you have your diffusion measures in different directories. You do not need to copy them 
to one directory i.e. FA_maps. Thus you can prevent data duplication, save some space, and yet 
run TBSS gracefully.

```
-i data/imagelist.csv # 3 columns corresponding to 3 modalities, first column is of FA images
--modality FA,FAt,FW  # first modality FA is case-sensitive, rest can be any 
```

#### just FA

(i) directory as input
```
-i FA_maps
--modality FA # first modality FA is case-sensitive
```

(ii) image list as input

Useful when you have your diffusion measures in different directories. You do not need to copy them 
to one directory i.e. `FA_maps`. Thus you can prevent data duplication, save some space, and yet 
run TBSS gracefully.

```
-i data/fa_list.csv # 1 column for FA only
--modality FA       # first modality FA is case-sensitive
```

#### separate nonFA or future nonFA

Upon running FA TBSS, you can run nonFA TBSS separately. This feature is useful when you have not decided about all the 
modalities for which you want to run nonFA TBSS. Moreover, it spares you from requiring to run non-linear 
ANTs registration again at a later time. Thus, you save time taken in registration, 
prevent duplication of registration files, and save some space.

```
-i data/fat_fw_list.csv # 2 columns for FAt and FW
--modality FAt,FW
-o enigma-tbss/
```

```
-i FAt_maps,FW_maps
--modality FAt,FW
--xfmrDir enigma-tbss/transform
```

```
-i fat_list.csv
--modality FAt
--xfmrDir enigma-tbss/transform
```

```
-i FW_maps
--modality FW
--xfmrDir enigma-tbss/transform
```

#### Imagelist creation

Let's try to create a few lists from the `tudir`:

> tree data/C001419
```
data/C001419
├── C001419_FW.nii.gz
├── C001419_TensorDTI_FWCorrected_decomp_FAt.nii.gz
└── C001419_TensorDTINoNeg_decomp_FA.nii.gz
```

##### one modality

> ls \`pwd\`/???????/*_FW.nii.gz > /tmp/${USER}_fw_list.csv

##### multiple modalities

```bash
cd data
rm /tmp/${USER}_imagelist.csv

for caseid in `ls -d ???????`;
do
    caseid=${caseid%/};
    echo `pwd`/${caseid}/${caseid}_TensorDTINoNeg_decomp_FA.nii.gz,`pwd`/${caseid}/${caseid}_TensorDTI_FWCorrected_decomp_FAt.nii.gz,`pwd`/${caseid}/${caseid}_FW.nii.gz >> /tmp/${USER}_imagelist.csv;
done
```

### 2. --modality MODALITY

```
FA          # FA is case-sensitive
FA,MD,AD,RD # for multi-modalities, FA must be the first modality
FW,FAt      # FA was run before
```

### 3. -C CASELIST

* One `caseid` in each line
* caseids from caselist is used to find images in input directories and relevant transform files down the pipeline
* each image file name should have `caseid` somewhere in its name:

```
My_caseid_FA.nii.gz
caseid_Eddy_FA.nii.gz
sub-caseid_DTI_Tensor_FA.nii.gz
```

```
cd data

ls -d C00???? | sed 's+/++' > /tmp/${USER}_caselist.txt
ls -d P00???? | tr -d '/'   >> /tmp/${USER}_caselist.txt

# or using a single regex pattern

ls -d ??????? | tr -d '/'   > /tmp/${USER}_caselist.txt
```

**NOTE** `sed` and `tr` are two ways to trim the trailing slash appearing at the end of the `caseid` directory when 
listed using `ls -d`.

### 4. -o OUTDIR

* provide only when FA is one of your modalities
* accepts relative path

> -o enigma-tbss # resolves to `pwd`/enigma-tbss


### 5. Branch name

https://github.com/pnlbwh/TBSS/blob/master/docs/TUTORIAL.md#branchestemplates


## Examples

### 1. ENIGMA

Let's come back to the tutorial directory:

> tudir

* All modalities together

```
tbss_all \
-o /tmp/${USER}_enigma/ \
-i data/imagelist.csv \
--modality FA,FAt,FW \
-c caselist.txt \
--enigma \
--ncpu 2
```

* FA only
```
tbss_all \
-o /tmp/${USER}_enigma/ \
-i FA_maps \
--modality FA \
-c caselist.txt \
--enigma
```

* Separate nonFA
```
tbss_all \
-i FW_maps \
--modality FW \
-o /tmp/${USER}_enigma/ \
--enigma \
--ncpu 2
```

(i) Resource profile

See [here](TUTORIAL.md#resource-profile) to learn how to plan for `--ncpu` to maximally parallelize your processes. 


(ii) Inspect outputs:

```
tudir
tree enigma-tbss/ -L 2 -I "*.nii.gz|*log|*mat"
```
```
├── FA
│   ├── origdata
│   ├── preproc
│   ├── roi
│   ├── skeleton
│   ├── slicesdir
│   └── warped
├── FAt
│   ├── origdata
│   ├── preproc
│   ├── roi
│   ├── skeleton
│   ├── slicesdir
│   └── warped
├── FW
│   ├── origdata
│   ├── preproc
│   ├── roi
│   ├── skeleton
│   ├── slicesdir
│   ├── tbss_skeleton_test.sh
│   └── warped
├── stats
│   ├── FA_combined_roi_avg.csv
│   ├── FA_combined_roi.csv
│   ├── FAt_combined_roi_avg.csv
│   ├── FAt_combined_roi.csv
│   ├── FW_combined_roi_avg.csv
│   └── FW_combined_roi.csv
└── transform
```

```
cd /data/pnl/kcho/tbss_example/enigma-tbss/FA
for i in *; do tree $i -L 2 | head -3; done
```

```
origdata
├── C001419.nii.gz
├── C001424.nii.gz
preproc
├── C001419_FA_mask.nii.gz
├── C001419_FA.nii.gz
roi
├── C001419_FA_roi_avg.csv
├── C001419_FA_roi.csv
skeleton
├── C001419_FA_to_target_skel.nii.gz
├── C001424_FA_to_target_skel.nii.gz
slicesdir
├── C001419.png
├── C001424.png
warped
├── C001419_FA_to_target.nii.gz
├── C001424_FA_to_target.nii.gz

```


Pay attention to `enigma-tbss/log/commands.txt`. This file is used to run nonFA TBSS 
under the same settings of previous FA TBSS.

(iii) fsleyes visualization

* Before registration data are not aligned
```
cd /data/pnl/kcho/tbss_example/enigma-tbss/FA/origdata
fsleyes C001419.nii.gz P003785.nii.gz
```

* After registration, data are aligned

```
cd /data/pnl/kcho/tbss_example/enigma-tbss/FA/warped
fsleyes C001419_FA_to_target.nii.gz P003785_FA_to_target.nii.gz
```

(iv) skeleton superimposed on FA

> firefox enigma-tbss/FA/slicesdir/summary.html



### 2. Study template

```
tbss_all \
-o /tmp/${USER}_study/ \
-i data/imagelist.csv \
--modality FA,FAt,FW \
-c caselist.txt \
--studyTemplate \
--ncpu 2
```

```
tudir
cd study-tbss/
ls template
```

* `template0.nii.gz` is in subject space, not in any standard space, provide `-s SPACE` to bring to a standard space

* ROI based analysis is not done by default, provide `-s SPACE --lut LUT --labelMap LABELMAP`


### 3. TBSS with DWI image

https://github.com/pnlbwh/TBSS/blob/master/docs/TUTORIAL.md#1-with-dwimask-image-list

```
-i INPUT.csv    # a txt/csv file with dwi,mask pair in each line
--generate      # FA,MD,AD,RD diffusion measures are created
--modality FA   # but you get a choice to run TBSS on one (or few) of the modalities
-c caselist.txt
--enigma
```


## Status check

```
tudir
tbss_all --status -o enigma-tbss
tbss_all --status -o study-tbss
```

# Troubleshooting

https://github.com/pnlbwh/TBSS/blob/master/docs/TUTORIAL.md#troubleshooting

(i) Made a mistake or program failed

Remove the output directory of the modality for which it failed only:

`rm enigma-tbss/FW`

And retry ...

(ii) Re-run utilizing previous registration files

This feature is useful when you want to adjust a single parameter i.e. `SKEL_THRESH`. 
With adjusted parameters, TBSS will re-run bypassing registration but re-create all other files.

(iii) `--noHtml`

(iv) `--ncpu`

Reduce it

(v) `--noAllSkeleton`

See [documentation](./TUTORIAL.md) for details about them.

# Outlier analysis

* See details at https://github.com/pnlbwh/freesurfer-analysis

* Analyze statistics
```
tudir
/data/pnl/soft/pnlpipe3/freesurfer-analysis/scripts/generate-summary.py -i enigma-tbss/stats/FA_combined_roi_avg.csv -o /tmp/FA-outliers/
```

* View outlier summary
> firefox http://localhost:8050/

