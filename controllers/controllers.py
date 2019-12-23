# -*- coding: utf-8 -*-
from odoo import http

# class BccrOdoo12/(http.Controller):
#     @http.route('/bccr_odoo12//bccr_odoo12//', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bccr_odoo12//bccr_odoo12//objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('bccr_odoo12/.listing', {
#             'root': '/bccr_odoo12//bccr_odoo12/',
#             'objects': http.request.env['bccr_odoo12/.bccr_odoo12/'].search([]),
#         })

#     @http.route('/bccr_odoo12//bccr_odoo12//objects/<model("bccr_odoo12/.bccr_odoo12/"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bccr_odoo12/.object', {
#             'object': obj
#         })