#!/bin/bash
#
export srcDir=/home/paugam/Src/GetArome
export dataDir=/mnt/data3/SILEX/AROME/
export logDir=/mnt/data3/SILEX/AROME/FORECAST/log
mkdir -p $logDir

source ~/.myKey.sh
source ~/Venv/arome/bin/activate
python $srcDir/download_arome.py $dataDir >& $logDir/aromeDownload.log
exit_code=$?
echo out download_arome.py: $exit_code
if [ $exit_code -eq 0 ]; then
    echo "start fwi calculation"
    $srcDir/../hFWI/src/run-fwi.sh $dataDir
fi
if [ $exit_code -eq 3 ]; then
    if [ -f "$dataDir/FORECAST/lock.txt" ]; then
        echo "rm $dataDir/FORECAST/lock.txt"
        rm "$dataDir/FORECAST/lock.txt"
        cp $dataDir/FWI/log/fwi.log /home/paugam/WebSite/certec/data/FWI/
    fi
fi
