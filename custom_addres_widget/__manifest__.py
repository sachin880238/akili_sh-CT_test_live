{
    'name': 'custom address widget',
    'summary': '',
    'version': '1.0',
    'description': """ Sale order & purchase order address icons""",
    'company': "Akili Systems Pvt. Ltd.",
    'author': "Akili Systems Pvt. Ltd.",
    'website': "http://www.akilisystems.in/",
    'license': 'AGPL-3',
    'category': 'Uncategorized',
    'depends': [
        'base', 'base_setup', 'bus', 'web_tour','sale'],
    'external_dependencies': {
        'python': [
        ],
    },
    'data': [
        'views/templates.xml',],
    'qweb': [
	'static/src/xml/custom.xml',],

    'installable': True,
    'application': True,
    'auto_install': False,
}