#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 14 21:40:30 2018

@author: niels-peter
"""

from datetime import datetime, timedelta


def xbrl_54_to_xbrl_de_11(dict54, metadata = False):
    # Find metadata!!!
    Metadata = {}
    units = {}
    languages = {}
    periods = {}
    PrecedingReportingPeriodStartDate = PredingReportingPeriodEndDate = None
    for post in dict54:
        if post[0] == 'de-gcd-2013-04-30:genInfo.report.id.accordingTo.yearEnd':
            ReportingPeriodEndDate = (dict54[post])[0]
        if type(post[4]).__name__ != 'NoneType':
            if (post[1], post[2]) not in periods:
                periods[post[1], post[2]] = 1
            else:
                periods[post[1], post[2]] = periods[post[1], post[2]] + 1
            if post[4] not in units:
                if post[4][0:3] == 'iso':
                    units[post[4]] = 1
            else:
                units[post[4]] = units[post[4]] + 1
            if post[4] not in languages:
                if post[4][0:5] == 'lang:':
                    languages[post[4]] = 1
            else:
                languages[post[4]] = languages[post[4]] + 1
    unitmax = 0
    language = None
    for post in units:
        if units[post] > unitmax:
            unitmax = units[post]
            unit = post
    Metadata['unit'] = unit    
    languagemax = 0
    for post in languages:
        if languages[post] > languagemax:
            languagemax = languages[post]
            language = post
    Metadata['language'] = language
    Metadata['ReportingPeriodEndDate'] = ReportingPeriodEndDate
    periodmax = 0
    for post in periods:
        if type(post[0]).__name__ != 'NoneType' and post[1] == ReportingPeriodEndDate and periods[post] > periodmax:
            Metadata['ReportingPeriodStartDate'] = ReportingPeriodStartDate = post[0]
            
    PredingReportingPeriodEndDate_temp\
        = str(datetime.strptime(ReportingPeriodStartDate, '%Y-%m-%d') - timedelta(days=1))[:10]    
    periodmax = 0
    for post in periods:
        if type(post[0]).__name__ != 'NoneType' and post[1] == PredingReportingPeriodEndDate_temp and periods[post] > periodmax:
            Metadata['PredingReportingPeriodStartDate'] = PredingReportingPeriodStartDate = post[0]
            Metadata['PredingReportingPeriodEndDate'] = PredingReportingPeriodEndDate = post[0]    
    dict11 = {}
    if metadata == True:
        dict11['metadata'] = Metadata
    for key in dict54:
        if key[1] == ReportingPeriodStartDate\
                and key[2] == ReportingPeriodEndDate and key[3] == None\
                and (key[4] == Metadata['unit'] or key[4] == None or key[4] == Metadata['language']):
            dict11[key[0]] = dict54[key][0]
        if key[1] == None and key[2] == ReportingPeriodEndDate and key[3] == None\
                and (key[4] == Metadata['unit'] or key[4] == None or key[4] == Metadata['language']):
            dict11[key[0]] = dict54[key][0]
        try:
            if key[1] == PrecedingReportingPeriodStartDate and key[2]\
                    == PredingReportingPeriodEndDate and key[3] == None\
                    and (key[4] == Metadata['unit'] or key[4] == None or key[4] == Metadata['language']):
                dict11[key[0] + '_prev'] = dict54[key][0]
        except:
            pass
        try:
            if key[1] == None and key[2] == PredingReportingPeriodEndDate and key[3] == None\
                    and (key[4] == Metadata['unit'] or key[4] == None or key[4] == Metadata['language']):
                dict11[key[0] + '_prev'] = dict54[key][0]
        except:
            pass
        if key in ('{http://www.xbrl.org/2003/linkbase}schemaRef',
                   '@{http://www.w3.org/2001/XMLSchema-instance}schemaLocation'):
            Metadata[key] = dict54[key]
    return dict11
