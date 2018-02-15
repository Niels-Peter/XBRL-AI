#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 14 22:21:59 2018

@author: niels-peter
"""

datafil =[['filnavn', 'Indhold', 'regnskaber']]
import glob
import numpy as np
import pandas as pd
from xbrl_ai import xbrlinstance_to_dict, xbrldict_to_xbrl_54
from xbrl_local.xbrl_ai_de import xbrl_54_to_xbrl_de_11

format15 = format5 = format3 = format1 = 0


filer = glob.glob("/home/niels-peter/Dokumenter/Tyskland/*.xbrl")
for filenavn in filer:
    Indholdsscore = 0
    print(filenavn)
    file = open(filenavn,'r')     
    file_indhold = file.read()
    xbrl = xbrlinstance_to_dict(file_indhold)
    xbrl54 = xbrldict_to_xbrl_54(xbrl)
    xbrl11 = xbrl_54_to_xbrl_de_11(xbrl54, True)
    if xbrl11.get('de-gaap-ci-2013-04-30:bs.ass', 'mangler') != 'mangler':
        Indholdsscore = Indholdsscore + 1
    if xbrl11.get('2010-01-31:bs.ass', 'mangler') != 'mangler':
        Indholdsscore = Indholdsscore + 1
    if xbrl11.get('de-gaap-ci-2013-04-30:bs.ass_prev', 'mangler') != 'mangler':
        Indholdsscore = Indholdsscore + 2
    if xbrl11.get('2010-01-31:bs.ass_prev', 'mangler') != 'mangler':
        Indholdsscore = Indholdsscore + 2
    if xbrl11.get('de-gaap-ci-2013-04-30:is.netIncome', 'mangler') != 'mangler':
        Indholdsscore = Indholdsscore + 4
    if xbrl11.get('2010-01-31:is.netIncome', 'mangler') != 'mangler':
        Indholdsscore = Indholdsscore + 4
    if xbrl11.get('de-gaap-ci-2013-04-30:is.netIncome_prev', 'mangler') != 'mangler':
        Indholdsscore = Indholdsscore + 8
    if xbrl11.get('2010-01-31:is.netIncome_prev', 'mangler') != 'mangler':
        Indholdsscore = Indholdsscore + 8 
    if Indholdsscore == 15:
        format15 = format15 + 1
    if Indholdsscore == 5:
        format5 = format5 + 1
    if Indholdsscore == 3:
        format3 = format3 + 1
    if Indholdsscore == 1:
        format1 = format1 + 1

    datafil = np.append(datafil, [[filenavn, Indholdsscore, xbrl11]], axis=0)

datafil_frame = pd.DataFrame(np.delete(datafil,(0), axis=1)[1:], index=datafil[:, 0][1:], columns=datafil[0][1:])


file = open('/home/niels-peter/Dokumenter/Tyskland/140314011228.xbrl','r')     
file_indhold = file.read()
xbrl = xbrlinstance_to_dict(file_indhold)
xbrl54 = xbrldict_to_xbrl_54(xbrl)
xbrl11 = xbrl_54_to_xbrl_de_11(xbrl54, True)

print(format1, format3, format5, format15)