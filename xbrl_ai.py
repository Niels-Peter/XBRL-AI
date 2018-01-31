#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 30 09:40:44 2018

@author: niels-peter
"""

__title__ = 'xbrl_ai'
__version__ = '0.0.3'
__author__ = 'Niels-Peter Rønmos'

from xml.etree.ElementTree import fromstring
from xmljson import badgerfish as bf


def xbrlinstance_to_dict(xbrlinstance):
    """
    Transforming XBRL-instant to python dictionary
    """
    # From XBRL to dict
    xbrldict = bf.data(fromstring(xbrlinstance))['{http://www.xbrl.org/2003/instance}xbrl']
    # Extract unit information
    unitlist = {}
    unit = xbrldict['{http://www.xbrl.org/2003/instance}unit']
    if type(unit).__name__ == 'list':
        for post in unit:
            unitlist[post['@id']]\
                = (post['{http://www.xbrl.org/2003/instance}measure'])['$']
    if type(unit).__name__ == 'OrderedDict':
        unitlist[unit['@id']]\
            = (unit['{http://www.xbrl.org/2003/instance}measure'])['$']
    # Extract context information
    contexts = xbrldict['{http://www.xbrl.org/2003/instance}context']
    contextlist = {}
    for post in contexts:
        identifier = scheme = startdate = enddate\
            = instant = explicit = typed = None
        entity = post['{http://www.xbrl.org/2003/instance}entity']
        for element in entity:
            identifier = (entity[element])['$']
            scheme = (entity[element])['@scheme']
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
    # RemCOcoove unit and context information as they are extracted
    for opryd in ('{http://www.xbrl.org/2003/instance}context',
                  '{http://www.xbrl.org/2003/instance}unit'):
        del xbrldict[opryd]
    # Add unit and context infdromation on concepts
    for concept in xbrldict:
        if type(xbrldict[concept]).__name__ == 'OrderedDict':
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
        if type(xbrldict[concept]).__name__ == 'list':
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
