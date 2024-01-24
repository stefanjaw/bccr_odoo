# -*- coding: utf-8 -*-
{
    'name': "bccr_odoo",

    'summary': """
        Modulo para Tipo de Cambio en Costa Rica, para Odoo V16.
        """,

    'description': """
        Modulo para Tipo de Cambio en Costa Rica, para Odoo V16.
        1573844490
    """,

    'author': "Avalantec",
    'website': "http://www.avalantec.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.2.17',

    # any module necessary for this one to work correctly
    'depends': ['base','currency_rate_live'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
