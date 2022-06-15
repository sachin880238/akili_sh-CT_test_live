from odoo import fields, models, api, _
from datetime import date

from odoo.addons.base.models.res_users import GroupsView

from lxml import etree
from lxml.builder import E

from odoo.osv import expression
from odoo.tools import partition

#
# Functions for manipulating boolean and selection pseudo-fields
#
def name_boolean_group(id):
    return 'in_group_' + str(id)

def name_selection_groups(ids):
    return 'sel_groups_' + '_'.join(str(it) for it in ids)

def is_boolean_group(name):
    return name.startswith('in_group_')

def is_selection_groups(name):
    return name.startswith('sel_groups_')

def is_reified_group(name):
    return is_boolean_group(name) or is_selection_groups(name)


class Users(models.Model):
    _inherit = "res.users"

    team_ids = fields.One2many('crm.team', 'user_id', string="Teams", help="Teams related to particular user.")
    department_id = fields.Many2one('hr.department', 'Department')
    job_id = fields.Many2one('hr.job', 'Position')
    work_location = fields.Char('Location')
    state = fields.Selection(compute='_compute_state', search='_search_state', string='Status',
                 selection=[('new', 'DRAFT'), ('active', 'ACTIVE'), ('inactive', 'INACTIVE')], default="new")
    add_date_created = fields.Date(string="Created", default=date.today())
    add_last_used_date  = fields.Date(string='Last Used', default=date.today())
    street3 = fields.Char()
    parent_state = fields.Selection([
        ('green', 'GREEN'),
        ('yellow', 'YELLOW'),
        ('red', 'RED'),
        ('black', 'BLACK')], default='black')
    
    status = fields.Char(compute="get_user_state_color",string="Status", help="Use for status color in tree view as well as in dashboard tile.")

    @api.onchange('phone')
    def onchange_primary_tel_type(self):
        comm_obj = self.env['communication.type'].search([('for_phone', '=', True)], limit=1)
        self.primary_tel_type = comm_obj.id

    @api.depends('parent_state')
    def get_user_state_color(self):
        for rec in self:
            if rec.parent_state == "green":
                rec.status = "#006400"
            elif rec.parent_state == "yellow":
                rec.status = "#FFD700"
            elif rec.parent_state == "red":
                rec.status = "#FF0000"
            else:
                rec.status = "#000000"

    def _search_state(self, operator, value):
        negative = operator in expression.NEGATIVE_TERM_OPERATORS

        # In case we have no value
        if not value:
            return expression.TRUE_DOMAIN if negative else expression.FALSE_DOMAIN

        if operator in ['in', 'not in']:
            if len(value) > 1:
                return expression.FALSE_DOMAIN if negative else expression.TRUE_DOMAIN
            if value[0] == 'new':
                comp = '!=' if negative else '='
            if value[0] == 'active':
                comp = '=' if negative else '!='
            return [('log_ids', comp, False)]

        if operator in ['=', '!=']:
            # In case we search against anything else than new, we have to invert the operator
            if value != 'new':
                operator = expression.TERM_OPERATORS_NEGATION[operator]

            return [('log_ids', operator, False)]

        return expression.TRUE_DOMAIN

    @api.multi
    def _compute_state(self):
        for user in self:
            user.state = 'active' if user.login_date else 'new'

    def _get_default_permissions(self):
        default_groups = super(Users, self).default_get(['groups_id'])
        group_ids = default_groups["groups_id"][0][2]
        perm_list = []
        group_list = []
        gr_ids = []
        for gr_id in group_ids:
            group = self.env['res.groups'].search([('id', '=', gr_id), ('category_id.name', 'not in', ['Technical Settings', 'Extra Rights'])])
            if group:
                group_list.append(group)
                gr_ids.append(gr_id)

        for gr_id in gr_ids:
            group = self.env['res.groups'].search([('id', '=', gr_id), ('category_id.name', 'not in', ['Technical Settings', 'Extra Rights'])])
            if group:
                for grp in group_list:
                    if grp != group:
                        if group in grp.implied_ids:
                            group = False
                            break
            if group:
                permission_vals = {'application_id': group.category_id.id}
                group_obj = self.env['group.permission'].create(permission_vals)
                perm_list.append(group_obj.id)
        permissions = [(6, 0, perm_list)]
        return permissions

    permission_ids = fields.One2many('group.permission', 'permission_id', string='Permissions', default=_get_default_permissions)

    @api.model
    def create(self, vals):
        if vals.get('permission_ids'):
            permissions_list = [perm[1:] for perm in vals['permission_ids'] if perm[2]]
            for perm in permissions_list:
                permission = self.env['group.permission'].search([('id', '=', perm[0])])
                groups = self.env['res.groups'].search([('category_id', '=', permission.application_id.id)])
                groups = sorted([group.id for group in groups])
                field_name = "sel_groups"
                for group in groups:
                    field_name+="_" + str(group)
                vals[field_name] = perm[1]['position_id']
        res = super(Users, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        if vals.get('permission_ids'):
            permissions_list = [perm[1:] for perm in vals['permission_ids'] if perm[2]]
            for perm in permissions_list:
                permission = self.env['group.permission'].search([('id', '=', perm[0])])
                groups = self.env['res.groups'].search([('category_id', '=', permission.application_id.id)])
                groups = sorted([group.id for group in groups])
                field_name = "sel_groups"
                for group in groups:
                    field_name+="_" + str(group)
                vals[field_name] = perm[1]['position_id']
        res = super(Users, self).write(vals)
        return res

class GroupPermission(models.Model):
    _name = "group.permission"
    _description = "Group Permissions"

    application_id = fields.Many2one('ir.module.category', string='Application' )
    position_id = fields.Many2one('res.groups', string='Position')
    permission_id = fields.Many2one('res.users', string='permission_id')

class res_groups_mail_channel(models.Model):
    """ Update of res.groups class
        - if adding users from a group, check mail.channels linked to this user
          group and subscribe them. This is done by overriding the write method.
    """
    _inherit = 'res.groups'
    _description = 'Access Groups'

    state  = fields.Selection([
        ('draft','DRAFT'),
        ('active','ACTIVE'),
        ('inactive','INACTIVE')], default='active')

    @api.multi
    def inactive_group(self):
        self.write({'state': 'inactive'})
        return True

    @api.multi
    def reset_to_draft_group(self):
        self.write({'state': 'draft'})
        return True

    @api.multi
    def active_group(self):
        self.write({'state': 'active'})
        return True



class Child_defaults(models.Model):
    _inherit = 'res.users'

    @api.model
    def default_get(self, fields):
        group_fields, fields = partition(is_reified_group, fields)
        fields1 = (fields) if group_fields else fields
        values = super(Child_defaults, self).default_get(fields1)
        self._add_reified_groups(group_fields, values)
        return values

class Child(GroupsView):

    @api.model
    def _update_user_groups_view(self):
        """ Modify the view with xmlid ``base.user_groups_view``, which inherits
            the user form view, and introduces the reified group fields.
        """
        # remove the language to avoid translations, it will be handled at the view level
        self = self.with_context(lang=None)

        # We have to try-catch this, because at first init the view does not
        # exist but we are already creating some basic groups.
        view = self.env.ref('base.user_groups_view', raise_if_not_found=False)
        if view and view.exists() and view._name == 'ir.ui.view':
            group_no_one = view.env.ref('base.group_no_one')
            group_employee = view.env.ref('base.group_user')
            xml1, xml2, xml3 = [], [], []
            xml1.append(E.separator(string='User Type', colspan="2", groups='base.group_no_one'))
            xml2.append(E.separator(string='Application Accesses', colspan="2"))

            user_type_field_name = ''
            user_type_readonly = str({})
            sorted_triples = sorted(self.get_groups_by_application(),
                                    key=lambda t: t[0].xml_id != 'base.module_category_user_type')
            for app, kind, gs in sorted_triples:  # we process the user type first
                attrs = {}
                # hide groups in categories 'Hidden' and 'Extra' (except for group_no_one)
                if app.xml_id in ('base.module_category_hidden', 'base.module_category_extra', 'base.module_category_usability'):
                    attrs['groups'] = 'base.group_no_one'

                # User type (employee, portal or public) is a separated group. This is the only 'selection'
                # group of res.groups without implied groups (with each other).
                if app.xml_id == 'base.module_category_user_type':
                    # application name with a selection field
                    field_name = name_selection_groups(gs.ids)
                    user_type_field_name = field_name
                    user_type_readonly = str({'readonly': [(user_type_field_name, '!=', group_employee.id)]})
                    attrs['widget'] = 'radio'
                    attrs['groups'] = 'base.group_no_one'
                    xml1.append(E.field(name=field_name, **attrs))
                    xml1.append(E.newline())

                elif kind == 'selection':
                    # application name with a selection field
                    field_name = name_selection_groups(gs.ids)
                    attrs['attrs'] = user_type_readonly
                    xml2.append(E.field(name=field_name, **attrs))
                    xml2.append(E.newline())
                else:
                    # application separator with boolean fields
                    app_name = app.name or 'Other'
                    xml3.append(E.separator(string=app_name, colspan="4", **attrs))
                    attrs['attrs'] = user_type_readonly
                    for g in gs:
                        field_name = name_boolean_group(g.id)
                        if g == group_no_one:
                            # make the group_no_one invisible in the form view
                            xml3.append(E.field(name=field_name, invisible="1", **attrs))
                        else:
                            xml3.append(E.field(name=field_name, **attrs))

            xml3.append({'class': "o_label_nowrap"})
            if user_type_field_name:
                user_type_attrs = {'invisible': [(user_type_field_name, '!=', group_employee.id)]}
                invisible_application = 1
            else:
                user_type_attrs = {}

            xml = E.field(
                E.group(*(xml1), col="2"),
                E.group(*(xml2), col="2", attrs=str(user_type_attrs)),
                E.group(*(xml2), col="2", invisible=str(invisible_application)),
                E.group(*(xml3), col="4", attrs=str(user_type_attrs)), name="groups_id", position="replace")
            xml.addprevious(etree.Comment("GENERATED AUTOMATICALLY BY GROUPS"))
            xml_content = etree.tostring(xml, pretty_print=True, encoding="unicode")

            new_context = dict(view._context)
            new_context.pop('install_filename', None)  # don't set arch_fs for this computed view
            new_context['lang'] = None
            view.with_context(new_context).write({'arch': xml_content})
