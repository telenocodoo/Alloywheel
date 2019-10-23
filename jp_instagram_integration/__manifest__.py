# -*- coding: utf-8 -*-
{
    'name': "Instagram Integration",

    'summary': """
        Instagram integration with user profile""",

    'description': """
        With this module you can get instagram user account 
        full name, profile picture, biography, external URL
        followers count, media count and engagement rate.
    """,

    'author': "Ing. Jean Paul Casis",
    'website': "http://soft.pvodoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'User types',
    'version': '12.1.0.0.0',
    'license': 'LGPL-3',
    'images': ['static/description/banner.png'],
    'depends': ['base'],

    'data': [
        'views/views.xml',
    ],
}