#!/bin/bash

if [ "$1" = "-c" ]  || [ "$1" = "-C" ]; then
    if [ "$2" = "1" ]; then
        python3 myRobC1.py --robname C1_97521_98123 
    elif [ "$2" = "2" ]; then
        python3 myRobC2.py --robname C2_97521_98123 
        echo "Mapping file name is 'myrob.map'"
    elif [ "$2" = "3" ]; then
        python3 myRobC3.py --robname C3_97521_98123 
        echo "Path file name is 'myrob.path'"
    fi
else
    echo "Usage: ./run.sh -c <challenge number>"
    echo "Example: ./run.sh -c 1"
fi