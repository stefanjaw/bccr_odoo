# -*- coding: utf-8 -*-

from odoo import models, fields, exceptions

class CurrencyRate(models.Model):
    _inherit = "res.currency.rate"
    rate = fields.Float(string="Rate", digits=(18, 14))