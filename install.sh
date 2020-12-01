#!/usr/bin/env bash

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


# ================================

SCRIPT=$(readlink -m $(type -p $0))
SCRIPTDIR=$(dirname $SCRIPT)
dataDir=$SCRIPTDIR/data
enigmaDir=$SCRIPTDIR/data/enigmaDTI
testDir=$SCRIPTDIR/lib/tests/
testDataDir=$SCRIPTDIR/lib/tests/data
libDir=$SCRIPTDIR/lib



install()
{
# ================================
echo Checking python version
read -r _ v <<< $(python --version 2>&1)
if [ ${v//.} -gt "300" ]
then
    echo "python>=3 found"
else
    echo "Installation requires python>=3"
    exit 1
fi

# ================================
echo Checking FSL environment
if [ ! -z $FSLDIR ]
then
    echo "FSLDIR is set"
else
    echo "FSL environment is not set, may be you want to do the following: "
    echo "export FSLDIR=~/fsl && source ~/fsl/etc/fslconf/fsl.sh && export PATH=\$PATH:~/fsl/bin"
    exit 1
fi


# ================================
echo Checking ANTSPATH
if [ -z $ANTSPATH ]
then
    echo "ANTSPATH is not set and/or ANTs commands are not available in PATH"
    echo "May be you forgot to do: "
    echo "export ANTSPATH=/path/to/ANTs/scripts && export PATH=\$PATH:/path/to/ANTs/executables"
    exit 1
else
    echo "ANTSPATH is set"
fi


# ================================
echo Downloading enigma data
if [ ! -f $dataDir/enigmaDTI.zip ]
then
    wget http://enigma.ini.usc.edu/wp-content/uploads/2013/02/enigmaDTI.zip -P $dataDir
else
    echo $dataDir/enigmaDTI.zip exists, unzipping enigmaDTI.zip
fi

unzip -o -d $enigmaDir $dataDir/enigmaDTI.zip
cp $dataDir/ENIGMA_look_up_table.txt.bak $enigmaDir/ENIGMA_look_up_table.txt


# ================================
echo Installing python libraries
pip install -r $SCRIPTDIR/requirements.txt --upgrade --no-cache-dir
}



test_pipeline()
{
# ================================
# pipeline tests

echo "Preparing to run TBSS pipeline tests ...
FA,MD,AD,RD modality TBSS are run on four dwi/mask pairs
Running multi-modality TBSS pipeline tests should take less than an hour"


if [ ! -d $testDataDir ]
then
    mkdir $testDataDir
fi

pushd .

echo Fetching test data ...
cd $testDataDir

if [ ! -d dcm_qa_uih ]
then
    git clone https://github.com/neurolabusc/dcm_qa_uih.git
fi

pushd .
cd dcm_qa_uih/Ref

IMAGELIST=$testDataDir/imagelist.txt
CASELIST=$testDataDir/caselist.txt
if [ -f $IMAGELIST ]
then
    rm $IMAGELIST
fi
touch $IMAGELIST

if [ -f $CASELIST ]
then
    rm $CASELIST
fi
touch $CASELIST

echo Generating brain mask for test data ...
for i in `ls *.nii`
do
    IFS=., read -r prefix _ _ <<< $i
    if [ -f $prefix.bval ] && [ -f $prefix.bvec ]
    then
        $libDir/dwiMask.py -i $i -o $prefix
        echo `pwd`/$i,`pwd`/${prefix}_mask.nii.gz >> $IMAGELIST
        echo $prefix >> $CASELIST
    fi
done
popd



# --enigma branch ==========================================
echo Testing --enigma branch ...
$libDir/tbss_all -i $IMAGELIST --generate \
-c $CASELIST \
--modality FA,MD,AD,RD --enigma \
--avg -o $testDir/enigmaTemplateOutput/ \
--noFillHole \
--ncpu -1 --force && echo --enigma branch execution successful \
|| echo --enigma branch execution FAILED


# read
# pushd .
# cd $SCRIPTDIR
# pytest -v $testDir/"test_enigma.py"
# popd


# --fmrib branch ===========================================
echo Testing --fmrib branch ...
pushd .
cd $testDir/enigmaTemplateOutput/
$libDir/tbss_all -i FA/origdata,MD/origdata,AD/origdata,RD/origdata \
-c $CASELIST \
--modality FA,MD,AD,RD --fmrib \
-l $FSLDIR/data/atlases/JHU/JHU-ICBM-labels-1mm.nii.gz \
--lut $testDir/data/FreeSurferColorLUT.txt \
--avg -o $testDir/fmribTemplateOutput/ \
--noAllSkeleton --noHtml \
--ncpu -1 --force && echo --fmrib branch execution successful \
|| echo --fmrib branch execution FAILED
popd


# read
# pushd .
# cd $SCRIPTDIR
# pytest -v $testDir/"test_fmrib.py"
# popd


# env variable for reproducing template
export ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS=1


# --studyTemplate branch ==================================
echo Testing --studyTemplate branch ...

pushd .
cd $testDir/enigmaTemplateOutput/
$libDir/tbss_all -i FA/origdata,MD/origdata,AD/origdata,RD/origdata \
-c $CASELIST \
--modality FA,MD,AD,RD --studyTemplate \
-s $FSLDIR/data/standard/FMRIB58_FA_1mm.nii.gz \
-l $FSLDIR/data/atlases/JHU/JHU-ICBM-labels-1mm.nii.gz \
--lut $testDir/data/FreeSurferColorLUT.txt \
--avg -o $testDir/studyTemplateOutput/ \
--noFillHole \
--ncpu -1 --force && echo --studyTemplate branch execution successful \
|| echo --studyTemplate branch execution FAILED
popd

# read
# pushd .
# cd $SCRIPTDIR
# pytest -v $testDir/"test_study.py"
# popd



# partial testing =========================================
echo Testing partial --enigma branch ...

pushd .
cd $testDir/enigmaTemplateOutput
$libDir/tbss_all -i MD/origdata,RD/origdata \
-o $testDir/enigmaTemplateOutput/ \
--modality MD,RD --noFillHole \
--enigma && echo Partial --enigma branch execution successful \
|| echo Partial --enigma branch execution FAILED
popd



echo Testing partial --studyTemplate branch ...

pushd .
cd $testDir/enigmaTemplateOutput/
$libDir/tbss_all -i AD/origdata,RD/origdata \
-o $testDir/studyTemplateOutput/ \
--modality AD,RD --noFillHole \
--study && echo Partial --studyTemplate branch execution successful \
|| echo Partial --studyTemplate branch execution FAILED
popd


# run all unittests together ==============================
pushd .
cd $SCRIPTDIR
pytest -v $testDir/test_*
popd

echo Testing complete.

}


# main function ===========================================
if [ -z $1 ]
then
    echo """Example usage: 
./install.sh setup test
./install.sh setup
./install.sh test"""
    exit 1
fi

for subcmd in $@
do
    if [ $subcmd == "setup" ]
    then
        install
    elif [ $subcmd == "test" ]
    then
        test_pipeline
    else
        echo Undefined argument $subcmd
        exit 1
    fi
    
done


