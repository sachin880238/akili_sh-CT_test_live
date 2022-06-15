from odoo import api, fields, models

AVAILABLE_PRIORITIES = [
    (' ', 'Normal'),
    ('x', 'Low'),
    ('x x', 'High'),
    ('x x x', 'Very High'),
]
