#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 12 17:38:00 2018

@author: niels-peter
"""

__title__ = 'test_xbrl_ai_de'
__version__ = '0.0.1'
__author__ = 'Niels-Peter Rønmos'

import requests
from xbrl_ai import xbrlinstance_to_dict, xbrldict_to_xbrl_54
from xbrl_local.xbrl_ai_de import xbrl_54_to_xbrl_de_11

file = open('151214030838.xbrl','r')
file_indhold = file.read()

xbrl = xbrlinstance_to_dict(file_indhold)
xbrl54 = xbrldict_to_xbrl_54(xbrl)

xbrl11 = xbrl_54_to_xbrl_de_11(xbrl54, True)