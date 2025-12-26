# -*- coding: utf-8 -*-

from odoo import models, fields, exceptions

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"
    email_bccr = fields.Char(string="email_bccr",related="company_id.email_bccr",readonly=False)
    token_bccr = fields.Char(string="token_bccr",related="company_id.token_bccr",readonly=False)
    last_currency_sync_date = fields.Date(related="company_id.last_currency_sync_date", readonly=True)