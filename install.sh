#!/usr/bin/env bash


SCRIPT=$(readlink -m $(type -p $0))
SCRIPTDIR=$(dirname $SCRIPT)

dataDir=$SCRIPTDIR/data
enigmaDir=$SCRIPTDIR/data/enigmaDTI


echo Getting enigma data
if [ ! -f $dataDir/enigmaDTI.zip ]
then
    wget http://enigma.ini.usc.edu/wp-content/uploads/2013/02/enigmaDTI.zip -P $dataDir
else
    echo $dataDir/enigmaDTI.zip exists, unzipping enigmaDTI.zip
fi

unzip -o -d $enigmaDir $dataDir/enigmaDTI.zip
mv $dataDir/ENIGMA_look_up_table.txt $enigmaDir


echo Checking python version
read -r _ v <<< `python --version`
if [ ${v//.} -gt 300 ]
then
    echo "python>=3 found"
else
    echo "Installation requires python>=3"
    exit 1
fi


echo Installing python libraries
pip install -r $SCRIPTDIR/requirements.txt


# Run pipeline test
#echo Fetching test data
#FA,MD,AD modality TBSS are run on three test dwi/mask pairs
#Multi modality TBSS pipeline test should take less than 10 minutes
