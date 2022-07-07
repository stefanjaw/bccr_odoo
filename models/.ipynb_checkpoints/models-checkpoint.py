# -*- coding: utf-8 -*-

from odoo import models, fields, api ,exceptions
import logging
log = _logging = logging.getLogger(__name__)
import datetime
import pytz

'''
from datetime import datetime
import lxml.etree as ET
import xmltodict
import requests
import time

'''

'''
class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"
    email_bccr = fields.Char(string="email_bccr",related="company_id.email_bccr")
    token_bccr = fields.Char(string="token_bccr",related="company_id.token_bccr")
'''

class Currency(models.Model):
    _inherit = "res.currency"
    rate = fields.Float(string="Rate", digits=(18, 14))

class CurrencyRate(models.Model):
    _inherit = "res.currency.rate"
    rate = fields.Float(string="Rate", digits=(18, 14))


class company(models.Model):
    _inherit = 'res.company'
    email_bccr = fields.Char(string="Correo Electronico", )
    token_bccr = fields.Char(string="Password", )
    '''
    currency_provider = fields.Selection([
        ('bccr', 'Banco Central Costa Rica'),
        ('yahoo', 'Yahoo (DISCONTINUED)'),
        ('ecb', 'European Central Bank'),
        ('fta', 'Federal Tax Administration (Switzerland)'),
        ('banxico', 'Mexican Bank'),
        ],  default='bccr', string='Service Provider')
    '''

    '''
    #cambios
    @api.multi
    def update_currency_rates(self):
    '''
    ''' This method is used to update all currencies given by the provider. Depending on the selection call _update_currency_ecb _update_currency_yahoo. '''
    '''
           log.info('-->1576089385')
           res = True
           all_good = True
           for company in self:
               if company.currency_provider == 'yahoo':
                  log.warning("Call to the discontinued Yahoo currency rate web service.")
               elif company.currency_provider == 'ecb':
                   res = company._update_currency_ecb()
               elif company.currency_provider == 'fta':
                   res = company._update_currency_fta()
               elif company.currency_provider == 'banxico':
                   res = company._update_currency_banxico()
               elif company.currency_provider == 'bccr':
                   log.info("CALL BCCR METHOD")
                   res = company._update_currency_bccr()
               if not res:
                   all_good = False
                   log.warning(('Unable to connect to the online exchange rate platform %s. The web service may be temporary down.') % company.currency_provider)
               elif company.currency_provider:
                   company.last_currency_sync_date = fields.Date.today()
           return all_good
    '''


    def _update_currency_bccr(self, date=None, indicador=None):
        log.info('--> 1573844490')
        
        company_ids = self.env['res.company'].search([
            ('email_bccr','!=', False),
            ('token_bccr','!=', False),
        ])
        _logging.info("DEF86 compnay_ids: {0}".format( company_ids ) )
        STOP90
        
        main_url = "https://gee.bccr.fi.cr/Indicadores/Suscripciones/WS/wsindicadoreseconomicos.asmx"
        
        if not indicador:
            indicador = '318' #Venta Dolar, 317 compra

        if date:
            date = datetime.strptime(date,"%Y-%m-%d")
            fechaInicio = date.strftime("%d/%m/%Y")
            fechaFinal = date.strftime("%d/%m/%Y")

        elif not date:
            fechaInicio = datetime.datetime.now().astimezone( tz=pytz.timezone('America/Costa_Rica')).strftime("%d/%m/%Y")
            fechaFinal  = datetime.datetime.now().astimezone( tz=pytz.timezone('America/Costa_Rica')).strftime("%d/%m/%Y")

        #S for Yes, N for No
        subNiveles='N'
        _logging.info("DEF97 self: {0}".format( self )  )
        STOP97
        for company_id in self:

            correoElectronico = company_id.email_bccr
            token = company_id.token_bccr

            main_url = main_url + "ObtenerIndicadoresEconomicosXML?Indicador={0}&FechaInicio={1}&FechaFinal={2}".format(
                indicador, fechaInicio, fechaFinal,
            )
            main_url = main_url + "&Nombre={0}&SubNiveles={1}&CorreoElectronico={2}&Token={3}".format(
                nombre, subNiveles, correoElectronico, token
            )
            
            _logging.info("DEF112 main_url: {0}".format( main_url ) )

            
#             try:
#                 response = requests.get(url)
#                 xml = response.text.replace('&lt;','<').replace('&gt;','>');
#                 root = ET.fromstring(xml.encode('utf-8'))
#                 ns = {'xmlns':'http://ws.sdde.bccr.fi.cr'}
#                 indicadorEconomico = root.xpath("xmlns:Datos_de_INGC011_CAT_INDICADORECONOMIC/xmlns:INGC011_CAT_INDICADORECONOMIC", namespaces=ns)[0]

#             except Exception as e:
#                 log.info('-->1576088109 %s',e)
#                 message_bccr = root.text
#                 if message_bccr:
#                     log.info('BCCR Mensaje --> %s', message_bccr)
#                     raise exceptions.Warning((message_bccr))
#                 return False

#             try:
#                 value = float(indicadorEconomico.xpath("xmlns:NUM_VALOR", namespaces=ns)[0].text)
#                 date = indicadorEconomico.xpath("xmlns:DES_FECHA", namespaces=ns)[0].text
#                 rate_calculation = company_id.rate_calculation(value)
#                 rate_model = company_id.env['res.currency.rate']
#                 currency = company_id.env['res.currency'].search([('name','=','USD')])

#                 if company_id.env['res.currency.rate'].search([('currency_id','=',currency.id),('name','=',date),('company_id','=',company_id.id)]):
#                     log.info("---> El tipo de cambio de hoy ya existe para la compañia %s %s!!" % (company_id.name,fechaInicio))
#                     #return False
#                 else:        
#                     currency.write({ 'rate_ids':  [ (0,0, {'name': date,'rate': rate_calculation,'currency_id':currency.id,'company_id':company.id})]   })

#             except Exception as e:
#                 log.info('-->1576088246 %s',e)
#                 return False

#             return True
        
    def rate_calculation(self,value):
        return 1 / value
