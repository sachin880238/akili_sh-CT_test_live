from lxml import etree as ElementTree

from odoo.http import Controller, route, request


class Board(Controller):

    @route('/board/add_to_dashboard/custom', type='json', auth='user')
    def add_to_dashboard_custom(self, action_id, context_to_save, domain, view_mode,menu_name, name=''):
        # Retrieve the 'My Dashboard' action from its xmlid
        action = request.env.ref('dashboard_custom.sale_dashboard_title_action')
        if action and action['res_model'] == 'dashboard.tile' and action['views'][0][1] == 'form' and action_id:
            # Maybe should check the content instead of model board.board ?
            view_id = action['views'][0][0]
            board = request.env['dashboard.tile'].fields_view_get(view_id, 'form')
            if board and 'arch' in board:
                xml = ElementTree.fromstring(board['arch'])
                column = xml.find('./board/column')
                if column is not None:
                    new_action = ElementTree.Element('action', {
                        'name': str(action_id),
                        'string': name,
                        'menu':menu_name,
                        'view_mode': view_mode,
                        'context': str(context_to_save),
                        'domain': str(domain)
                    })
                    column.insert(0, new_action)
                    arch = ElementTree.tostring(xml, encoding='unicode')
                    request.env['ir.ui.view.custom'].create({
                        'user_id': request.session.uid,
                        'ref_id': view_id,
                        'arch': arch
                    })
                    return True
        return False
