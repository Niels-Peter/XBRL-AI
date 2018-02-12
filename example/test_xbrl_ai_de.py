#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 12 17:38:00 2018

@author: niels-peter
"""



import requests
from xbrl_ai import xbrlinstance_to_dict, xbrldict_to_xbrl_54

__title__ = 'test_xbrl_ai_us'
__version__ = '0.0.1'
__author__ = 'Niels-Peter Rønmos'

file = open('151214030838.xbrl','r')
file_indhold = file.read()

xbrl = xbrlinstance_to_dict(file_indhold)
xbrl54 = xbrldict_to_xbrl_54(xbrl)

