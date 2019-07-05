#!/bin/bash

arra=("x=a y=3"
     "x=c y=4")

for i in "${arra[@]}"
do
    eval $i
    echo $y
done 
