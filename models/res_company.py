# -*- coding: utf-8 -*-

from odoo import models, fields, exceptions #, api
from datetime import datetime
import lxml.etree as ET
import xmltodict
import requests
import time
import logging

_logging = _logger = logging.getLogger(__name__)

class company(models.Model):
    _inherit = 'res.company'
    last_currency_sync_date = fields.Date(string="Last Sync Date", readonly=True)
    email_bccr = fields.Char(string="Correo Electronico", )
    token_bccr = fields.Char(string="Password", )

    currency_provider = fields.Selection( selection_add=[('bccr', 'Banco Central Costa Rica')] )

    def update_currency_rates(self):
           _logger.info('--> BCCR 1576089385')
           res = True
           all_good = True
           for company in self:
               if company.currency_provider == 'yahoo':
                  _logger.info("Call to the discontinued Yahoo currency rate web service.")
               elif company.currency_provider == 'ecb':
                   res = company._update_currency_ecb()
               elif company.currency_provider == 'fta':
                   res = company._update_currency_fta()
               elif company.currency_provider == 'banxico':
                   res = company._update_currency_banxico()
               elif company.currency_provider == 'bccr':
                   res = company._update_currency_bccr()
               if not res:
                   all_good = False
                   _logger.info(('Unable to connect to the online exchange rate platform %s. The web service may be temporary down.') % company.currency_provider)
               elif company.currency_provider:
                   company.last_currency_sync_date = fields.Date.today()
           return all_good


    def _update_currency_bccr(self, date=None):
        for company in self:

            token = company.token_bccr

            if not token:
                raise exceptions.ValidationError("BCCR Error: Token inválido")

            if date:
                date = datetime.strptime(date, "%Y-%m-%d")
            else:
                date = datetime.today()

            fecha_inicio = date.strftime("%Y/%m/%d")
            fecha_fin = fecha_inicio
            base_url = "https://apim.bccr.fi.cr/"
            endpoint = "SDDE/api/Bccr.GE.SDDE.Publico.Indicadores.API/cuadro/1/series"
            url = base_url + endpoint
            
            headers = {
                "Authorization": f"Bearer {token}",
                "User-Agent": "Mozilla/5.0"
            }
            
            params = {
                "fechaInicio": fecha_inicio,
                "fechaFin": fecha_fin,
                "idioma": "ES"
            }
            
            try:
                response = requests.get(url, headers=headers, params=params)
                _logger.info("\tBCCR Response status: %s", response.status_code)
                data = response.json()
    
                if not data.get("estado"):
                    raise exceptions.Warning(data.get("mensaje"))
    
                indicadores = data["datos"][0]["indicadores"]
    
                venta = None
    
                for ind in indicadores:
                    if ind["codigoIndicador"] == "318":
                        venta = ind["series"][0]["valorDatoPorPeriodo"]
    
                currency = company.env['res.currency'].search([('name','=','USD')], limit=1)
    
                rate_date = date.strftime("%Y-%m-%d")
    
                exists = company.env['res.currency.rate'].search([
                    ('currency_id','=',currency.id),
                    ('name','=',rate_date),
                    ('company_id','=',company.id)
                ])
    
                if exists:
                    _logger.info("\tRate already exists")
                else:
                    currency.write({
                        'rate_ids': [(0,0,{
                            'name': rate_date,
                            'inverse_company_rate': venta,
                            'currency_id': currency.id,
                            'company_id': company.id
                        })]
                    })
    
                return True
    
            except Exception as e:
                _logger.error("BCCR ERROR: %s", e)
                return False
