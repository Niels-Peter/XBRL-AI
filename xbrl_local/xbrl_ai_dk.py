#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 31 09:10:49 2018

@author: niels-peter
"""
import time
import collections
import requests
from datetime import datetime, timedelta
from sklearn.base import BaseEstimator, TransformerMixin
import numpy as np
from xbrl_ai import xbrlinstance_to_dict


__title__ = 'xbrl_ai_dk'
__version__ = '0.0.3'
__author__ = 'Niels-Peter Rønmos'


def fetchlist_dk(cvrnummer, date='dd', reports='AARSRAPPORT', style='dict'):
    """
    Opslag til ERST json indeks indeholdende regnskaber i XBRL eller uden XBRL:

    CVRnummer:
        8 cifret string bestående af tal.

    date:
        Tekststring med formattet: YYYY-MM-DD
        dd: Default. Dags dato (time)

        Anvendes kun hvis style == 'dict', dvs. hvis der ønsker kun 1 svar
        Retursvar indeholder seneste regnskab med en slutdato <= date

    reports:
        Tekststring jf. definitioner i json indekset
        'AARSRAPPORT': Default
        'ALL': medtager alt.
        ... øvrige: se indekset.

    style:
        dict: Returnere én forekomst: seneste, se date ovenfor.
        list: Returnere liste over all, se dog 'reports' ovenfor.
        json: Returnere retursvar fra json indeks i json-format
        request: Returnere det rå svar fra json indekset

    Retursvar:
        ... se dokumentation af json indeks. Variabelnavne genbrugt!!!!
    """

    def _post_to_dict(post):
        dict_post = {}
        dict_post['_id'] = post['_id']
        dict_post['cvrNummer'] = (post['_source'])['cvrNummer']
        dict_post['regNummer'] = (post['_source'])['regNummer']
        dict_post['offentliggoerelsesTidspunkt'] = (post['_source'])\
            ['offentliggoerelsesTidspunkt']
        dict_post['offentliggoerelsestype'] = (post['_source'])\
            ['offentliggoerelsestype']
        dict_post['omgoerelse'] = (post['_source'])['omgoerelse']
        dict_post['sagsNummer'] = (post['_source'])['sagsNummer']
        dict_post['startDato'] = (((post['_source'])['regnskab'])\
            ['regnskabsperiode'])['startDato']
        dict_post['slutDato'] = (((post['_source'])['regnskab'])\
            ['regnskabsperiode'])['slutDato']
        dict_post['dokumentUrl'] = None
        for dok in (post['_source'])['dokumenter']:
            if dok['dokumentMimeType'] == 'application/xml':
                dict_post['dokumentUrl'] = dok['dokumentUrl']
                dict_post['dokumentType'] = dok['dokumentType']
        return dict_post

    if date == 'dd':
        date = time.strftime("%Y-%m-%d")
    returnstatement = None
    url = 'http://distribution.virk.dk/offentliggoerelser/_search?q=cvrNummer:"' + cvrnummer + '"'
    reg = requests.get(url)
    json = reg.json()
    indhold = json['hits']['hits']
    if style == 'list':
        regnskabsliste = []
        for post in indhold:
            dict_regn = _post_to_dict(post)
            if reports == 'ALL':
                regnskabsliste.append(dict_regn)
            elif reports == dict.get('dokumentType', None):
                regnskabsliste.append(dict_regn)
            else:
                pass
        returnstatement = regnskabsliste
    elif style == 'dict':
        return_dict = None
        fundet_dato = ''
        returnstatement = None
        for post in indhold:
            dict_post = _post_to_dict(post)
            if dict_post['slutDato'] <= date \
            and (reports == dict_post.get('dokumentType', None) or reports == 'ALL'):
                if dict_post['slutDato'] > fundet_dato:
                    fundet_dato = dict_post['slutDato']
                    return_dict = dict_post
        returnstatement = return_dict
    elif style == 'json':
        returnstatement = json
    elif style == 'request':
        returnstatement = reg
    else:
        returnstatement = None
    return returnstatement


def xbrldict_to_xbrl_dk_64(xbrldict):
    """
    SKAL rettes til:
        - Strategi ved dobbeltfelter med afvigende value/decimal
    """

    def get_xbrlkey(post, char):
        return post[post.index(char)+1:]

    def explicit_list(explicit, ifrs):
        explicit_liste = {}
        dimension_list = []
        label_extend = ''
        koncern = False
        if not ifrs:
            koncern = False
            if type(explicit).__name__ == 'OrderedDict':
                if get_xbrlkey(explicit['@dimension'], ":")\
                        == 'ConsolidatedSoloDimension':
                    koncern = True
                else:
                    explicit_liste[get_xbrlkey(explicit['@dimension'], ":")]\
                        = get_xbrlkey(explicit['$'], ":")
            if type(explicit).__name__ == 'list':
                for element in explicit:
                    if get_xbrlkey(element['@dimension'], ":")\
                            == 'ConsolidatedSoloDimension':
                        koncern = True
                    else:
                        explicit_liste[get_xbrlkey(element['@dimension'], ":")]\
                            = get_xbrlkey(element['$'], ":")
        else:
            koncern = True
            if type(explicit).__name__ == 'OrderedDict':
                if get_xbrlkey(explicit['@dimension'], ":")\
                    == 'ConsolidatedAndSeparateFinancialStatementsAxis':
                        koncern = False
                else:
                    explicit_liste[get_xbrlkey(explicit['@dimension'], ":")]\
                        = get_xbrlkey(explicit['$'], ":")
            if type(explicit).__name__ == 'list':
                for element in explicit:
                    if get_xbrlkey(element['@dimension'], ":")\
                            == 'ConsolidatedAndSeparateFinancialStatementsAxis':
                        koncern = False
                    else:
                        explicit_liste[get_xbrlkey(element['@dimension'], ":")]\
                            = get_xbrlkey(element['$'], ":")
        explicit_liste_od = collections.OrderedDict(sorted(explicit_liste.items()))
        for keys in explicit_liste_od:
            label_extend = label_extend + '_' + explicit_liste_od[keys]
            dimension_list.append(keys)
        return koncern, label_extend, dimension_list

    def typed_list(typed):
        typed_liste = {}
        dimension_list = []
        label_typed = label_typed_id = ''
        if type(typed).__name__ == 'OrderedDict':
            for poster in typed:
                if poster == '@dimension':
                    dimension = get_xbrlkey(typed['@dimension'], ":")
                if poster != '@dimension':
                    vaerdi = (typed[poster]).get('$', None)
                    member = get_xbrlkey(poster, "}")
            typed_liste[dimension, vaerdi] = member
        if type(typed).__name__ == 'list':
            for element in typed:
                for poster in element:
                    if poster == '@dimension':
                        dimension = get_xbrlkey(element['@dimension'], ":")
                    if poster != '@dimension':
                        vaerdi = (element[poster]).get('$', None)
                        member = get_xbrlkey(poster, "}")
                typed_liste[dimension, vaerdi] = member
        typed_liste_od = collections.OrderedDict(sorted(typed_liste.items()))
        for keys in typed_liste_od:
            dimension_list.append(keys[0])
            label_typed = label_typed + '_' + typed_liste_od[keys]
            if label_typed_id == '':
                label_typed_id = str(keys[1])
            else:
                label_typed_id = label_typed_id + '|' + str(keys[1])
        return label_typed, label_typed_id, dimension_list

    def concept_data(inputdata, ifrs):
        value = inputdata.get('$', None)
        unit = inputdata.get('unit', None)
        decimals = inputdata.get('@decimals', None)
        context = inputdata['context']
        lang = inputdata.get('@{http://www.w3.org/XML/1998/namespace}lang', None)
        if type(lang).__name__ != 'NoneType':
            lang = 'lang:' + lang
        # identificer = context[0]
        startdate = context[2]
        enddate = context[3]
        instant = context[4]
        if type(enddate).__name__ != 'str':
            enddate = instant
        explicit = context[5]
        typed = context[6]
        koncern, label_extend, dimension_list_extend = explicit_list(explicit, ifrs)
        label_typed, label_typed_id, dimension_list_typed = typed_list(typed)
        dimension_list = dimension_list_extend.append(dimension_list_typed)
        if label_typed_id == '':
            label_typed_id = None
        return value, unit, decimals, startdate, enddate, koncern, lang,\
            label_extend, label_typed, label_typed_id, dimension_list_extend

    #schemaRef = (XBRL['{http://www.xbrl.org/2003/linkbase}schemaRef'])\
    #['@{http://www.w3.org/1999/xlink}href']
    dict64 = {}
    if len([v for k, v in xbrldict.items() if k.startswith('{http://xbrl.ifrs.org/')]) > 0:
        ifrs = True
    else:
        ifrs = False
    for post in xbrldict:
        if post not in ('{http://www.xbrl.org/2003/linkbase}schemaRef',
                        '@{http://www.w3.org/2001/XMLSchema-instance}schemaLocation'):
            ref = post[:post.index('}')]
            xbrlref = ref[(ref.rfind('/') - len(ref) + 1):]
            if type(xbrldict[post]).__name__ == 'list':
                for element in xbrldict[post]:
                    value, unit, decimals, startdate, enddate, koncern, lang, label_extend,\
                        label_typed, label_typed_id, dimension_list = concept_data(element, ifrs)
                    concept = xbrlref + ':' + get_xbrlkey(post, '}') + label_extend + label_typed
                    if type(unit).__name__ == 'NoneType':
                        unit = lang
                    nogle = (concept, startdate, enddate, label_typed_id, koncern, unit)
                    if nogle in dict64 and dict64[nogle][0] != value:
                        print('!!!!!!!!!', nogle, value, unit, decimals, dict64[nogle])
                    if len(str(dimension_list)) < 5:
                        dimension_list = None
                    dict64[nogle] = [value, unit, decimals, dimension_list]
            if type(xbrldict[post]).__name__ == 'OrderedDict':
                value, unit, decimals, startdate, enddate, koncern, lang, label_extend, label_typed,\
                    label_typed_id, dimension_list = concept_data(xbrldict[post], ifrs)
                concept = xbrlref + ':' + get_xbrlkey(post, '}') + label_extend + label_typed
                if type(unit).__name__ == 'NoneType':
                    unit = lang
                nogle = (concept, startdate, enddate, label_typed_id, koncern, unit)
                if nogle in dict64 and dict64[nogle][0] != value:
                    print('!!!!!!!!!', nogle, value, unit, decimals, dict64[nogle])
                if len(str(dimension_list)) < 5:
                    dimension_list = None
                dict64[nogle] = [value, unit, decimals, dimension_list]
        if post in ('{http://www.xbrl.org/2003/linkbase}schemaRef',
                    '@{http://www.w3.org/2001/XMLSchema-instance}schemaLocation'):
            dict64[post] = xbrldict[post]
    return dict64

def xbrl_dk_64_to_xbrl_dk_11(dict64, metadata = False):
    # Find metadata!!!
    koncern = False
    units = {}
    languages = {}
    periods = {}
    PrecedingReportingPeriodStartDate = PredingReportingPeriodEndDate\
        = PredingReportingPeriodEndDate_temp = None
    for post in dict64:
        if post[0] == 'gsd:ReportingPeriodStartDate':
            ReportingPeriodStartDate = (dict64[post])[0]
        if post[0] == 'gsd:ReportingPeriodEndDate':
            ReportingPeriodEndDate = (dict64[post])[0]
        if post[0] == 'gsd:PrecedingReportingPeriodStartDate':
            PrecedingReportingPeriodStartDate = (dict64[post])[0]
        if post[0] == 'gsd:PredingReportingPeriodEndDate':
            PredingReportingPeriodEndDate = (dict64[post])[0]
        if post[4] is True:
            koncern = True
        if type(post[5]).__name__ != 'NoneType':
            if (post[1], post[2]) not in periods:
                periods[post[1], post[2]] = 1
            else:
                periods[post[1], post[2]] = periods[post[1], post[2]] + 1
            if post[5] not in units:
                if post[5][0:3] == 'iso':
                    units[post[5]] = 1
            else:
                units[post[5]] = units[post[5]] + 1
            if post[5] not in languages:
                if post[5][0:5] == 'lang:':
                    languages[post[5]] = 1
            else:
                languages[post[5]] = languages[post[5]] + 1
    unitmax = 0
    language = None
    for post in units:
        if units[post] > unitmax:
            unitmax = units[post]
            unit = post
    languagemax = 0
    for post in languages:
        if languages[post] > languagemax:
            languagemax = languages[post]
            language = post
    Metadata = {}
    Metadata['unit'] = unit
    Metadata['language'] = language
    Metadata['koncern'] = koncern
    Metadata['ReportingPeriodEndDate'] = ReportingPeriodEndDate
    Metadata['ReportingPeriodStartDate'] = ReportingPeriodStartDate
    if PrecedingReportingPeriodStartDate is None or\
            PredingReportingPeriodEndDate is None:
        PredingReportingPeriodEndDate_temp\
            = str(datetime.strptime(ReportingPeriodStartDate, '%Y-%m-%d') - timedelta(days=1))[:10]
    periodmax = 0
    for post in periods:
        if post[1] == PredingReportingPeriodEndDate_temp\
                and type(post[0]).__name__ != 'NoneType'\
                and periods[post] > periodmax:
            PredingReportingPeriodEndDate = PredingReportingPeriodEndDate_temp
            periodmax = periods[post]
            PrecedingReportingPeriodStartDate = post[0]
            
    Metadata['PrecedingReportingPeriodStartDate'] = PrecedingReportingPeriodStartDate
    Metadata['PredingReportingPeriodEndDate'] = PredingReportingPeriodEndDate
    
    dict11 = {}
    if metadata == True:
        dict11['metadata'] = Metadata
    for key in dict64:
        if key[1] == ReportingPeriodStartDate and key[2]\
            == ReportingPeriodEndDate and key[3] == None and key[4]\
            == Metadata['koncern']\
            and (key[5] == Metadata['unit'] or key[5] == None or key[5] == Metadata['language']):
            dict11[key[0]] = dict64[key][0]
        if key[1] == None and key[2] == ReportingPeriodEndDate and key[3]\
                == None and key[4] == Metadata['koncern']\
                and (key[5] == Metadata['unit'] or key[5] == None or key[5] == Metadata['language']):
            dict11[key[0]] = dict64[key][0]
        if key[1] == PrecedingReportingPeriodStartDate and key[2]\
                == PredingReportingPeriodEndDate and key[3] == None\
                and key[4] == Metadata['koncern']\
                and (key[5] == Metadata['unit'] or key[5] == None or key[5] == Metadata['language']):
            dict11[key[0] + '_prev'] = dict64[key][0]
        if key[1] == None and key[2] == PredingReportingPeriodEndDate and key[3]\
                == None and key[4] == Metadata['koncern']\
                and (key[5] == Metadata['unit'] or key[5] == None or key[5] == Metadata['language']):
            dict11[key[0] + '_prev'] = dict64[key][0]
        if key in ('{http://www.xbrl.org/2003/linkbase}schemaRef',
                   '@{http://www.w3.org/2001/XMLSchema-instance}schemaLocation'):
            Metadata[key] = dict64[key]
    compscore = 0
    if dict11.get('fsa:Assets', 'mis') != 'mis' :
        compscore = compscore + 1
    if dict11.get('fsa:Assets_prev', 'mis') != 'mis':
        compscore = compscore + 2
    if dict11.get('fsa:ProfitLoss', 'mis') != 'mis':
        compscore = compscore + 4
    if dict11.get('fsa:ProfitLoss_prev', 'mis') != 'mis':
        compscore = compscore + 8 
    Metadata['compscore'] = compscore

    return dict11


class xbrl_to_dk_11(BaseEstimator, TransformerMixin):
    """Extract features from each XBRL document for DictVectorizer etc."""

    def fit(self, x, y=None):
        return self

    def transform(self, posts):
        outputdata = []
        for indhold in posts:
            try:
                metadata = fetchlist_dk(str(indhold[0]), (indhold[1]))
                targeturl = metadata['dokumentUrl']
                xbrldoc_as_dict\
                    = xbrlinstance_to_dict(requests.get(targeturl).content)
                xbrl_as_dk_64 = xbrldict_to_xbrl_dk_64(xbrldoc_as_dict)
                xbrl_as_dk_11 = xbrl_dk_64_to_xbrl_dk_11(xbrl_as_dk_64)
                outputdata\
                    = np.append(outputdata, [xbrl_as_dk_11], axis=0)
            except:
                pass
        return outputdata
    