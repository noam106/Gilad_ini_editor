from configparser import ConfigParser

import config
from config import *

if __name__ == '__main__':
    main_contract_tuple = ('UVXY', 'VXX', 'VIXY', 'SVIX', 'UVIX', 'SVXY')
    contract_type_tuple = ('regular', 'inverse')
    print('Hi Gilad')
    accounts = input('Which accounts would you like to change? ')
    accounts_list = accounts.split()
    print(accounts_list)
    # need to validayt the accuonts

    try:
        contract_leveragy = float(input('insert the contract leveragy: '))
    except ValueError:
        print('contract leveragy need to be a number')

    contract_type = input()

    m = config.Config
    m.ib['accounts'] = section




