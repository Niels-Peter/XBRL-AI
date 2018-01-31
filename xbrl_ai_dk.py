#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 31 09:10:49 2018

@author: niels-peter
"""
import time
import requests


__title__ = 'xbrl_ai_dk'
__version__ = '0.0.1'
__author__ = 'Niels-Peter Rønmos'


def fetchlist_dk(cvrnummer, date='dd', reports='AARSRAPPORT', style='dict'):
    """
    Opslag til ERST json indeks indeholdende regnskaber i XBRL eller uden XBRL:

    CVRnummer:
        8 cifret string bestående af tal.

    date:
        Tekststring med formattet: YYYY-MM-DD
        dd: Default. Dags dato (time)

        Anvendes kun hvis style == 'dict', dvs. hvis der ønsker kun 1 svar i kaldet!!!!
        Retursvar indeholder seneste regnskab med en slutdato før eller lig med date

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
        dict_post['offentliggoerelsesTidspunkt'] = (post['_source'])['offentliggoerelsesTidspunkt']
        dict_post['offentliggoerelsestype'] = (post['_source'])['offentliggoerelsestype']
        dict_post['omgoerelse'] = (post['_source'])['omgoerelse']
        dict_post['sagsNummer'] = (post['_source'])['sagsNummer']
        dict_post['startDato'] = (((post['_source'])['regnskab'])['regnskabsperiode'])['startDato']
        dict_post['slutDato'] = (((post['_source'])['regnskab'])['regnskabsperiode'])['slutDato']
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
