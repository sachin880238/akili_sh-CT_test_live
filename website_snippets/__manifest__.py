{
    'name': 'Website Snippets',
    'version': '14.0',
    'summary': 'Website Snippets',
    'category': 'Tools',
    'author': 'Akili Systems Pvt. Ltd.',
    'maintainer': 'Akili Systems Pvt. Ltd.',
    'website': 'www.akilisystems.in',
    'depends': ['base', 'website', 'web_editor', 'web', 'website_sale'],
    'data': [
        'view/snippets/snippet_templates.xml',
        'view/snippets/snippet_views.xml',
        # 'view/snippets/assets.xml',
    ],
    'demo': [
        'data/website_blog_demo.xml',
        # 'data/website_blog_data.xml',
    ],
    'liscence': 'AGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}
