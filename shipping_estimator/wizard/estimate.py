from odoo import api, fields, models, _
from odoo.exceptions import UserError


class EstimateShipping(models.TransientModel):
    _name = "shipping.estimate.wizard"
    _description = "Shipping Estimate Wizard"

    estimate_line = fields.One2many('shipping.estimate.line', string='Estimation Line', store=False)
    ship = fields.Float('Shipping')
    pack = fields.Float('Packaging')
    markup = fields.Float('Markup')
    calculate = fields.Float('Calculated')
    estimate = fields.Float('Estimate')

    def calculate_shipment_bare(self, product_id=False,ship_id=False,order_id=False,  quantity=0):

        dim_weight_factor = self.env['ir.config_parameter'].search([('key', '=', 'shipping_estimator.dim_weight_factor')])
        dim_weight = (product_id.dim1 * product_id.dim2 * product_id.dim3) / 1
        if ship_id:
            for _ in range(int(round(quantity))):
                rec = self._context['o2m_selection']
                pre_ship = self.env['pre.shipment'].search([('id', '=', rec['pre_shipment_lines']['ids'][0])])
                virtual_packages = self.env['virtual.package'].search([])
                vals = {
                    'name': 'VP' + str(len(virtual_packages)),
                    'order_id': order_id.id,
                    'contents': product_id.default_code,
                    'dim1': int(round(product_id.dim1)),
                    'dim2': int(round(product_id.dim2)),
                    'dim3': int(round(product_id.dim3)),
                    'weight': int(round(product_id.weight)),
                    'dim_weight': dim_weight,
                    'billing_weight': max(product_id.weight, dim_weight),
                    'container_id': False,
                    'container_name': '',
                    'surcharge': product_id.product_surcharge,
                }
                virtual_package = self.env['virtual.package'].create(vals)

            

        elif order_id:
            for _ in range(int(round(quantity))):
                virtual_packages = self.env['virtual.package'].search([])
                vals = {
                    'order_id': order_id.id,
                    'name': 'VP' + str(len(virtual_packages)),
                    'contents': product_id.default_code,
                    'dim1': int(round(product_id.dim1)),
                    'dim2': int(round(product_id.dim2)),
                    'dim3': int(round(product_id.dim3)),
                    'weight': int(round(product_id.weight)),
                    'dim_weight': dim_weight,
                    'billing_weight': max(product_id.weight, dim_weight),
                    'container_id': False,
                    'container_name': '',
                    'surcharge': product_id.product_surcharge,
                }

    def calculate_shipment_alone(self, product_id=False, ship_id=False, order_id=False, quantity=0):
        dim_weight_factor = self.env['ir.config_parameter'].search([('key', '=', 'shipping_estimator.dim_weight_factor')])
        dim_weight = (product_id.dim1 * product_id.dim2 * product_id.dim3) / int(dim_weight_factor.value)
        if ship_id:
            for _ in range(int(round(quantity))):
                rec = self._context['o2m_selection']

                pre_ship = self.env['pre.shipment'].search([('id', '=', rec['pre_shipment_lines']['ids'][0])])
                virtual_packages = self.env['virtual.package'].search([])
                vals = {
                    'name': 'VP' + str(len(virtual_packages)),
                    'order_id': order_id.id,
                    'contents': product_id.default_code,
                    'dim1': int(round(product_id.dim1)),
                    'dim2': int(round(product_id.dim2)),
                    'dim3': int(round(product_id.dim3)),
                    'weight': int(round(product_id.weight)),
                    'dim_weight': dim_weight,
                    'billing_weight': max(product_id.weight, dim_weight),
                    'container_id': False,
                    'container_name': '',
                    'surcharge': product_id.product_surcharge,
                }
                virtual_package = self.env['virtual.package'].create(vals)

       

    def calculate_shipment_flowable(self, product_id):
        flowable_packing_factor = self.env['ir.config_parameter'].search([('key', '=', 'shipping_estimator.flowable_packing_factor')])
        if ship_id:
            for _ in range(int(round(quantity))):
                rec = self._context['o2m_selection']
                pre_ship = self.env['pre.shipment'].search([('id',  '=', rec['pre_shipment_lines']['ids'][0])])
                virtual_packages = self.env['virtual.package'].search([])
                vals = {
                    
                    'cumulative_volume': 0.0 + (pre_ship.product_uom_qty * product_id.volume * float(flowable_packing_factor.value)),
                    'cumulative_weight': 0.0 + (pre_ship.product_uom_qty * product_id.weight),
                    'cumulatie_surcharge': 0.0 + (pre_ship.product_uom_qty * product_id.product_surcharge) + product_id.product_orderline_surcharge}
                return vals

    def calculate_shipment_flexible(self, product_id=False,ship_id=False,order_id=False,  quantity=0):
        flexible_packing_factor = self.env['ir.config_parameter'].search([('key', '=', 'shipping_estimator.flexible_packing_factor')])
        if ship_id:
            for _ in range(int(round(quantity))):
                rec = self._context['o2m_selection']
                pre_ship = self.env['pre.shipment'].search([('id',  '=', rec['pre_shipment_lines']['ids'][0])])
                virtual_packages = self.env['virtual.package'].search([])
                vals = {
                    
                    'cumulative_volume': 0.0 + (pre_ship.ship_lines.product_uom_qty * product_id.volume * float(flexible_packing_factor.value)),
                    'cumulative_weight': 0.0 + (pre_ship.ship_lines.product_uom_qty * product_id.weight),
                    'cumulatie_surcharge': 0.0 + (pre_ship.ship_lines.product_uom_qty * product_id.product_surcharge) + product_id.line_surcharge
                }
                return vals
    def calculate_shipment_rigid(self, product_id):
        rigid_packing_factor = self.env['ir.config_parameter'].search([('key', '=', 'shipping_estimator.rigid_packing_factor')])
        if ship_id:
            for _ in range(int(round(quantity))):
                rec = self._context['o2m_selection']
                pre_ship = self.env['pre.shipment'].search([('id',  '=', rec['pre_shipment_lines']['ids'][0])])
                virtual_packages = self.env['virtual.package'].search([])
                vals = {
                    'cumulative_volume': 0.0 + (pre_ship.product_uom_qty * product_id.volume * float(rigid_packing_factor.value)),
                    'cumulative_weight': 0.0 + (pre_ship.product_uom_qty * product_id.weight),
                    'cumulatie_surcharge': 0.0 + (pre_ship.product_uom_qty * product_id.product_surcharge) + product_id.product_orderline_surcharge}
                return vals

    def calculate_shipment_enclosed(self, product_id, ship_id=False, order_id=False, quantity=0):
        boxed_packing_factor = self.env['ir.config_parameter'].search([('key', '=', 'shipping_estimator.boxed_packing_factor')])
        if ship_id:
            for _ in range(int(round(quantity))):
                rec = self._context['o2m_selection']
                pre_ship = self.env['pre.shipment'].search([('id',  '=', rec['pre_shipment_lines']['ids'][0])])
                virtual_packages = self.env['virtual.package'].search([])
                vals = {
                    'order_id': order_id.id,
                    'name': 'VP' + str(len(virtual_packages)),
                    'cumulative_volume': 0.0 + (pre_ship.ship_lines.product_uom_qty * product_id.volume * float(boxed_packing_factor.value)),
                    'cumulative_weight': 0.0 + (pre_ship.ship_lines.product_uom_qty * product_id.weight),
                    'cumulatie_surcharge': 0.0 + (pre_ship.ship_lines.product_uom_qty * product_id.product_surcharge) + product_id.product_orderline_surcharge}
                return vals

    def create_long_virtual_package(self, order_id, container, long_container_count, cumulative_long_weight, dim1, dim2, dim3, cumulative_long_surcharge):
        dim_weight_factor = self.env['ir.config_parameter'].search([('key', '=', 'shipping_estimator.dim_weight_factor')])
        dim_weight = (dim1 * dim2 * dim3 / int(dim_weight_factor.value))
        for _ in range(long_container_count):
            virtual_packages = self.env['virtual.package'].search([])
            vals = {
                'order_id': order_id.id,
                'name': 'VP' + str(len(virtual_packages)),
                'contents': "assorted long items",
                'dim1': int(round(container.dim1)),
                'dim2': int(round(container.dim2)),
                'dim3': int(round(container.dim3)),
                'weight': int(round((cumulative_long_weight / long_container_count) + container.weight)),
                'billing_weight': max(int(round((long_container_count * container.weight) + container.weight)), dim_weight),
                'container_id': container.id,
                'container_name': container.name,
                'surcharge': (cumulative_long_surcharge / long_container_count) + container.surcharge,
            }
            virtual_package = self.env['virtual.package'].create(vals)
        for line in order_id.vir_pkg_ids:
            # pckg_lst = []
            
            line.write({'vir_pkg_ids':[(0,0,vals)]})



    def create_remaining_virtual_package(self, order_id, sufficient, package_count, container, cumulative_weight, dim1, dim2, dim3, cumulative_surcharge):
        dim_weight_factor = self.env['ir.config_parameter'].search([('key', '=', 'shipping_estimator.dim_weight_factor')])
        dim_weight = (dim1 * dim2 * dim3 / int(dim_weight_factor.value))
        if sufficient:
            virtual_packages = self.env['virtual.package'].search([])
            vals = {
                'order_id': order_id.id,
                'name': 'VP' + str(len(virtual_packages)),
                'contents': "assorted items",
                'dim1': int(round(container.dim1)),
                'dim2': int(round(container.dim2)),
                'dim3': int(round(container.dim3)),
                'weight': int(round(cumulative_weight + container.weight)),
                'billing_weight': max(int(round((package_count * container.weight) + container.weight)), dim_weight),
                'container_id': container.id,
                'container_name': container.name,
                'surcharge': cumulative_surcharge + container.surcharge,
            }
            virtual_package = self.env['virtual.package'].create(vals)
        else:
            for _ in range(package_count):
                virtual_packages = self.env['virtual.package'].search([])
                vals = {
                    'order_id': order_id.id,
                    'name': 'VP' + str(len(virtual_packages)),
                    'contents': "assorted items",
                    'dim1': int(round(container.dim1)),
                    'dim2': int(round(container.dim2)),
                    'dim3': int(round(container.dim3)),
                    'weight': int(round((cumulative_weight / package_count) + container.weight)),
                    'billing_weight': max(int(round((package_count * container.weight) + container.weight)), dim_weight),
                    'container_id': container.id,
                    'container_name': container.name,
                    'surcharge': (cumulative_surcharge / package_count) + container.surcharge,
                }
                virtual_package = self.env['virtual.package'].create(vals)

    def calculate_shipment(self):
        if not self._context.get('o2m_selection'):
            raise UserError(_('Please Select at least One Order Lines to Perform this Action!!!')) 

        rec = self._context.get('o2m_selection')
        
        quotation = self._context.get('active_id')
        cumulative_volume = 0
        cumulative_weight = 0
        cumulative_surcharge = 0
        maximum_dim = 0
        max_dim = 0
        cumulative_long_section = 0
        cumulative_long_weight = 0
        cumulative_long_surcharge = 0
        maximum_long_dim = 0
        long_container_count = 0
        package_count = 0
        dim1 = 0
        dim2 = 0
        dim3 = 0
        boxed_packing_factor = self.env['ir.config_parameter'].search([('key', '=', 'shipping_estimator.boxed_packing_factor')])
        long_packing_factor = self.env['ir.config_parameter'].search([('key', '=', 'shipping_estimator.long_packing_factor')])
        flexible_packing_factor = self.env['ir.config_parameter'].search([('key', '=', 'shipping_estimator.flexible_packing_factor')])
        flowable_packing_factor = self.env['ir.config_parameter'].search([('key', '=', 'shipping_estimator.flowable_packing_factor')])
        rigid_packing_factor = self.env['ir.config_parameter'].search([('key', '=', 'shipping_estimator.rigid_packing_factor')])
        maximum_clearance = self.env['ir.config_parameter'].search([('key', '=', 'shipping_estimator.maximum_clearance')])
        minimum_clearance = self.env['ir.config_parameter'].search([('key', '=', 'shipping_estimator.minimum_clearance')])

        if rec:
            is_shipment = True
            order_id = self.env['sale.order'].search([('id', '=', quotation)])

            ship_id = self.env['pre.shipment'].search([('id', '=', rec['pre_shipment_lines']['ids'][0])])
            virtual_packages = self.env['virtual.package'].search([])
            for value in ship_id.ship_lines:
                # if value.product_id.packing_category == 'bare':
                #     self.calculate_shipment_bare(value.product_id,ship_id, order_id, value.product_uom_qty)
                # if value.product_id.packing_category == 'alone':
                #     self.calculate_shipment_alone(value.product_id,ship_id, order_id, value.product_uom_qty)
                # if value.product_id.packing_category == 'flowable':
                #     self.calculate_shipment_flowable(value.product_id,order_id)
                # if value.product_id.packing_category == 'flexible':
                #     self.calculate_shipment_flexible(value.product_id,order_id)
                # if value.product_id.packing_category == 'rigid':
                #     self.calculate_shipment_rigid(value.product_id)
                # if value.product_id.packing_category == 'enclosed':
                #     self.calculate_shipment_enclosed(value.product_id)
                if value.product_id.packing_category == 'bare':
                    self.calculate_shipment_bare(value.product_id, ship_id, order_id, value.product_uom_qty)

                if value.product_id.packing_category == 'alone':
                    self.calculate_shipment_alone(value.product_id, ship_id, order_id, value.product_uom_qty)

                elif value.product_id.packing_category == 'flowable':
                    cumulative_volume = cumulative_volume + (value.product_uom_qty * value.product_id.volume * float(flowable_packing_factor.value))
                    cumulative_weight = cumulative_weight + (value.product_uom_qty * value.product_id.weight)
                    cumulative_surcharge = cumulative_surcharge + (value.product_uom_qty * value.product_id.product_surcharge) + value.product_id.line_surcharge
                    # self.calculate_shipment_flowable(value.product_id, ship_id, order_id, value.product_uom_qty)

                elif value.product_id.packing_category == 'flexible':
                    cumulative_volume = cumulative_volume + (value.product_uom_qty * value.product_id.volume * float(flexible_packing_factor.value))
                    cumulative_weight = cumulative_weight + (value.product_uom_qty * value.product_id.weight)
                    cumulative_surcharge = cumulative_surcharge + (value.product_uom_qty * value.product_id.product_surcharge) + value.product_id.line_surcharge
                    # self.calculate_shipment_flexible(value.product_id,ship_id,order_id,value.product_uom_qty)

                elif value.product_id.packing_category == 'rigid':
                    max_dim = max(value.product_id.dim1, value.product_id.dim2, value.product_id.dim3)
                    if max_dim > maximum_dim:
                        maximum_dim = max_dim
                    cumulative_volume = cumulative_volume + (value.product_uom_qty * value.product_id.volume * float(rigid_packing_factor.value))
                    cumulative_weight = cumulative_weight + (value.product_uom_qty * value.product_id.weight)
                    cumulative_surcharge = cumulative_surcharge + (value.product_uom_qty * value.product_id.product_surcharge) + value.product_id.line_surcharge
                    # self.calculate_shipment_rigid(value.product_id, ship_id, order_id, value.product_uom_qty)

                elif value.product_id.packing_category == 'enclosed':
                    max_dim = max(value.product_id.dim1, value.product_id.dim2, value.product_id.dim3)
                    if max_dim > maximum_dim:
                        maximum_dim = max_dim
                    cumulative_volume = cumulative_volume + (value.product_uom_qty * value.product_id.volume * float(boxed_packing_factor.value))
                    cumulative_weight = cumulative_weight + (value.product_uom_qty * value.product_id.weight)
                    cumulative_surcharge = cumulative_surcharge + (value.product_uom_qty * value.product_id.product_surcharge) + value.product_id.line_surcharge
                    # self.calculate_shipment_enclosed(value.product_id, ship_id, order_id, value.product_uom_qty)

                elif value.product_id.packing_category in ['nestable', 'rollable']:
                    dim1 = value.product_id.dim1
                    dim2 = value.product_id.dim2
                    dim3 = value.product_id.dim3 + ((value.product_uom_qty - 1) * value.product_id.dim3_increment)
                    max_dim = max(dim1, dim2, dim3)
                    if max_dim > maximum_dim:
                        maximum_dim = max_dim
                    cumulative_volume = cumulative_volume + (dim1 * dim2 * dim3 * float(rigid_packing_factor.value))
                    cumulative_weight = cumulative_weight + (value.product_uom_qty * value.product_id.weight)
                    cumulative_surcharge = cumulative_surcharge + (value.product_uom_qty * value.product_id.product_surcharge) + value.product_id.line_surcharge
                    # self.calculate_shipment_nest_roll(value.product_id, ship_id, order_id, value.product_uom_qty)

                elif value.product_id.packing_category == 'long':
                    max_dim = max(value.product_id.dim1, value.product_id.dim2, value.product_id.dim3)
                    if max_dim > maximum_long_dim:
                        maximum_long_dim = max_dim
                    cumulative_long_section = cumulative_long_section + (value.product_uom_qty * value.product_id.cross_section * float(long_packing_factor.value))
                    cumulative_long_weight = cumulative_long_weight + (value.product_uom_qty * value.product_id.weight)
                    cumulative_long_surcharge = cumulative_long_surcharge + (value.product_uom_qty * value.product_id.product_surcharge) + value.product_id.line_surcharge
                #     self.calculate_shipment_long(value.product_id, False, order_id, value.product_uom_qty)

            if any([cumulative_long_section, cumulative_long_weight, long_container_count, cumulative_long_surcharge]):
                all_containers = self.env['product.product'].search([('product_type', '=', 'container'), ('cross_section', '>', 0)])
                min_long_clearance = maximum_long_dim + int(minimum_clearance.value)
                max_long_clearance = maximum_long_dim + int(maximum_clearance.value)
                selected_containers = []

                for container in all_containers:
                    if min_long_clearance <= max(container.dim1, container.dim2, container.dim3) <= max_long_clearance:
                        selected_containers.append(container)

                final_containers = {container: container.cross_section for container in selected_containers if container.cross_section > cumulative_long_section}

                if final_containers:
                    min_cross = min(final_containers.values())
                    final_container = set([key for key in final_containers if final_containers[key] == min_cross])
                    self.create_long_virtual_package(order_id, final_container, long_container_count, cumulative_long_weight, dim1, dim2, dim3, cumulative_long_surcharge)

                else:
                    long_container_count = 2
                    cumulative_long_section = cumulative_long_section / long_container_count
                    while True:
                        final_containers = {container: container.cross_section for container in selected_containers if container.cross_section > cumulative_long_section}

                        if final_containers:
                            min_cross = min(final_containers.values())
                            final_container = set([key for key in final_containers if final_containers[key] == min_cross])
                            self.create_long_virtual_package(final_container, long_container_count, cumulative_long_weight, dim1, dim2, dim3, long_packing_factor)
                            break
                        else:
                            long_container_count += 1
                            cumulative_long_section /= long_container_count
                            break
            if any([cumulative_volume, package_count, cumulative_weight, cumulative_surcharge]):
                all_containers = self.env['product.product'].search([('product_type', '=', 'container'), ('cross_section', '=', 0)])
                selected_containers = []
                
                for container in all_containers:
                    if any([container.dim1 > maximum_dim, container.dim2 > maximum_dim, container.dim2 > maximum_dim]):
                        selected_containers.append(container)

                final_containers = {container: container.volume for container in selected_containers if container.volume > cumulative_volume}
                if final_containers:
                    min_cross = min(final_containers.values())
                    final_container = set([key for key in final_containers if final_containers[key] == min_cross])
                    self.create_remaining_virtual_package(order_id, True, package_count, final_container, cumulative_weight, dim1, dim2, dim3, cumulative_surcharge)
                else:
                    package_count += 1
                    cumulative_volume /= package_count
                    while True:
                        final_containers = {container: container.volume for container in selected_containers if container.volume > cumulative_volume}

                        if final_containers:
                            min_cross = min(final_containers.values())
                            final_container = set([key for key in final_containers if final_containers[key] == min_cross])
                            self.create_remaining_virtual_package(order_id, False, package_count, final_container, cumulative_weight, dim1, dim2, dim3, cumulative_surcharge)
                            break
                        else:
                            package_count += 1
                            cumulative_volume /= package_count
                            break
                        
    @api.multi
    def update_lines(self):
        sale_line_ids = self.env['sale.order.line'].search([('id', 'in', self._context['selected_rec'])])

class EstimateShippingLine(models.TransientModel):
    _name = "shipping.estimate.line"
    _description = "Shipping Estimate line"

    wizard_id = fields.Many2one('shipping.estimate.wizard', string='Wizard')
    carrier = fields.Many2one('delivery.carrier', string="Carrier")
    cost = fields.Float('Cost')




class SaleOrderInheritClass(models.Model):
    _inherit = "sale.order"

    
    def shipping_estimated_wizard(self):
        self.ensure_one()
        context = self._context
        selection = context['o2m_selection']
        if not selection:
            raise UserError(_('Please Select One Order Lines to Perform this Action!!!'))
        elif len(selection['pre_shipment_lines']['ids']) > 1:
            raise UserError(_('Please Select Only One Order Lines to Perform this Action!!!')) 
        wizard_form = self.env.ref('shipping_estimator.estimate_shipping_wizard_view')
        return {
            'name' : _('Add Shipping'),
            'type' : 'ir.actions.act_window',
            'res_model' : 'shipping.estimate.wizard',
            'view_id' : wizard_form.id,
            'view_type' : 'form',
            'view_mode' : 'form',
            'target': 'new',
            'context': {'default_sale_id':self.id}
        }
