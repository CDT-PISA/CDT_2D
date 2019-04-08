#!/bin/bash

# a function to compare version numbers
# https://stackoverflow.com/questions/4023830/how-to-compare-two-strings-in-dot-separated-version-format-in-bash

vercomp () {
    if [[ $1 == $2 ]]
    then
        return 0
    fi
    local IFS=.
    local i ver1=($1) ver2=($2)
    # fill empty fields in ver1 with zeros
    for ((i=${#ver1[@]}; i<${#ver2[@]}; i++))
    do
        ver1[i]=0
    done
    for ((i=0; i<${#ver1[@]}; i++))
    do
        if [[ -z ${ver2[i]} ]]
        then
            # fill empty fields in ver2 with zeros
            ver2[i]=0
        fi
        if ((10#${ver1[i]} > 10#${ver2[i]}))
        then
            return 1
        fi
        if ((10#${ver1[i]} < 10#${ver2[i]}))
        then
            return 2
        fi
    done
    return 0
}

# ---------- SETUP ----------

# SOME CHECKS TO START

# check if it is possible that is already setup

if [ -d "build" ] || [ -d "output" ]; then
	echo "'build' or 'output' directory already exist."
	echo "Are you sure to setup again? (y or n)"
	echo "ATTENTION: It will remove the whole content of 'bin', 'build' and 'output'."
	echo -n ""; read ANS
	if [ -z $ANS ] || [ $ANS != 'y' ]; then
		exit
	fi
	echo " "
fi

# check if there is a recent enough version of cmake

REGEX_VNUM='\d+[.]\d+[.]\d+'
VNUM=$(cmake --version | grep -o -m 1 -P $REGEX_VNUM)

if [ -z $VNUM ]; then
	echo "No available version of cmake found."
	exit
fi

vercomp $VNUM 3
case $? in
	0) op='=';;
	1) op='>';;
	2) op='<';;
esac

if [ $op = '<' ]; then
	echo "cmake version $VNUM is too old"
	echo "minimum requested: 3"
	exit
fi

# check if the PWD is the project folder

if [ $(basename $(pwd)) != "CDT_2D" ]; then
	echo "Please, run 'setup.sh' from 'CDT_2D' project folder."
	exit
fi

# BEGIN SETUP

echo -e "setup... \n"

# remove old folders

if [ -d "build" ]; then
	rm -rf build
fi

if [ -d "bin" ]; then
	rm -rf bin
fi

if [ -d "output" ]; then
	rm -rf output
fi

# create new folders

mkdir build output output/test output/data

# cmake the project

cd build
cmake ..

# set configs
cd ..
if [ -e "config.json" ]; then
	rm config.json
fi

echo "{" >> config.json
echo "Enter a valid email adress to receive notifications of run endings:"
echo " ⎛if left empty no email will be sent,"
echo " ⎝is adjustable after"
echo -n "--> "
read receiver_email
if [ -z "$receiver_email" ]; then
	receiver_email="null"
fi
echo "    \"receiver_email\": \"$receiver_email\"," >> config.json
echo

echo "Enter a valid remote for rclone:"
echo " ⎛if left empty no upload/download will be possible,"
echo " ⎝is adjustable after"
echo -n "--> "
read rclone_remote
if [ -z "$rclone_remote" ]; then
	rclone_remote="null"
fi
echo "    \"rclone_remote\": \"$rclone_remote\"" >> config.json
echo "}" >> config.json

