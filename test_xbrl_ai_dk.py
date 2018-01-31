#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 31 11:16:07 2018

@author: niels-peter
"""

import requests
from xbrl_ai import xbrlinstance_to_dict
from xbrl_ai_dk import fetchlist_dk


__title__ = 'test_xbrl_ai_dk'
__version__ = '0.0.1'
__author__ = 'Niels-Peter Rønmos'


"""
This testsample fetch metadata om newest annual report from
company with Business Register Number 30004000 on date 015-10-31
and load it into xbrldoc_as_dict
"""

metadata = fetchlist_dk('30004000', '2015-10-31')

targeturl = metadata['dokumentUrl']
xbrldoc_as_dict = xbrlinstance_to_dict(requests.get(targeturl).content)


