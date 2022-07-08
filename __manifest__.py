# -*- coding: utf-8 -*-
{
    'name': "Módulo para tipo de cambio del BCCR",

    'summary': """
        Módulo para obtener el tipo de cambio del
        Banco Central de Costa Rica""",

    'description': """
        Módulo para obtener el tipo de cambio del
        Banco Central de Costa Rica
    """,

    'author': "Avalantec",
    'website': "https://www.avalantec.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','currency_rate_live'],

    # always loaded
    'data': [
        'views/res_company.xml',
        # 'security/ir.model.access.csv',
        #'views/views.xml',
        
    ],
    # only loaded in demonstration mode
    #'demo': [
    #    'demo/demo.xml',
    #],
}
