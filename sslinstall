#! /usr/bin/python3.6
import json, os, getpass, sys
from classes.Dom import Domain as Dom
from classes.whm import WHM

if getpass.getuser() != 'root':
    print('This Script must be run as Root.\n \
        Come back when you have the right privileges \n \
            Maybe try sudo?')
    sys.exit(1)

if getpass.getuser() == 'root':
    domain = Dom()
    whm = WHM()
    whm.install_ssl(domain.domain_data['domain_name'], 
        domain.csr_data['key'], 
        domain.sslCert['certificate'], 
        domain.sslCert['cabundle'])
