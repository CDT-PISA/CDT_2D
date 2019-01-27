#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 27 12:25:38 2019

@author: alessandro
"""
from os import mkdir
from shutil import rmtree

def clear_output():
    rmtree("output")
    mkdir("output")
    