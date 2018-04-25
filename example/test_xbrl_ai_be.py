#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 25 21:42:35 2018

@author: niels-peter
"""

__title__ = 'test_xbrl_ai_be'
__version__ = '0.0.1'
__author__ = 'Niels-Peter Rønmos'

import requests
from xbrl_ai import xbrlinstance_to_dict, xbrldict_to_xbrl_54

file = open('201702100243.xbrl','r')


file_indhold = file.read()

xbrl = xbrlinstance_to_dict(file_indhold)
xbrl_as_54 = xbrldict_to_xbrl_54(xbrl)