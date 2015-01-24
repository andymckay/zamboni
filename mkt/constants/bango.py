# -*- coding: utf8 -*-
from lib.constants import ALL_COUNTRIES, ALL_CURRENCIES

from tower import ugettext_lazy as _lazy

# From page 10 of the Mozilla Exporter API docs v1.0.0
#
# BDT not in docs, but added in for bug 1043481.
BANGO_CURRENCIES = ['AUD', 'BDT', 'CAD', 'CHF', 'COP', 'DKK', 'EGP', 'EUR',
                    'GBP', 'IDR', 'MXN', 'MYR', 'NOK', 'NZD', 'PHP', 'PLN',
                    'QAR', 'SEK', 'SGD', 'THB', 'USD', 'ZAR']
BANGO_CURRENCIES = dict((k, ALL_CURRENCIES[k]) for k in BANGO_CURRENCIES)

BANGO_OUTPAYMENT_CURRENCIES = ['EUR', 'GBP', 'USD']
BANGO_OUTPAYMENT_CURRENCIES = [(k, ALL_CURRENCIES[k])
                               for k in BANGO_OUTPAYMENT_CURRENCIES]

BANGO_COUNTRIES = [(k, v) for k, v in ALL_COUNTRIES.items()]
# Bango also recognises these region, that aren't ISO 3166
BANGO_COUNTRIES.append(('KOS', _lazy(u'Kosovo')))
BANGO_COUNTRIES.append(('SCG', _lazy(u'Serbia and Montenegro')))
