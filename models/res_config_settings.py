# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    bccr_email = fields.Char(related="company_id.bccr_email", readonly=False)
    bccr_token = fields.Char(related="company_id.bccr_token", readonly=False)

