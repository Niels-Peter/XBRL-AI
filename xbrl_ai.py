#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 30 09:40:44 2018

@author: niels-peter
"""

__title__ = 'xbrl_ai'
__version__ = '0.0.4'
__author__ = 'Niels-Peter Rønmos'

from xml.etree.ElementTree import fromstring
from xmljson import badgerfish as bf
import collections



def xbrlinstance_to_dict(xbrlinstance):
    """
    Transforming XBRL-instant to python dictionary
    """
    # From XBRL to dict
    xbrldict = bf.data(fromstring(xbrlinstance))['{http://www.xbrl.org/2003/instance}xbrl']
    # Extract unit information
    unitlist = {}
    unit = xbrldict['{http://www.xbrl.org/2003/instance}unit']
    if isinstance(unit, list):
        for post in unit:
            try:
                unitlist[post['@id']] = (post['{http://www.xbrl.org/2003/instance}measure'])['$']
            except LookupError:
                pass               
            try:
                divide = post['{http://www.xbrl.org/2003/instance}divide']
                unitlist[post['@id']] = ((divide['{http://www.xbrl.org/2003/instance}unitNumerator'])['{http://www.xbrl.org/2003/instance}measure'])['$'] + '/'\
                    + ((divide['{http://www.xbrl.org/2003/instance}unitDenominator'])['{http://www.xbrl.org/2003/instance}measure'])['$']
            except LookupError:
                pass                           
    elif isinstance(unit, dict):
        try:
            unitlist[unit['@id']] = (unit['{http://www.xbrl.org/2003/instance}measure'])['$']
        except LookupError:
            pass               
        try:
            divide = unit['{http://www.xbrl.org/2003/instance}divide']
            unitlist[unit['@id']] = ((divide['{http://www.xbrl.org/2003/instance}unitNumerator'])['{http://www.xbrl.org/2003/instance}measure'])['$'] + '/'\
                + ((divide['{http://www.xbrl.org/2003/instance}unitDenominator'])['{http://www.xbrl.org/2003/instance}measure'])['$']
        except LookupError:
                pass
    # Extract context information
    contexts = xbrldict['{http://www.xbrl.org/2003/instance}context']
    contextlist = {}
    for post in contexts:
        identifier = scheme = startdate = enddate\
            = instant = explicit = typed = None
        entity = post['{http://www.xbrl.org/2003/instance}entity']
        for element in entity:
            try:
                identifier = (entity[element])['$']
                scheme = (entity[element])['@scheme']
            except LookupError:
                pass
            try:
                explicit = (entity['{http://www.xbrl.org/2003/instance}segment'])\
                    ['{http://xbrl.org/2006/xbrldi}explicitMember']
            except LookupError:
                pass
            try:
                typed = (entity['{http://www.xbrl.org/2003/instance}segment'])\
                    ['{http://xbrl.org/2006/xbrldi}typedMember']
            except LookupError:
                pass
        period = post['{http://www.xbrl.org/2003/instance}period']
        try:
            startdate\
                = (period['{http://www.xbrl.org/2003/instance}startDate'])['$']
        except LookupError:
            startdate = None
        try:
            enddate\
                = (period['{http://www.xbrl.org/2003/instance}endDate'])['$']
        except LookupError:
            enddate = None
        try:
            instant\
                = (period['{http://www.xbrl.org/2003/instance}instant'])['$']
        except LookupError:
            instant = None
        try:
            explicit = (post['{http://www.xbrl.org/2003/instance}scenario'])\
                ['{http://xbrl.org/2006/xbrldi}explicitMember']
        except LookupError:
            pass
        try:
            typed = (post['{http://www.xbrl.org/2003/instance}scenario'])\
                ['{http://xbrl.org/2006/xbrldi}typedMember']
        except LookupError:
            pass
        contextlist[post['@id']] = [identifier,\
                   scheme, startdate, enddate, instant, explicit, typed]
    for opryd in ('{http://www.xbrl.org/2003/instance}context',
                  '{http://www.xbrl.org/2003/instance}unit'):
        del xbrldict[opryd]
    # Add unit and context infdromation on concepts
    for concept in xbrldict:
        if isinstance(xbrldict[concept], dict):
            try:
                (xbrldict[concept])['context']\
                    = contextlist[(xbrldict[concept])['@contextRef']]
            except LookupError:
                pass
            try:
                (xbrldict[concept])['unit']\
                    = unitlist[(xbrldict[concept])['@unitRef']]
            except LookupError:
                pass
        if isinstance(xbrldict[concept], list):
            for i in range(0, len(xbrldict[concept])):
                try:
                    ((xbrldict[concept])[i])['context']\
                        = contextlist[((xbrldict[concept])[i])['@contextRef']]
                except LookupError:
                    pass
                try:
                    ((xbrldict[concept])[i])['unit']\
                        = unitlist[((xbrldict[concept])[i])['@unitRef']]
                except LookupError:
                    pass
    return xbrldict


def xbrldict_to_xbrl_54(xbrldict):

    def get_xbrlkey(post, char):
        return post[post.index(char)+1:]

    def explicit_list(explicit):
        explicit_liste = {}
        dimension_list = []
        label_extend = ''
        if type(explicit).__name__ == 'OrderedDict':
            explicit_liste[get_xbrlkey(explicit['@dimension'], ":")]\
                = get_xbrlkey(explicit['$'], ":")
        if isinstance(explicit, list):
            for element in explicit:
                explicit_liste[get_xbrlkey(element['@dimension'], ":")]\
                    = get_xbrlkey(element['$'], ":")        
        explicit_liste_od = collections.OrderedDict(sorted(explicit_liste.items()))
        for keys in explicit_liste_od:
            label_extend = label_extend + '_' + explicit_liste_od[keys]
            dimension_list.append(keys)
        return label_extend, dimension_list

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

    def concept_data(inputdata):
        value = inputdata.get('$', None)
        unit = inputdata.get('unit', None)
        decimals = inputdata.get('@decimals', None)
        context = inputdata['context']
        lang = inputdata.get('@{http://www.w3.org/XML/1998/namespace}lang', None)
        if type(lang).__name__ != 'NoneType':
            lang = 'lang:' + lang
        startdate = context[2]
        enddate = context[3]
        instant = context[4]
        if type(enddate).__name__ != 'str':
            enddate = instant
        explicit = context[5]
        typed = context[6]
        label_extend, dimension_list_extend = explicit_list(explicit)
        label_typed, label_typed_id, dimension_list_typed = typed_list(typed)
        dimension_list = dimension_list_extend.append(dimension_list_typed)
        if label_typed_id == '':
            label_typed_id = None
        return value, unit, decimals, startdate, enddate, lang,\
            label_extend, label_typed, label_typed_id, dimension_list_extend

    
    #schemaRef = (XBRL['{http://www.xbrl.org/2003/linkbase}schemaRef'])\
    #['@{http://www.w3.org/1999/xlink}href']
    dict54 = {}
    for post in xbrldict:
        if post not in ('{http://www.xbrl.org/2003/linkbase}s, xbrldict_to_xbrl_54chemaRef',
                        '@{http://www.w3.org/2001/XMLSchema-instance}schemaLocation'):
            ref = post[:post.index('}')]
            xbrlref = ref[(ref.rfind('/') - len(ref) + 1):]
            if type(xbrldict[post]).__name__ == 'list':
                for element in xbrldict[post]:
                    if element.get('context', 'missing') != 'missing':
                        value, unit, decimals, startdate, enddate, lang, label_extend,\
                            label_typed, label_typed_id, dimension_list = concept_data(element)
                        concept = xbrlref + ':' + get_xbrlkey(post, '}') + label_extend + label_typed
                        if type(unit).__name__ == 'NoneType':
                            unit = lang
                        nogle = (concept, startdate, enddate, label_typed_id, unit)
                        if nogle in dict54 and dict54[nogle][0] != value:
                            print('!!!!!!!!!', nogle, value, unit, decimals, dict54[nogle])
                        if len(str(dimension_list)) < 5:
                            dimension_list = None
                        dict54[nogle] = [value, unit, decimals, dimension_list]
            if type(xbrldict[post]).__name__ == 'OrderedDict':
                if (xbrldict[post]).get('context', 'missing') != 'missing':
                    value, unit, decimals, startdate, enddate, lang, label_extend, label_typed,\
                        label_typed_id, dimension_list = concept_data(xbrldict[post])
                    concept = xbrlref + ':' + get_xbrlkey(post, '}') + label_extend + label_typed
                    if type(unit).__name__ == 'NoneType':
                        unit = lang
                    nogle = (concept, startdate, enddate, label_typed_id, unit)
                    if nogle in dict54 and dict54[nogle][0] != value:
                        print('!!!!!!!!!', nogle, value, unit, decimals, dict54[nogle])
                    if len(str(dimension_list)) < 5:
                        dimension_list = None
                    dict54[nogle] = [value, unit, decimals, dimension_list]
        if post in ('{http://www.xbrl.org/2003/linkbase}schemaRef',
                    '@{http://www.w3.org/2001/XMLSchema-instance}schemaLocation'):
            dict54[post] = xbrldict[post]
    return dict54
