#!/bin/bash

# get all dirs in current dir
function ergodic(){
  for file in `ls $1`
  do
    if [ -d $1"/"$file ]
    then
      ergodic $1"/"$file
    else
      local path=$1"/"$file
      if [[ ! $1 =~ $FILTER ]]
      then
        echo "mkdir -p ."${1/"`pwd`"/""} ";touch ./${1/"`pwd`"/""}/init.md"
      fi
    fi
  done
}

IFS=$'\n'
INIT_PATH="`pwd`";
FILTER="uff"
ergodic $INIT_PATH
