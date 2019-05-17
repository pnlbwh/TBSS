#!/usr/bin/env bash


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
    echo "export FSLDIR=~/fsl && source ~/fsl/etc/fslconf/fsl.sh && export PATH=$PATH:~/fsl/bin"
    exit 1
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
pip install -r $SCRIPTDIR/requirements.txt --upgrade
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

echo Generating bet mask for test data ...
for i in `ls *.nii`
do
    IFS=., read -r prefix _ _ <<< $i
    if [ -f $prefix.bval ] && [ -f $prefix.bvec ]
    then
        bet $i $prefix -m -n
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
--ncpu -1 && echo --enigma branch execution successful \
|| echo --enigma branch execution FAILED

# pushd .
# cd $SCRIPTDIR
# python -m unittest -v $testDir/"test_enigma.py"
# popd


# --fmrib branch ===========================================
echo Testing --fmrib branch ...
pushd .
cd $testDir/enigmaTemplateOutput/
$libDir/tbss_all -i FA/origdata,MD/origdata,AD/origdata,RD/origdata \
--modality FA,MD,AD,RD --fmrib \
-l $FSLDIR/data/atlases/JHU/JHU-ICBM-labels-1mm.nii.gz \
--avg -o $testDir/fmribTemplateOutput/ \
--ncpu -1 && echo --fmrib branch execution successful \
|| echo --fmrib branch execution FAILED
popd

# pushd .
# cd $SCRIPTDIR
# python -m unittest -v $testDir/"test_fmrib.py"
# popd


# --studyTemplate branch ==================================
echo Testing --studyTemplate branch ...

pushd .
cd $testDir/enigmaTemplateOutput/
$libDir/tbss_all -i FA/origdata,MD/origdata,AD/origdata,RD/origdata \
-c $CASELIST \
--modality FA,MD,AD,RD --studyTemplate \
-s $FSLDIR/data/standard/FMRIB58_FA_1mm.nii.gz \
-l $FSLDIR/data/atlases/JHU/JHU-ICBM-labels-1mm.nii.gz \
--avg -o $testDir/studyTemplateOutput/ \
--ncpu -1 && echo --studyTemplate branch execution successful \
|| echo --studyTemplate branch execution FAILED
popd

# pushd .
# cd $SCRIPTDIR
# python -m unittest -v $testDir/"test_study.py"
# popd

# run all tests together
pushd .
cd $SCRIPTDIR
python -m unittest -v $testDir/test_*
popd

echo Testing complete.

}


# main function ==================
if [ -z $@ ]
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

