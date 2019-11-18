# -*- coding: utf-8 -*-

from odoo import models, fields, api ,exceptions
from lxml import etree
import xmltodict

import time
import logging

_logger = logging.getLogger(__name__)
log = logging.getLogger(__name__)

class Currency(models.Model):
    _inherit = "res.currency"

    rate = fields.Float(string="Rate", digits=(18, 12))
    
class company(models.Model):
    _inherit = 'res.company'
    currency_provider = fields.Selection([
        ('bccr', 'Banco Central Costa Rica'),
        ('yahoo', 'Yahoo (DISCONTINUED)'),
        ('ecb', 'European Central Bank'),
        ('fta', 'Federal Tax Administration (Switzerland)'),
        ('banxico', 'Mexican Bank'),
        ],  default='bccr', string='Service Provider')


    #cambios
    @api.multi
    def update_currency_rates(self):
           ''' This method is used to update all currencies given by the provider. Depending on the selection call _update_currency_ecb _update_currency_yahoo. '''
           res = True
           all_good = True
           for company in self:
               if company.currency_provider == 'yahoo':
                   _logger.warning("Call to the discontinued Yahoo currency rate web service.")
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
                   _logger.warning(_('Unable to connect to the online exchange rate platform %s. The web service may be temporary down.') % company.currency_provider)
               elif company.currency_provider:
                   company.last_currency_sync_date = fields.Date.today()
           return all_good



    def _update_currency_bccr(self):

        log.info('--> 1573844490')
        indicador = '318' #Venta Dolar, 317 compra
        fechaInicio = time.strftime("%d/%m/%Y")
        fechaFinal = time.strftime("%d/%m/%Y")
        #S for Yes, N for No
        subNiveles='N'

        url="http://indicadoreseconomicos.bccr.fi.cr/indicadoreseconomicos/WebServices/wsIndicadoresEconomicos.asmx/ObtenerIndicadoresEconomicosXML?tcIndicador="+indicador+"&tcFechaInicio="+fechaInicio+"&tcFechaFinal="+fechaFinal+"&tcNombre=dmm&tnSubNiveles="+subNiveles
        try:
            tree = etree.parse(url)
            root = tree.getroot()
            dic = xmltodict.parse(root.text)
        except:
            return False

        value = float(dic[u'Datos_de_INGC011_CAT_INDICADORECONOMIC'][u'INGC011_CAT_INDICADORECONOMIC'][u'NUM_VALOR'])
        date = dic[u'Datos_de_INGC011_CAT_INDICADORECONOMIC'][u'INGC011_CAT_INDICADORECONOMIC'][u'DES_FECHA']

        rate_calculation = self.rate_calculation(value)
        rate_model = self.env['res.currency.rate']


        currency = self.env['res.currency'].search([('name','=','USD')])

        if self.env['res.currency.rate'].search([('currency_id','=',currency.id),('name','=',date)]):
            raise exceptions.Warning(("El tipo de cambio de hoy ya existe!"))

        '''id_rate = rate_model.create(
            {'name': date,
             'rate': rate_calculation,
             'currency_id':currency.id,
            }
         )'''

        '''log.info('--> id rate %s',id_rate.id)'''

        currency.write({ 'rate_ids':  [ (0,0, {'name': date,'rate': rate_calculation,'currency_id':currency.id})]   })

        return True


    def rate_calculation(self,value):
        return 1 / value
