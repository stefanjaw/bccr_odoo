# -*- coding: utf-8 -*-

from odoo import models, fields, api ,exceptions
import logging
log = _logging = logging.getLogger(__name__)
import datetime
import pytz
import urllib.parse
from lxml import etree
import requests


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

    def _update_currency_bccr(self, params={} ):
        log.info('1657212414, 1573844490')
        
        if params.get('main_url'):
            main_url = params.get('main_url')
        else:
            main_url = "https://gee.bccr.fi.cr/Indicadores/Suscripciones/WS/wsindicadoreseconomicos.asmx"
        
        company_ids = self.env['res.company'].search([
            ('email_bccr','!=', False),
            ('token_bccr','!=', False),
        ])
        
        if len( company_ids ) == 0:
            _logging.info("  No company detected to update BCCR")
        
        if params.get('indicador'):
            indicador = params.get('indicador')
        else:
            indicador = '318' #Venta Dolar, 317 compra

        if params.get('date'):
            date1 = datetime.datetime.strptime( params.get('date'),"%Y-%m-%d")
            fechaInicio = date1.strftime("%d/%m/%Y")
            fechaFinal = date1.strftime("%d/%m/%Y")
        else:
            fechaInicio = datetime.datetime.now().astimezone( tz=pytz.timezone('America/Costa_Rica')).strftime("%d/%m/%Y")
            fechaFinal  = datetime.datetime.now().astimezone( tz=pytz.timezone('America/Costa_Rica')).strftime("%d/%m/%Y")

        #S for Yes, N for No
        if params.get('subNiveles'):
            subNiveles=params.get('subNiveles')
        else:
            subNiveles='N'
        
        for company_id in company_ids:
            
            if str(indicador) == '318':
                currency_id = company_id.env['res.currency'].search( [('name','=','USD')] )
            else:
                currency_id = False

            if currency_id == False:
                _logging.info("  Currency not defined with Indicador {0} for Company: {1}".format(
                    indicador, company_id.name ) )
                continue

            req_url = main_url + "/ObtenerIndicadoresEconomicosXML?Indicador={0}&FechaInicio={1}&FechaFinal={2}".format(
                indicador, fechaInicio, fechaFinal,
            )
            req_url = req_url + "&Nombre={0}&SubNiveles={1}&CorreoElectronico={2}&Token={3}".format(
                urllib.parse.quote( company_id.name ), subNiveles, company_id.email_bccr, company_id.token_bccr
            )

            try:
                response_obj = requests.get(req_url)
                xml_txt = response_obj.text.replace('&lt;','<').replace('&gt;','>');
                response_xml = etree.fromstring(xml_txt.encode('utf-8'))
                response_nsmap = response_xml.nsmap
                response_nsmap['xmlns'] = response_nsmap[None]
                response_nsmap.pop(None)

                bccr_value = float(response_xml.xpath(u'//xmlns:NUM_VALOR', namespaces=response_nsmap)[0].text)
                bccr_date = response_xml.xpath(u'//xmlns:DES_FECHA', namespaces=response_nsmap)[0].text

            except Exception as e:
                log.info('-->1576088109 %s',e)
                message_bccr = root.text
                if message_bccr:
                    log.info('BCCR Mensaje --> %s', message_bccr)
                    raise exceptions.Warning((message_bccr))
                return False

            record_exist = self.env['res.currency.rate'].sudo().search([
                ('name','=',bccr_date),
                ('currency_id','=',currency_id.id),
                ('company_id','=',company_id.id),
            ])
            if len( record_exist ) > 0:
                _logging.info("  Exchange Record already exists: {0} - {1} {2}".format(
                    bccr_date, currency_id.name, bccr_value
                ))
                continue
            
            record_id = self.env['res.currency.rate'].sudo().create({
                'name': bccr_date,
                'rate': float( 1 / bccr_value ),
                'currency_id': currency_id.id,
                'company_id': company_id.id,
            })
            
            _logging.info("  Created Record: {0}".format( record_id ) )
        return True
