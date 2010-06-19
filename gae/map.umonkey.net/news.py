#!/usr/bin/env python

import urllib
import re

_CSV = 'http://spreadsheets.google.com/pub?key=0Ai-BMIF8tVI3dERnZ2FtdkNMOE5xTGVPSjBMUzcwUFE&hl=en&single=true&gid=0&output=csv'

html = urllib.urlopen('http://poselenia.ru/').read()
links = ['http://poselenia.ru' + x for x in re.findall('(/poselenie/[^"]+)', html)]

csvlinks = []
for line in urllib.urlopen(_CSV).read().decode('utf-8').split('\n'):
    for cell in line.split(','):
        if cell.startswith('http://') and cell not in csvlinks:
            csvlinks.append(cell)

for link in sorted(links):
    if link not in csvlinks:
        print 'New link:', link
