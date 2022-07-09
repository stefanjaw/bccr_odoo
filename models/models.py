# -*- coding: utf-8 -*-

from odoo import models, fields, api ,exceptions, _
import logging
log = _logging = logging.getLogger(__name__)
import datetime
import pytz
import urllib.parse
from lxml import etree
import requests

from odoo.exceptions import ValidationError

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
    
    currency_provider = fields.Selection(selection_add=[('bccr', 'Banco Central de Costa Rica')])

    def _parse_bccr_data(self, available_currencies):
        log.info('1657212414') #1573844490
        
        for currency_id in available_currencies:
            if currency_id.name == "USD" and not self.email_bccr or not self.token_bccr:
                _logging.info("  Currency: {0}, NOT CONFIGURED EMAIL OR TOKEN IN THE COMPANY".format(
                    currency_id.name )  )
                continue
            elif currency_id.name == "USD" and self.email_bccr and self.token_bccr:
                params = {
                    'company_name': self.name,
                    'indicador': 318,
                    'email_bccr': self.email_bccr,
                    'token_bccr': self.token_bccr,
                }
                bccr_data = self._get_currency_bccr(params)
                rslt = {}
                if len( bccr_data ) == 3:
                    rslt[currency_id.name] = ( 1.0/ bccr_data.get('bccr_value'), fields.Date.today() )
                    rslt[self.currency_id.name] = ( 1.0, fields.Date.today() )
                else:
                    msg = "1657388130 ERROR: Escalate with support Currency: {0} BCCR Data: {1}".format(
                        currency_id, bccr_data)
                    raise ValidationError( _( msg ) )
            else:
                continue

        return rslt


    def _get_currency_bccr(self, params={} ):
        _logging.info("1657388479")
        '''params:
            company_name: string
            indicador: 318 Venta Dolar, 317 compra
            subNiveles: #S for Yes, N for No
            date: yyyy-mm-dd
        '''
        
        main_url = "https://gee.bccr.fi.cr/Indicadores/Suscripciones/WS/wsindicadoreseconomicos.asmx"
        
        if not params.get('email_bccr'):
            msg = "1657385110 ERROR: email_bccr missing in params"
            raise ValidationError( _( msg ) )
        elif not params.get('token_bccr'):
            msg = "1657385120 ERROR: token_bccr missing in params"
            raise ValidationError( _( msg ) )        
        elif not params.get('company_name'):
            msg = "1657385130 ERROR: company_name missing in params"
            raise ValidationError( _( msg ) )
        elif not params.get('indicador'):
            msg = "1657385140 ERROR: indicador missing in params"
            raise ValidationError( _( msg ) )
        
        if params.get('subNiveles'):
            subNiveles = params.get('subNiveles')
        else:
            subNiveles='N'  #S for Yes, N for No

        if params.get('date'):
            date1 = datetime.datetime.strptime( params.get('date'),"%Y-%m-%d")
            fechaInicio = date1.strftime("%d/%m/%Y")
            fechaFinal = date1.strftime("%d/%m/%Y")
        else:
            fechaInicio = datetime.datetime.now().astimezone(
                tz=pytz.timezone('America/Costa_Rica')).strftime("%d/%m/%Y")
            fechaFinal  = datetime.datetime.now().astimezone(
                tz=pytz.timezone('America/Costa_Rica')).strftime("%d/%m/%Y")

        req_url = main_url + \
            "/ObtenerIndicadoresEconomicosXML?Indicador={0}&FechaInicio={1}&FechaFinal={2}".format(
                params.get('indicador'), fechaInicio, fechaFinal)
        req_url = req_url + "&Nombre={0}&SubNiveles={1}&CorreoElectronico={2}&Token={3}".format(
            urllib.parse.quote( params.get('company_name') ),
            subNiveles, params.get('email_bccr'), params.get('token_bccr') )
        
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
            log.info('-->1576088109 Error: %s',e)
            message_bccr = response_obj.text
            if message_bccr:
                log.info('BCCR Mensaje --> %s', message_bccr)
                raise ValidationError( _( message_bccr ) )
            return False
        
        return {
            'indicador': params.get('indicador'),
            'bccr_value': bccr_value,
            'bccr_date': bccr_date,
        }
