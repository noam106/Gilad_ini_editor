import configparser
import re
import logging
import numpy as np

class Config:

    def __init__(self, path):

        self.config_obj = configparser.ConfigParser(converters={'list': lambda x: [i.strip() for i in x.split(',')]})
        logging.info(f'Reading config from {path} ...')
        self.path = path
        self.config_obj.read(self.path)
        self.general = {}
        self.ib = {}
        self.policy = {}
        self.slack = {}
        self.reports = {}

        self.config_to_dict()
        logging.info('Done.')

    def config_to_dict(self):

        # general
        section = self.config_obj['general']
        self.general['name'] = section.get('name')

        # IB params
        section = self.config_obj['IB']
        self.ib['port'] = section.getint('port')
        self.ib['host'] = section.get('host', fallback='127.0.0.1')
        self.ib['user_id'] = section.getint('user_id', fallback=100)
        self.ib['autostart'] = section.getboolean('autostart', fallback=False)
        self.ib['username'] = section.get('username', fallback='')
        self.ib['password'] = section.get('password', fallback='')
        # self.ib['account_id'] = section.get('account_id')
        self.ib['accounts'] = section.getlist('accounts')
        self.ib['is_advisor'] = section.getboolean('is_advisor')






        
        # self.ib['IBC_params_file'] = section.get('IBC_params_file')
        # self.ib['timezone'] = section.get('timezone', fallback='US/Eastern')
        # self.ib['backfill_days'] = section.getint('backfill_days', fallback=10)
        

        # policy params
        section = self.config_obj['policy']
        self.policy['trade_weekends'] = section.getboolean('trade_weekends', fallback=False)
        self.policy['long_positions'] = section.getboolean('long_positions', fallback=True)
        self.policy['short_positions'] = section.getboolean('short_positions', fallback=True)
        self.policy['hedge'] = section.getboolean('hedge', fallback=False)
        self.policy['hedge_percent'] = section.getfloat('hedge_percent', fallback=0.5)
        self.policy['max_put_risk'] = section.getfloat('max_put_risk', fallback=0.05)
        self.policy['stakes'] = [int(i) for i in section.getlist('stakes')]
        self.policy['max_portfolio'] = section.getint('max_portfolio', fallback=0)
        self.policy['limit_orders'] = section.getboolean('limit_orders', fallback=False)
        self.policy['distribute_orders'] = section.getboolean('distribute_orders', fallback=False)
        self.policy['distribute_quantity'] = section.getint('distribute_quantity', fallback=100000)
        self.policy['distribute_time'] = section.getfloat('distribute_time', fallback=0.1)
        self.policy['distribute_order_type'] = section.getboolean('distribute_order_type', fallback=True)
        self.policy['main_contract'] = section.get('main_contract', fallback='UVXY')
        self.policy['contract_leverage'] = section.getfloat('contract_leverage', fallback=1.5)
        self.policy['contract_type'] = section.get('contract_type', fallback='regular')
        
        # adjust to contract leverage
        self.policy['hedge_percent'] = self.policy['hedge_percent'] * self.policy['contract_leverage']
        self.policy['max_put_risk'] = self.policy['max_put_risk'] * self.policy['contract_leverage']
        
        # protect other account if not advisor
        if not self.ib['is_advisor']:
            if len(self.ib['accounts']) > 1:
                logging.warning(f'Only one account allowed if not advisor. Using first account. {self.ib["accounts"]} --> {self.ib["accounts"][0]}')
                self.ib['accounts'] = [self.ib['accounts'][0]]  # only use first account
            if len(self.policy['stakes']) > 1:
                logging.warning(f'Only one stake allowed if not advisor. Using first stake. {self.policy["stakes"]} --> {self.policy["stakes"][0]}')
                self.policy['stakes'] = [self.policy['stakes'][0]]  # only use first stake

        # slack
        section = self.config_obj['slack']
        self.slack['prefix'] = section.get('prefix', fallback='')
        self.slack['conf_messages'] = section.getboolean('conf_messages', fallback=False)

        # reports
        section = self.config_obj['reports']
        self.reports['end_day_email'] = section.getboolean('end_day_email', fallback=False)
        # validate email addresses
        adresses = section.getlist('email_address', fallback='')
        self.reports['email_address'] = []
        for address in adresses:
            if re.fullmatch(r"[^@\s]+@[^@\s]+\.[a-zA-Z0-9]+$", address):
                self.reports['email_address'].append(address)
        if not len(self.reports['email_address']):
            logging.warning('No eligible client email found. End day email summary will not be sent.')
            self.reports['end_day_email'] = False

    # set new account fo Gilad

    def set_accounts(self, new_accounts: list[str]):
        self.config_obj.set('ib', 'accounts', str(new_accounts)[1:-1])
        with open(self.path, 'w') as configfile:
            self.config_obj.write(configfile)

    def set_main_contract(self, new_main_contract: list):
        main_contract_tuple = ('UVXY', 'VXX', 'VIXY', 'SVIX', 'UVIX', 'SVXY')
        for i in new_main_contract:
            if i not in main_contract_tuple:
                raise ValueError('there is problem with the contract name')
            else:
                self.config_obj.set('policy', 'main_contract', str(new_main_contract)[1:-1])
                with open(self.path, 'w') as configfile:
                    self.config_obj.write(configfile)

    def set_contract_leverage(self, new_contract_leverage: str):
        self.config_obj.set('policy', 'contract_leverage', new_contract_leverage)
        with open(self.path, 'w') as configfile:
            self.config_obj.write(configfile)

    def set_contract_type(self, new_contract_type: str):
        contract_type_tuple = ('regular', 'inverse')
        if new_contract_type in contract_type_tuple:
            self.config_obj.set('policy', 'contract_type', new_contract_type)
            with open(self.path, 'w') as configfile:
                self.config_obj.write(configfile)
        else:
            raise ValueError('The contract type dose not exist')

    def update_config(self, portfolio=0, stakes=None):
        
        # update max portfolio
        if int(portfolio) > self.policy['max_portfolio']:
            self.config_obj.set('policy', 'max_portfolio', f'{int(portfolio)}')

        # update stake
        if stakes != None and np.any(np.greater(stakes, self.policy['stakes'])):
            self.config_obj.set('policy', 'stakes', str([int(i) for i in stakes])[1:-1])

        # update ini file
        with open(self.path, 'w') as configfile:
            self.config_obj.write(configfile)
        
        
