#!/usr/bin/env python3.6
import mwclient, mwparserfromhell,example,configparser, timeit
site = mwclient.Site(('https','en.wikipedia.org'), '/w/')
config = configparser.RawConfigParser()
config.read('credentials.txt')
site.login(config.get('enwikidep','username'), config.get('enwikidep', 'password'))
utils = [config,site,True]
example.process(site,"Pages using Columns-list with deprecated parameters",utils,0,True,1)
del site
del config
del utils
