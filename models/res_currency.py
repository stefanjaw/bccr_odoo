# -*- coding: utf-8 -*-

from odoo import models, fields, exceptions

class Currency(models.Model):
    _inherit = "res.currency"
    rate = fields.Float(string="Rate", digits=(18, 14))