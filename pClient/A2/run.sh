#!/bin/bash

challenge="1"
host="localhost"
robname="97521_98123"
pos="0"
outfile="solution"

while getopts "c:h:r:p:f:" op
do
    case $op in
        "c")
            challenge=$OPTARG
            ;;
        "h")
            host=$OPTARG
            ;;
        "r")
            robname=$OPTARG
            ;;
        "p")
            pos=$OPTARG
            ;;
        "f")
            outfile=$OPTARG
            ;;
        default)
            echo "ERROR in parameters"
            ;;
    esac
done

shift $(($OPTIND-1))

case $challenge in
    4)
        rm -f *.path *.map  # do not remove this line
        # how to call agent for challenge 4
        python3 artemis.py -h "$host" -p "$pos" -r "$robname" -f "$outfile"
        mv your_mapfile $outfile.map
        mv your_pathfile $outfile.path
        ;;
esac

