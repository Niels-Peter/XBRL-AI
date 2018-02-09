#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 31 11:16:07 2018

@author: niels-peter
"""

import requests
from xbrl_ai import xbrlinstance_to_dict
from xbrl_local.xbrl_ai_dk import fetchlist_dk, xbrldict_to_xbrl_dk_64, xbrl_dk_64_to_xbrl_dk_11


__title__ = 'test_xbrl_ai_dk'
__version__ = '0.0.1'
__author__ = 'Niels-Peter Rønmos'


"""
This testsample fetch metadata om newest apal report from
company with Business Register Number 30004000 on date 015-10-31
and load it into xbrldoc_as_dict
"""

# Step 1:
metadata = fetchlist_dk('30004000', '2015-10-31')
#metadata = fetchlist_dk('61056416', '2015-10-31')
#metadata = fetchlist_dk('36714565', date='2016-12-31', reports='ALL', style='dict')
#metadata = fetchlist_dk('11964346', '2016-08-31')


targeturl = metadata['dokumentUrl']

# Step 2:
xbrldoc_as_dict = xbrlinstance_to_dict(requests.get(targeturl).content)

# Step 3:
xbrl_as_dk_64 = xbrldict_to_xbrl_dk_64(xbrldoc_as_dict)

# Step 4:
xbrl_as_dk_11 = xbrl_dk_64_to_xbrl_dk_11(xbrl_as_dk_64)


