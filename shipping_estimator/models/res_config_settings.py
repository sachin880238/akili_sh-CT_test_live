from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    minimum_clearance = fields.Integer(
        string='Minimum Clearance', config_parameter='shipping_estimator.minimum_clearance', help="minimum inches clearance between products and end of container", default=0)

    maximum_clearance = fields.Integer(
        string='Maximum Clearance', config_parameter='shipping_estimator.maximum_clearance', help="maximum inches clearance between products and end of container", default=0)

    long_packing_factor = fields.Float(
        string='Long Packing Factor', config_parameter='shipping_estimator.long_packing_factor', help="multiply actual cross section by factor to get required cross section", default=0.0)

    flowable_packing_factor = fields.Float(
        string='Flowable Packing Factor', config_parameter='shipping_estimator.flowable_packing_factor', help="multiply actual volume by factor to get required volume", default=0.0)

    flexible_packing_factor = fields.Float(
        string='Flexible Packing Factor', config_parameter='shipping_estimator.flexible_packing_factor', help="multiply actual volume by factor to get required volume", default=0.0)

    rigid_packing_factor = fields.Float(
        string='Rigid Packing Factor', config_parameter='shipping_estimator.rigid_packing_factor', help="multiply actual volume by factor to get required volume", default=0.0)

    boxed_packing_factor = fields.Float(
        string='Boxed Packing Factor', config_parameter='shipping_estimator.boxed_packing_factor', help="multiply actual volume by factor to get required volume", default=0.0)

    shipping_cost_multiplier = fields.Float(
        string='Shipping Cost Multiplier', config_parameter='shipping_estimator.shipping_cost_multiplier', help="safety markup applied to estimated total shipping cost", default=0.0)

    minimum_shipping_charge = fields.Float(
        string='Minimum Shipping Charge', config_parameter='shipping_estimator.minimum_shipping_charge', help="minimum for shipment, not each package", default=0.0)

    insurance_multiplier = fields.Float(
        string='Insurance Multiplier', config_parameter='shipping_estimator.insurance_multiplier', help="multiply order total by this to get self-insured cost", default=0.0)

    dim_weight_factor = fields.Integer(
        string='Dim Weight Divider', config_parameter='shipping_estimator.dim_weight_factor', help="divide Container exterior volume by this to get dimensional weight", default=1)
