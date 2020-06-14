# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime

from lxml import etree
from odoo.addons.web.controllers.main import xml2json_from_elementtree

import pytz

import requests

import logging
log = logging.getLogger(__name__)

class company(models.Model):
    _inherit = ['res.company']

    log.info("\nLoaded class res.company inherit\n")
    bccr_email = fields.Char(string="Correo Electronico")

    bccr_token = fields.Char(string="Password")
    
    currency_provider = fields.Selection([
        ('ecb', 'European Central Bank'),
        ('fta', 'Federal Tax Administration (Switzerland)'),
        ('banxico', 'Mexican Bank'),
        ('boc', 'Bank Of Canada'),
        ('xe_com', 'xe.com'),
        ('bccr', 'Banco Central Costa Rica'),
    ], default='ecb', string='Service Provider')
      
    @api.model
    def create(self, vals):
        ''' Change the default provider depending on the company data.'''
        if vals.get('country_id') and 'currency_provider' not in vals:
            code_providers = {'CH' : 'fta', 'MX': 'banxico', 'CA' : 'boc', 'CR' : 'bccr'}
            cc = self.env['res.country'].browse(vals['country_id']).code.upper()
            if cc in code_providers:
                vals['currency_provider'] = code_providers[cc]
        return super(ResCompany, self).create(vals)
    
    @api.model
    def set_special_defaults_on_install(self):
        ''' At module isntallation, set the default provider depending on the company country.'''
        all_companies = self.env['res.company'].search([])
        for company in all_companies:
            if company.country_id.code == 'CH':
                # Sets FTA as the default provider for every swiss company that was already installed
                company.currency_provider = 'fta'
            elif company.country_id.code == 'MX':
                # Sets Banxico as the default provider for every mexican company that was already installed
                company.currency_provider = 'banxico'
            elif company.country_id.code == 'CA':
                # Bank of Canada
                company.currency_provider = 'boc'
            elif company.country_id.code == 'CR':
                # Banco Central de Costa Rica
                company.currency_provider = 'bccr'
            else:
                company.currency_provider = 'ecb'

    
    def _parse_bccr_data(self, available_currencies):
        ''' This method is used to update the currencies by using BCCR service provider.
            Rates are given against COLONES CRC
        '''
        
        #318 Venta Dolar, 317 compra
        indicador = str(318)
        
        #S for Yes, N for No
        subNiveles='N'      
        
        tzcr = pytz.timezone('America/Costa_Rica')

        date = datetime.datetime.now(tz=tzcr)
        fechaInicio = str( date.strftime("%d/%m/%Y") )
        fechaFinal = str( date.strftime("%d/%m/%Y") )
        
        bccr_email = str( self.bccr_email )
        bccr_token = str( self.bccr_token )

        request_url = "https://gee.bccr.fi.cr/Indicadores/Suscripciones/WS/wsindicadoreseconomicos.asmx/ObtenerIndicadoresEconomicosXML?Indicador={}&FechaInicio={}&FechaFinal={}&Nombre=dmm&SubNiveles={}&CorreoElectronico={}&Token={}".format(indicador,fechaInicio,fechaFinal,subNiveles,bccr_email,bccr_token)
        
        try:
            parse_url = requests.request('GET', request_url)
        except:
            #connection error, the request wasn't successful 
            return False
        
        try:
            xmlstr = etree.fromstring(parse_url.content)
        except:
            log.info("Modulo BCCR: URL Incorrecta\n\n")
            return False
        
        data = xml2json_from_elementtree(xmlstr)
                
        log.info("\nBCCR DATA\n%s\n", data)

        try:
            xml_etree = etree.fromstring( data['children'][0] )
        except:
            log.info("Modulo BCCR: Usuario y Contraseña incorrectos\n\n")
            return False
        
        exchange_rate_usd = float( xml_etree[0][2].text )
        
        # PENDIENTE CUANDO HAY ERRORES LOS IFs
        odoo_exchange_rate_format = 1 / exchange_rate_usd

        date = datetime.datetime.now(tz=tzcr)
        date_current = date.strftime("%Y,%m,%d")
        
        rslt = {}
        rslt['USD'] = ( odoo_exchange_rate_format, datetime.datetime.now(tz=tzcr) )
        
        available_currency_names = available_currencies.mapped('name')
        if rslt and 'CRC' in available_currency_names:
            rslt['CRC'] = (1.0, datetime.datetime.now(tz=tzcr) )
        
        return rslt
