![](doc/pnl-bwh-hms.png)

[![DOI](https://zenodo.org/badge/doi/10.5281/zenodo.2662497.svg)](https://doi.org/10.5281/zenodo.2662497) [![Python](https://img.shields.io/badge/Python-3.6-green.svg)]() [![Platform](https://img.shields.io/badge/Platform-linux--64%20%7C%20osx--64-orange.svg)]()

*TBSS* repository is developed by Tashrif Billah, Sylvain Bouix, and Ofer Pasternak, Brigham and Women's Hospital (Harvard Medical School).

If this repository is useful in your research, please cite as below: 

Billah, Tashrif; Bouix, Sylvain; Pasternak, Ofer; Generalized Tract Based Spatial Statistics (TBSS) pipeline,
https://github.com/pnlbwh/tbss, 2019, DOI: https://doi.org/10.5281/zenodo.2662497


Table of Contents
=================

   * [Table of Contents](#table-of-contents)
   * [Introduction](#introduction)
   * [Template](#template)
      * [1. --enigma](#1---enigma)
      * [2. --fmrib](#2---fmrib)
      * [3. --studyTemplate](#3---studytemplate)
      * [4. User template](#4-user-template)
   * [Space](#space)
   * [Caselist](#caselist)
   * [Input](#input)
      * [1. List](#1-list)
         * [i. With dwi/mask image list](#i-with-dwimask-image-list)
         * [ii. With diffusivity image list](#ii-with-diffusivity-image-list)
         * [2. Directory](#2-directory)
      * [3. With diffusivity image directory directory](#3-with-diffusivity-image-directory-directory)
   * [List of outputs](#list-of-outputs)
      * [1. Folders](#1-folders)
      * [2. Files](#2-files)
         * [i. FA/MD/AD/RD](#i-famdadrd)
            * [a. preproc](#a-preproc)
            * [b. origdata](#b-origdata)
            * [c. warped](#c-warped)
            * [d. skeleton](#d-skeleton)
            * [e. roi](#e-roi)
         * [ii. transform/template](#ii-transformtemplate)
         * [iii. log](#iii-log)
         * [iv. stats](#iv-stats)
   * [Dependencies](#dependencies)
   * [Installation](#installation)
      * [1. Install prerequisites](#1-install-prerequisites)
         * [i. Check system architecture](#i-check-system-architecture)
         * [ii. Python 3](#ii-python-3)
         * [iii. FSL](#iii-fsl)
         * [iv. ANTs](#iv-ants)
      * [2. Install pipeline](#2-install-pipeline)
      * [3. Configure your environment](#3-configure-your-environment)
   * [Running](#running)
      * [Usage](#usage)
      * [TBD](#tbd)
   * [multi-modality TBSS](#multi-modality-tbss)
   * [List creation](#list-creation)
      * [1. imagelist](#1-imagelist)
      * [2. caselist](#2-caselist)
   * [Tests](#tests)
      * [1. pipeline](#1-pipeline)
      * [2. unittest](#2-unittest)
   * [ROI analysis](#roi-analysis)
   * [Multi threading](#multi-threading)
   * [NRRD support](#nrrd-support)
   * [Misc.](#misc)
   * [Reference](#reference)


Table of Contents created by [gh-md-toc](https://github.com/ekalinin/github-markdown-toc)



# Introduction

This is Generalized Tract Based Spatial Statistics (TBSS) pipeline,
encompassing different protocols such as [ENIGMA](http://enigma.ini.usc.edu/wp-content/uploads/DTI_Protocols/ENIGMA_TBSS_protocol_USC.pdf) 
and [FSL](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/TBSS/UserGuide). It is elegantly designed so you no longer have to 
deal with naming your folders/files according to a protocol. It uses some command line tools relevant to 
skeleton creation from FSL while replacing all FSL (i.e `flirt`, `applyWarp` etc) registration steps by [ANTs](https://github.com/ANTsX/ANTs). 
In a nutshell, this pipeline should facilitate an user in running TBSS study by giving more liberty with inputs. 
Moreover, it harnesses multiprocessing capability from Python making the program significantly faster than any 
job scheduling framework (i.e lsf).

![](doc/tbss-ofer-flowchart.png)



# Template

The pipeline has four branches:


## 1. --enigma

ENIGMA provided templates are used with this argument:
    
    enigmaDir= pjoin(LIBDIR, 'data', 'enigmaDTI')
    args.template = pjoin(enigmaDir, 'ENIGMA_DTI_FA.nii.gz')
    args.templateMask = pjoin(enigmaDir, 'ENIGMA_DTI_FA_mask.nii.gz')
    args.skeleton = pjoin(enigmaDir, 'ENIGMA_DTI_FA_skeleton.nii.gz')
    args.skeletonMask = pjoin(enigmaDir, 'ENIGMA_DTI_FA_skeleton_mask.nii.gz')
    args.skeletonMaskDst = pjoin(enigmaDir, 'ENIGMA_DTI_FA_skeleton_mask_dst.nii.gz')
    args.lut = pjoin(enigmaDir, 'ENIGMA_look_up_table.txt')
    
In addition, the following atlas is used for ROI based analysis:
    
    args.labelMap = pjoin(fslDataDir, 'atlases', 'JHU', 'JHU-ICBM-labels-1mm.nii.gz')

## 2. --fmrib

FSL provided templates are used with this argument:
    
    args.template= pjoin(fslDataDir, 'standard', 'FMRIB58_FA_1mm.nii.gz')
    args.skeleton= pjoin(fslDataDir, 'standard', 'FMRIB58_FA-skeleton_1mm.nii.gz')

However, [FreeSurferColorLUT.txt](https://surfer.nmr.mgh.harvard.edu/fswiki/FsTutorial/AnatomicalROI/FreeSurferColorLUT) is used in this branch.
    
On the other hand, this branch does not do ROI based analysis by default. If wanted, the 
user should specify an atlas and corresponding space (if atlas and templates are in different space) 
as follows:

    --labelMap atlas.nii.gz --space MNI.nii.gz
    

## 3. --studyTemplate

With this branch, a study-specific template is created using `antsMultivariateTemplateConstruction2.sh`. 
`tbss_1_preproc INPUTDIR/*.nii.gz` pre-processes the given FA images. 
The pre-processed FA images are used in template construction. Again, the use should provide 
a set of FA images for study specific template construction. 

## 4. User template

Finally, the user can specify any or all of the following:
    
    --template TEMPLATE                 an FA image template (i.e ENIGMA, IIT), 
                                        if not specified, ANTs template will be created from provided images, 
                                        for ANTs template creation, you must provide FA images, 
                                        once ANTs template is created, you can run TBSS on 
                                        non FA images using that template
                                        
    --templateMask TEMPLATEMASK         mask of the FA template, if not provided, one will be created
        
    --skeleton SKELETON                 skeleton of the FA template, if not provided, one will be created
                                        
    --skeletonMask SKELETONMASK         mask of the provided skeleton
    
    --skeletonMaskDst SKELETONMASKDST   skeleton mask distance map
    

** NOTE ** Attributes provided as user templates are mutually exclusive to the ones default with branches specified above. 
In other words, branch specific templates have precedence over user template. 
For example, if `--enigma` is specified, it will override `--template`, `--skeleton` etc specified again.
However, since `--fmrib` comes with only `--template` and `--skeleton`, 
you may specify `--templateMask`, `--skeletonMask` etc. with it. 


# Space

Provided or created template can be projected to a standard space. For human brain, it should be projected to MNI space. 
However, for rat/other brains, it may be some other standard space. 

If ROI based analysis is to be done using a White-Matter atlas, the template should be projected to the space of the atlas.

# Caselist

Files in each subdirectory start with a caseid obtained from `--caselist`. If a caselist is not specified, then one 
is created from the input images. Such caselist comprise the basenames of images without extension. For example, if 
image path is: `/path/to/001/image001.nii.gz`, then created caseid would be `image001` only.

# Input

The TBSS pipeline requires input images i.e. FA, MD etc. You may specify the input images as a list 
or as a directory which contains them.

## 1. List

### i. With dwi/mask image list

For convenience, TBSS can start by creating diffusivity measures: FA, MD, AD, and RD. To let the pipeline create them, 
specify your input DWI/Mask in a text file as follows:

    -i INPUT.csv            a txt/csv file
                            with dwi1,mask1\ndwi2,mask2\n...

In addition, provide the `--generate` flag.

Then, FA, MD, AD, RD are created using either DIPY/FSL diffusion tensor models. Then, TBSS is done for 
specified `--modality`.


### ii. With diffusivity image list 

Alternatively, you can specify a list of diffusivity images sitting in different directories:

                            a txt/csv file with
    -i INPUT.csv            ModImg1\nModImg2\n... ; TBSS will be done for specified Modalities

The pipeline will organize them in proper [directory structure](#1-folders).


### 2. Directory

Finally, to be compatible with FSL/ENGIMA protocols, you may organize your images in separate directories. 
Then, you can provide the directory to run TBSS on:
    
    --modality FA,MD,... dir/of/FA/images,dir/of/MD/images,...
    
**NOTE** When specifiying multiple modalities at a time, make sure to correspond your directory to the right modality.

## 3. With diffusivity image directory directory

Alternatively, a directoy of modality images can be specified: 

      -i INPUT              a directory with one particular Modality={FA,MD,AD,RD,...} images


# List of outputs

Several files are created down the pipeline. They are organized with following folder hierarchy and naming:
    
## 1. Folders
    
    outDir
       |
    ------------------------------------------------------------------------------------------------------
       |           |             |                |        |       |                   |           |
       |           |             |                |        |       |                   |           |
    transform   template        FA                MD       AD      RD                 log        stats
                                 |       (same inner file structure as that of FA)
                                 |
                    ----------------------------------------
                     |         |         |       |        |
                    preproc  origdata  warped  skeleton  roi
    
    copy all FA into FA directory
    put all preprocessed data into preproc directory
    keep all warp/affine in transform directory
    output all warped images in warped directory
    output all skeletons in skel directory
    output ROI based analysis files in roi directory
    save all ROI statistics, mean, and combined images
    
        
    
## 2. Files
    
The following directories are created inside user specified output directory. Files residing in the nested directories 
are explained below:

### i. FA/MD/AD/RD

TBSS run on one or more specified modalities. The FA, MD, .. directories correspond to the modalities. In each modality 
directory, there are five sub-directories:
    
                FA
                 |
                 |
    ----------------------------------------
     |         |         |       |        |
    preproc  origdata  warped  skeleton  roi
    
    copy all FA into FA directory
    put all preprocessed data into preproc directory
    keep all warp/affine in transform directory
    output all warped images in warped directory
    output all skeletons in skel directory
    output ROI based analysis files in roi directory
    

Files in each subdirectory start with a caseid obtained from `--caselist`.

#### a. preproc

Contains all [`tbss_1_preproc`] processed data.

#### b. origdata

Contains raw diffusivity data. 

In fact `tbss_1_preproc` categorizes raw and preprocessed data into `origdata` and `FA` directories, respectively. 
The pipeline renames `FA` as `preproc` to be harmonious with the genre of data contained within.

#### c. warped

Preprocessed data are warped to template/standard space applying warp and affine obtained from registering each subject 
to the template. `warped` directory contains warped data.

#### d. skeleton

Provided/created skeleton is projected upon each subject. This directory contains projected skeletons in subject space.

#### e. roi

If you choose to do ROI based analysis providing a `--labelMap`, then a `*_roi.csv` file is created for each case containing 
region based statistics. Additionally, if you use `--avg` flag, RIGHT/LEFT regions in the ROIs are averaged. The averaged 
statistics are saved in `*_roi.csv` file.


Several files are created down the pipeline. They are organized with proper folder hierarchy and naming:


    outDir
       |
    -------------------------------------------------------------------------
       |           |          |       |       |       |        |        |
       |           |          |       |       |       |        |        |
    transform   template     FA       MD      AD      RD      log     stats
    
### ii. transform/template

If a template is given, input images are registered with the template. On the other hand, if a template is not 
given/`--studyTemplate` branch is specified, a template is created in the pipeline. Corresponding transform files: 
`*Affine.mat` and `*Warp*.nii.gz` are created in `transform/template` directory.



Moreover, same directory is used to store transform files if a template is further registered to another space (i.e. MNI).

### iii. log

ANTs registration logs are stored in this directory for each case starting with a caseid. However, the user can print 
all the outputs to `stdout` by `--verbose` option.


### iv. stats

As the name suggests, all statistics are saved in this directory. Statistics include mean and combined modality images, 
csv file containing summary of region based statistics etc.


# Dependencies

* ANTs = 2.2.0
* FSL = 5.0.11
* numpy = 1.16.2
* pandas = 1.2.1
* dipy = 0.16.0
* nibabel = 2.3.0
* pynrrd = 0.3.6
* conversion = 2.0

**NOTE** The above versions were used for developing the repository. However, *tbss* should work on 
any advanced version. 


# Installation

## 1. Install prerequisites

You may ignore installation instruction for any software module that you have already.

### i. Check system architecture

    uname -a # check if 32 or 64 bit

### ii. Python 3

Download [Miniconda Python 3.6 bash installer](https://docs.conda.io/en/latest/miniconda.html) (32/64-bit based on your environment):
    
    sh Miniconda3-latest-Linux-x86_64.sh -b # -b flag is for license agreement

Activate the conda environment:

    source ~/miniconda3/bin/activate # should introduce '(base)' in front of each line

### iii. FSL

Follow the [instruction](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FslInstallation) to download and install FSL.


### iv. ANTs

(*Preferred*) You should install pre-complied ANTs from [Aramislab](https://anaconda.org/Aramislab/ants):
    
    conda install -c aramislab ants
    
Installation with conda is more manageable. It will put the ANTs commands/scripts in your path when you do:
    
    source ~/miniconda3/bin/activate
    

    
Alternatively, you can build ANTs from [source](https://github.com/ANTsX/ANTs).

    
## 2. Install pipeline

Now that you have installed the prerequisite software, you are ready to install the pipeline:

    git clone https://github.com/pnlbwh/tbss && cd tbss
    ./install setup test
    
You


Alternatively, if you already have ANTs, you can continue using your python environment by directly installing 
the prerequisite libraries:

    pip install -r requirements.txt --upgrade


## 3. Configure your environment

Make sure the following executables are in your path:

    antsMultivariateTemplateConstruction2.sh
    antsApplyTransforms
    antsRegistrationSyNQuick.sh
    tbss_1_preproc
    
You can check them as follows:

    which tbss_1_preproc
    
If any of them does not exist, add that to your path:

    export PATH=$PATH:/directory/of/executable
    
ANTs commands should be in `~/miniconda3/pkgs/ants-2.2.0-0/bin` and/or `~/miniconda3/bin/` directories. 
If they are not in your path already, use export `PATH=$PATH:miniconda3/pkgs/ants-2.2.0-0/bin` 
to put all the commands in your path. However, if you choose to use pre-installed ANTs scripts, 
you may need to define [ANTSPATH](https://github.com/ANTsX/ANTs/wiki/Compiling-ANTs-on-Linux-and-Mac-OS#set-path-and-antspath)


# Running

## Usage
Upon successful installation, you should be able to see the help message

`$ lib/tbss-pnl --help`
    
    TBSS at PNL encapsulating different protocols i.e FSL, ENIGMA, ANTs template etc.

    optional arguments:
    -h, --help            show this help message and exit
    --modality MODALITY   Modality={FA,MD,AD,RD ...} of images to run TBSS on
    
                          (i) single modality analysis:
                          you must run --modality FA first, then you can run for other modalities such as --modality AD
    
                          (ii) multi modality analysis:
                          first modality must be FA, and then the rest i.e --modality FA,MD,AD,RD,...
                          files from FA TBSS analysis are used in rest of the modalities
    -i INPUT, --input INPUT
                          (i) DWI images and masks:
                          a txt/csv file with dwi1,mask1\ndwi2,mask2\n... ; TBSS will start by creating FA, MD, AD, and RD;
                          additionally, use --generate flag
    
                          (ii) single modality analysis:
                          a directory with one particular Modality={FA,MD,AD,RD,...} images, or
                          a txt/csv file with ModImg1\nModImg2\n...
                          TBSS will be done for specified Modality
    
                          (iii) multi modality analysis:
                          comma-separated multiple input directories corresponding to the sequence of --modality, or
                          a txt/csv file with Mod1_Img1,Mod2_Img1,...\nMod1_Img2,Mod2_Img2,...\n... ;
                          TBSS will be done for FA first, and then for other modalities.
    --generate            generate diffusion measures for dwi1,mask1\n... list
    
    -c CASELIST, --caselist CASELIST
                          caselist.txt where each line is a subject ID
    -o OUTDIR, --outDir OUTDIR
                          where all outputs are saved in an organized manner
    
    --studyTemplate       create all of template, templateMask, skeleton, skeletonMask, and skeletonMaskDst
    --enigma              use ENGIMA provided template, templateMask, skeleton, skeletonMask, and skeletonMaskDst, do JHU white matter atlas based ROI analysis using ENIGMA look up table
    --fmrib               use FSL provided template, and skeleton
    
    
    --template TEMPLATE   an FA image template (i.e ENIGMA, IIT), if not specified, ANTs template will be created from provided images, for ANTs template creation, you must provide FA images, once ANTs template is created, you can run TBSS on non FA images using that template
    --templateMask TEMPLATEMASK
                          mask of the FA template, if not provided, one will be created
    --skeleton SKELETON   skeleton of the FA template, if not provided, one will be created
    --skeletonMask SKELETONMASK
                          mask of the provided skeleton
    --skeletonMaskDst SKELETONMASKDST
                          skeleton mask distance map
    -s SPACE, --space SPACE
                          you may register your template (including ANTs) to another standard space i.e MNI, not recommended for a template that is already in MNI space (i.e ENIGMA, IIT)
    
    -l LABELMAP, --labelMap LABELMAP
                          labelMap (atlas) in standard space (i.e any WhiteMatter atlas from ~/fsl/data/atlases/
    --lut LUT             look up table for specified labelMap (atlas), default: FreeSurferColorLUT.txt
    
    --qc                  halt TBSS pipeline to let the user observe quality of registration
    --avg                 average Left/Right components of tracts in the atlas
    --force               overwrite existing directory/file
    --verbose             print everything to STDOUT
    
    -n NCPU, --ncpu NCPU  number of processes/threads to use (-1 for all available, may slow down your system)
    
    --SKEL_THRESH SKEL_THRESH
                          threshold for masking skeleton and projecting FA image upon the skeleton
    --SEARCH_RULE_MASK SEARCH_RULE_MASK
                          search rule mask for nonFA TBSS, see "tbss_skeleton --help"

## TBD

# multi-modality TBSS

Unlike requiring to save FA TBSS files with a particular name as directed by some protocol, this pipeline is capable of 
running multi-modality TBSS. All you have to do is to make sure, first modality in the specified modalities is FA and 
corresponding input images are FA.

    --modality MODALITY         Modality={FA,MD,AD,RD ...} of images to run TBSS on
            
                                (i) single modality analysis:
                                you must run --modality FA first, then you can run for other modalities such as --modality AD
            
                                (ii) multi modality analysis:
                                first modality must be FA, and then the rest i.e --modality FA,MD,AD,RD,...
                                files from FA TBSS analysis are used in rest of the modalities
                                
    -i INPUT, --input INPUT
                                (i) DWI images and masks:
                                a txt/csv file with dwi1,mask1\ndwi2,mask2\n... ; TBSS will start by creating FA, MD, AD, and RD;
                                additionally, use --generate flag
            
                                (ii) single modality analysis:
                                a directory with one particular Modality={FA,MD,AD,RD,...} images, or
                                a txt/csv file with ModImg1\nModImg2\n...
                                TBSS will be done for specified Modality
            
                                (iii) multi modality analysis:
                                comma-separated multiple input directories corresponding to the sequence of --modality, or
                                a txt/csv file with Mod1_Img1,Mod2_Img1,...\nMod1_Img2,Mod2_Img2,...\n... ;
                                TBSS will be done for FA first, and then for other modalities.



# List creation

## 1. imagelist

You can easily generate list of your FA images as follows:

    cd projectDirectory
    ls `pwd`/000????/eddy/FA/*_FA.nii.gz > imagelist.txt

Here, we have a bunch of cases in the project directory whose IDs start with `000` and is followed by 
four alphanumeric characters. The directory structure to obtain FA images is `000????/eddy/FA/`. Inside the 
directory, we have an FA image ending with `_FA.nii.gz`.

**NOTE**: `pwd` is used to obtain absolute path


Similarly, you can generate a list of your dwis,masks as follows:
    
    cd projectDirectory
    touch dwi_mask_list.txt
    for i in GT_????
    do 
        echo `pwd`/$i/${i}_dwi_xc.nii.gz,`pwd`/$i/${i}_dwi_xc_mask.nii.gz >> dwi_mask_list.txt;
    done
    
In the above example, we have a bunch of cases with IDs GT_???? having separate folders.  
The dwis of the cases follow the pattern `ID_dwi_xc.nii.gz` and corresponding masks follow the pattern  
`ID_dwi_xc_mask.nii.gz`.

In the same way, you can define your file structure and file names to obtain an image/case list.


## 2. caselist

For just caselist, you can do:

    cd projectDirectory
    ls 000???? > caselist.txt 
    
Use of `????` is detailed above.
 
                 
# Tests

Test includes both pipeline test and unit tests. It is recommended to run tests before analyzing your data.  

## 1. pipeline

The repository comes with separate testing for three branches: `--enigma`, `--fmrib`, and `--studyTemplate`:

    ./install.sh test
    
Running the tests should take less than an hour.

## 2. unittest

You may run smaller and faster unit tests as follows.
    
    python -m unittest discover -v lib/tests/
    
**NOTE** In the current release, unit tests are dependant upon the outputs of whole pipeline test. 
This is likely to change in future. 
    

# ROI analysis

`--enigma` and `--fmrib` branch of the pipeline performs ROI based analysis as default. The way it works is, each of the 
projected skeleton in subject space is superimposed upon a binary label map.
     

# Multi threading

Processing can be multi-threaded over the cases. Besides, `antsMultivariateTemplateConstruction2.sh` utilizes 
multiple threads to speed-up template construction. 

    --nproc 8 # default is 4, use -1 for all available
   
However, multi-threading comes with a price of slowing down other processes that may be running in your system. So, it 
is advisable to leave out at least two cores for other processes to run smoothly.



# NRRD support

The pipeline is written for NIFTI image format. However, NRRD support is incorporated through [NIFTI --> NRRD](https://github.com/pnlbwh/dMRIharmonization/blob/parallel/lib/preprocess.py#L78) 
conversion on the fly.

See Billah, Tashrif; Bouix, Sylvain, Rathi, Yogesh; Various MRI Conversion Tools, 
https://github.com/pnlbwh/conversion, 2019, DOI: 10.5281/zenodo.2584003 for more details on the conversion method.

    
    
# Misc.



# Reference


S.M. Smith, M. Jenkinson, H. Johansen-Berg, D. Rueckert, T.E. Nichols, C.E. Mackay, K.E. Watkins, 
O. Ciccarelli, M.Z. Cader, P.M. Matthews, and T.E.J. Behrens. 
Tract-based spatial statistics: Voxelwise analysis of multi-subject diffusion data. NeuroImage, 31:1487-1505 


E. Garyfallidis, M. Brett, B. Amirbekian, A. Rokem, S. Van Der Walt, M. Descoteaux, 
I. Nimmo-Smith and DIPY contributors, "DIPY, a library for the analysis of diffusion MRI data", 
Frontiers in Neuroinformatics, vol. 8, p. 8, Frontiers, 2014.


Billah, Tashrif; Bouix, Sylvain, Rathi, Yogesh; Various MRI Conversion Tools, 
https://github.com/pnlbwh/conversion, 2019, DOI: 10.5281/zenodo.2584003.