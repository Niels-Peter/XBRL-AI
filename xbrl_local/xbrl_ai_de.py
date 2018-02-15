#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 14 21:40:30 2018

@author: niels-peter
"""

from datetime import datetime, timedelta


def xbrl_54_to_xbrl_de_11(dict54, metadata = False):

    def get_xbrlkey(post, char):
        return post[post.index(char)+1:]

    # Find metadata!!!
    Metadata = {}
    units = {}
    languages = {}
    periods = {}
    ReportingPeriodStartDate = PrecedingReportingPeriodStartDate = PredingReportingPeriodEndDate = None
    for post in dict54:
        if post[0] == 'de-gcd-2013-04-30:genInfo.report.id.accordingTo.yearEnd':
            ReportingPeriodEndDate = (dict54[post])[0]
        if post[0] == '2010-01-31:genInfo.report.id.accordingTo.yearEnd':
            print((dict54[post])[0])
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
    try:        
        PrecedingReportingPeriodEndDate_temp\
            = str(datetime.strptime(ReportingPeriodStartDate, '%Y-%m-%d') - timedelta(days=1))[:10]
    except:
        pass
    periodmax = 0
    for post in periods:
        try:
            if type(post[0]).__name__ != 'NoneType' and post[1] == PrecedingReportingPeriodEndDate_temp and periods[post] > periodmax:
                Metadata['PrecedingReportingPeriodStartDate'] = PrecedingReportingPeriodStartDate = post[0]
                Metadata['PrecedingReportingPeriodEndDate'] = PrecedingReportingPeriodEndDate = post[0]
        except:
            pass
    if type('PrecedingReportingPeriodEndDate').__name__ != 'NoneType':
        PrecedingReportingPeriodEndDate_temp\
            = str(int(ReportingPeriodEndDate[0:4])-1) + ReportingPeriodEndDate[4:10]
        periodmax = 0
        for post in periods:
            try:
                if type(post[0]).__name__ == 'NoneType' and post[1] == PrecedingReportingPeriodEndDate_temp and periods[post] > periodmax:
                    Metadata['PrecedingReportingPeriodEndDate'] = PrecedingReportingPeriodEndDate = post[1]
            except:
                pass             
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
                    == PrecedingReportingPeriodEndDate and key[3] == None\
                    and (key[4] == Metadata['unit'] or key[4] == None or key[4] == Metadata['language']):
                dict11[key[0] + '_prev'] = dict54[key][0]
        except:
            pass
        try:
            if key[1] == None and key[2] == PrecedingReportingPeriodEndDate and key[3] == None\
                    and (key[4] == Metadata['unit'] or key[4] == None or key[4] == Metadata['language']):
                dict11[key[0] + '_prev'] = dict54[key][0]
        except:
            pass
        if key in ('{http://www.xbrl.org/2003/linkbase}schemaRef',
                   '@{http://www.w3.org/2001/XMLSchema-instance}schemaLocation'):
            Metadata[key] = dict54[key]
    compscore = 0
    if dict11.get('de-gaap-ci-2013-04-30:bs.ass', 'mis') != 'mis' or dict11.get('2010-01-31:bs.ass', 'mis') != 'mis':
        compscore = compscore + 1
    if dict11.get('de-gaap-ci-2013-04-30:bs.ass_prev', 'mis') != 'mis' or dict11.get('2010-01-31:bs.ass_prev', 'mis') != 'mis':
        compscore = compscore + 2
    if dict11.get('de-gaap-ci-2013-04-30:is.netIncome', 'mis') != 'mis' or dict11.get('2010-01-31:is.netIncome', 'mis') != 'mis':
        compscore = compscore + 4
    if dict11.get('de-gaap-ci-2013-04-30:is.netIncome_prev', 'mis') != 'mis'or dict11.get('2010-01-31:is.netIncome_prev', 'mis') != 'mis':
        compscore = compscore + 8 
    Metadata['compscore'] = compscore
    return dict11
