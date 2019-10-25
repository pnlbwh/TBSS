![](doc/pnl-bwh-hms.png)

[![DOI](https://zenodo.org/badge/doi/10.5281/zenodo.2662497.svg)](https://doi.org/10.5281/zenodo.2662497) [![Python](https://img.shields.io/badge/Python-3.6-green.svg)]() [![Platform](https://img.shields.io/badge/Platform-linux--64%20%7C%20osx--64-orange.svg)]()

*TBSS* repository is developed by Tashrif Billah, Sylvain Bouix, and Ofer Pasternak, Brigham and Women's Hospital (Harvard Medical School).

If this repository is useful in your research, please cite as below: 

Billah, Tashrif; Bouix, Sylvain; Pasternak, Ofer; Generalized Tract Based Spatial Statistics (TBSS) pipeline,
https://github.com/pnlbwh/tbss, 2019, DOI: https://doi.org/10.5281/zenodo.2662497

See [documentation](./TUTORIAL.md) for details.

Table of Contents
=================

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
   * [Tests](#tests)
      * [1. pipeline](#1-pipeline)
      * [2. unittest](#2-unittest)
    
Table of Contents created by [gh-md-toc](https://github.com/ekalinin/github-markdown-toc)


# Dependencies

* ANTs = 2.2.0
* FSL = 5.0.11
* numpy = 1.16.2
* pandas = 1.2.1
* dipy = 0.16.0
* nibabel = 2.3.0
* nilearn = 0.5.2
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

(*Preferred*) You should install pre-complied ANTs from [PNL-BWH](https://anaconda.org/pnlbwh/ants):
    
    conda install -c pnlbwh ants
    
Installation with conda is more manageable. It will put the ANTs commands/scripts in your path when you do:
    
    source ~/miniconda3/bin/activate    

Alternatively, you can build ANTs from [source](https://github.com/ANTsX/ANTs). 

    
## 2. Install pipeline

Now that you have installed the prerequisite software, you are ready to install the pipeline:

    git clone https://github.com/pnlbwh/tbss && cd tbss
    ./install setup test
    
If you would not like to run tests, just omit the `test` argument. But it is recommended to run tests before you use 
this pipeline to analyze your data.


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
    
ANTs commands should be in `~/miniconda3/pkgs/ants-2.3.0-py3/bin` and/or `~/miniconda3/bin` directories. 
If they are not in your path already, use export `PATH=$PATH:~/miniconda3/pkgs/ants-2.3.0-py3/bin` 
to put all the commands in your path. Additionally, you should define define [ANTSPATH](https://github.com/ANTsX/ANTs/wiki/Compiling-ANTs-on-Linux-and-Mac-OS#set-path-and-antspath):

    export ANTSPATH=~/miniconda3/bin


# Running

Upon successful installation, you should be able to see the help message

`$ lib/tbss-pnl --help`
    
See [Useful commands](#-useful-commands) for quick tips about running the pipeline.


                 
# Tests

Test includes both pipeline test and unit tests. It is recommended to run tests before analyzing your data.  

## 1. pipeline

The repository comes with separate testing for three branches: `--enigma`, `--fmrib`, and `--studyTemplate`:

    ./install.sh test
    
Running the tests should take less than an hour.

## 2. unittest

You may run smaller and faster unit tests as follows.
    
    pytest -v lib/tests/test_*.py
    
**NOTE** In the current release, unit tests are dependant upon the outputs of whole pipeline test. 
This is likely to change in future. 

