import base64
import csv
from datetime import datetime
import dateutil.parser
import io
from io import BytesIO
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo_csv_tools.lib import mapper
from odoo_csv_tools.lib.transform import Processor
import openpyxl
import subprocess


class ImportData(models.TransientModel):
    _name = "import.data"
    _description = 'Import Account Data'

    upload_file = fields.Binary("File")
    core = fields.Integer('Core', help='cores your cpu has?', default=4, required=True)
    size = fields.Integer('Size', help='Records per worker', default=100, required=True)
    workers = fields.Integer('Total Workers', compute='_get_total_workers', store=True)
    filename = fields.Char('File Name')

    @api.depends('core')
    def _get_total_workers(self):
        for record in self:
            record.workers = (record.core * 2) * 80 // 100

    def get_file_type(self):
        extension = self.filename.split('.')
        if extension and extension[-1] not in ['xlsx', 'xls', 'csv']:
            raise UserError(_("Error!, You can only upload csv or xlsx file format."))
        return extension[-1]

    def read_file(self):
        val = base64.decodestring(self.upload_file)
        tempfile = BytesIO()
        tempfile.write(val)
        return tempfile

    contract_template = fields.Binary(default=lambda self: self.env.ref('import_utility.account_addresses_excel').datas, string="Template")

    @api.multi
    def get_contract_template(self):
        return {
            'type': 'ir.actions.act_url',
            'name': 'contract',
            'url': '/web/content/import.data/%s/contract_template/PartnerImportTemplate.xls?download=true' % (self.id),
        }

    def convert_to_csv(self, file):
        excel = openpyxl.load_workbook(file)
        sheet = excel.active
        col = csv.writer(open("conf/files/res_partner.csv", 'w', newline=""))
        for row in sheet.rows:
            col.writerow([cell.value for cell in row])

    def read_csv(self):
        csv_data = base64.b64decode(self.upload_file)
        data_file = io.StringIO(csv_data.decode("utf-8"))
        data_file.seek(0)
        file_reader = []
        csv_reader = csv.reader(data_file, delimiter=',')
        file_reader.extend(csv_reader)
        col = csv.writer(open("conf/files/res_partner.csv", 'w', newline=""))
        for row in file_reader:
            col.writerow([cell for cell in row])

    def data_upload_account(self):
        if not self.upload_file or not self.filename:
            raise UserError(_("Error!, Kindly upload the file."))
        extension = self.get_file_type()
        if extension in ['xlsx', 'xls']:
            workbook = self.read_file()
            self.convert_to_csv(workbook)
        else:
            self.read_csv()

        processor = Processor('conf/files/res_partner.csv', delimiter=',')
        company_type_mapping = {'company': 'company', 'individual': 'person'}
        address_mapping = {'account': '', 'contact': 'contact', 'billing': 'invoice', 'shipping': 'delivery', 'purchasing': 'purchase', 'payment': 'invoice'}
        shipping_terms_mapping = {'prepay and add': 'prepaid', 'free shipping': 'free', 'collect': 'collect', '3rd party billing': 'collect'}

        telephone_type_mapping = {
            'id': mapper.m2o_map('import_telephone_type', mapper.val('Telephone Type')),
            'name': mapper.val('Telephone Type'),
            'for_phone': mapper.const('1')
        }

        other_communication_type_mapping = {
            'id': mapper.m2o_map('import_other_communication_type', mapper.val('Other Communication 1 Type')),
            'name': mapper.val('Other Communication 1 Type'),
            'for_other': mapper.const('1')
        }

        other_communication_type_2_mapping = {
            'id': mapper.m2o_map('import_other_communication_type_2', mapper.val('Other Communication 2 Type')),
            'name': mapper.val('Other Communication 2 Type'),
            'for_other': mapper.const('1')
        }

        product_pricelist_mapping = {
            'id': mapper.m2o_map('import_product_pricelist', mapper.val('Pricelist')),
            'name': mapper.val('Pricelist'),
        }

        account_payment_term_mapping = {
            'id': mapper.m2o_map('import_account_payment_term', mapper.val('Sales Payment Terms')),
            'name': mapper.val('Sales Payment Terms'),
        }

        vendor_account_payment_term_mapping = {
            'id': mapper.m2o_map('import_vendor_account_payment_term', mapper.val('Vendor Payment Terms')),
            'name': mapper.val('Vendor Payment Terms'),
        }

        def customer_type_mapper(line):
            if line['Customer Address Type'] == 'account':
                return 'account'
            if line['Customer Address Type'] == 'contact':
                return 'contact'
            if line['Customer Address Type'] == "billing":
                return 'invoice'
            if line['Customer Address Type'] == "shipping":
                return 'delivery'
            return 'contact'

        def vendor_type_mapper(line):
            if line['Vendor Address Type'] == 'account':
                return 'account'
            if line['Vendor Address Type'] == 'contact':
                return 'contact'
            if line['Vendor Address Type'] == 'payment':
                return 'invoice'
            if line['Vendor Address Type'] == 'shipping':
                return 'delivery'
            if line['Vendor Address Type'] == "purchasing":
                return 'purchase'
            return 'contact'

        customer_description_mapping = {
            'id': mapper.m2o_map('import_customer_description', mapper.val('Customer Description')),
            'name': mapper.val('Customer Description'),
            'type': customer_type_mapper,
        }

        vendor_description_mapping = {
            'id': mapper.m2o_map('import_vendor_description', mapper.val('Vendor Description')),
            'name': mapper.val('Vendor Description'),
            'type': vendor_type_mapper,
        }

        customer_tags_mapping = {
            'id': mapper.m2m_id_list('customer_tags', 'Customer Tags'),
            'name': mapper.val('Customer Tags'),
            'type': customer_type_mapper,
        }

        vendor_tags_mapping = {
            'id': mapper.m2m_id_list('vendor_tags', 'Vendor Tags'),
            'name': mapper.val('Vendor Tags'),
            'type_vendor': vendor_type_mapper,
            'for_vendor': mapper.const('1')
        }

        def tags_mapper(line):
            if line['Customer Tags']:
                return 'customer_tags.' + line['Customer Tags']
            if line['Vendor Tags']:
                return 'vendor_tags.' + line['Vendor Tags']
            return None

        def address_type_mapper(line):
            if line['Customer Address Type'] == 'contact' or line['Vendor Address Type'] == 'contact':
                return 'other'
            if line['Customer Address Type'] == "billing" or line['Vendor Address Type'] == 'payment':
                return 'invoice'
            if line['Customer Address Type'] == "shipping" or line['Vendor Address Type'] == 'shipping':
                return 'delivery'
            if line['Vendor Address Type'] == "purchasing":
                return 'purchase'
            return None

        def last_credit_mapper(line):
            if line['Last Credit Review']:
                last_credit_date = dateutil.parser.parse(line['Last Credit Review'])
                return datetime.strptime(str(last_credit_date), '%Y-%m-%d  %H:%M:%S')
            return None

        def comments_mapper(line):
            if line['Sales Comments']:
                return line['Sales Comments']
            if line['Address Comments']:
                return line['Address Comments']
            return None

        def default_address_mapper(line):
            if line['Sales Default Address'] in ['false', 'true']:
                if line['Sales Default Address'] == 'false':
                    return 0
                return 1
            if line['Purchasing Default Address'] in ['false', 'true']:
                if line['Purchasing Default Address'] == 'false':
                    return 0
                return 1
            return 0

        def sale_currency_mapper(line):
            if line['Sales Currency']:
                return 'base.' + line['Sales Currency']
            return 'base.USD'

        def purchase_currency_mapper(line):
            if line['Purchasing Currency']:
                return 'base.' + line['Purchasing Currency']
            return 'base.USD'

        country_map = {
            'UNITED STATES': 'base.us',
            'CANADA': 'base.ca',
        }

        def child_mapper(line):
            if line['Address ID'] != '0':
                return 'import_res_partner.' + line['Account ID'] + '_' + line['Address ID']
            return None

        def parent_mapper(line):
            if line['Address ID'] != '0':
                return 'import_res_partner.' + line['Account ID'] + '_0'
            return None

        def account_mapper(line):
            if line['Address ID'] == '0':
                return 'import_res_partner.' + line['Account ID'] + '_0'
            return None

        def created_date_mapper(line):
            if line['Date Created']:
                create_date = dateutil.parser.parse(line['Date Created'])
                return datetime.strptime(str(create_date), '%Y-%m-%d  %H:%M:%S')
            return None

        def last_used_date_mapper(line):
            if line['Date Last Used']:
                last_used_date = dateutil.parser.parse(line['Date Last Used'])
                return datetime.strptime(str(last_used_date), '%Y-%m-%d  %H:%M:%S')
            return None

        res_partner_account_mapping = {
            'id': account_mapper,
            'name': mapper.val('Name'),
            'old_account_id': mapper.val('Account ID'),
            'old_address_id': mapper.val('Address ID'),
            'customer': mapper.bool_val('Customer', ['true'], ['false']),
            'supplier': mapper.bool_val('Vendor', ['true'], ['false']),
            'is_supplier': mapper.bool_val('Vendor', ['true'], ['false']),
            'company_type': mapper.map_val('Account Type', company_type_mapping),
            'comp_name': mapper.val('Company Name'),
            'street': mapper.val('Street Line 1'),
            'street2': mapper.val('Street Line 2'),
            'street3': mapper.val('Street Line 3'),
            'city': mapper.val('City'),
            'state_id': mapper.val('State'),
            'zip': mapper.val('Zipcode'),
            'country_id/id': mapper.map_val('Country', country_map),
            'icon_letters': mapper.val('Icon'),
            'email': mapper.val('Email '),
            'phone': mapper.val('Telephone'),
            'primary_tel_type/id': mapper.m2o_map('import_telephone_type', mapper.val('Telephone Type')),
            'alternate_communication_1': mapper.val('Other Communication 1'),
            'alternate_commu_type_1/id': mapper.m2o_map('import_other_communication_type', mapper.val('Other Communication 1 Type')),
            'alternate_communication_2': mapper.val('Other Communication 2'),
            'alternate_commu_type_2/id': mapper.m2o_map('import_other_communication_type_2', mapper.val('Other Communication 2 Type')),
            'website': mapper.val('Website'),
            'add_date_created': created_date_mapper,
            'add_last_used_date': last_used_date_mapper,
            'currency_id/id': sale_currency_mapper,
            'sal_currency_id/id': sale_currency_mapper,
            'property_purchase_currency_id/id': purchase_currency_mapper,
            'pur_currency_id/id': purchase_currency_mapper,
            'barcode': mapper.val('Account Barcode'),
            'sale_shipping_terms': mapper.map_val('Customer Shipping Terms', shipping_terms_mapping),
            'campaign_id': mapper.val('Campaign'),
            'medium_id': mapper.val('Medium'),
            'source_id': mapper.val('Source'),
            'referred': mapper.val('Referred By'),
            'property_product_pricelist/id': mapper.m2o_map('import_product_pricelist', mapper.val('Pricelist')),
            'property_payment_term_id/id': mapper.m2o_map('import_account_payment_term', mapper.val('Sales Payment Terms')),
            'property_supplier_payment_term_id/id': mapper.m2o_map('import_vendor_account_payment_term', mapper.val('Vendor Payment Terms')),
            'quotation_warn_msg': mapper.val('Quotation Warning'),
            'picking_warn_msg': mapper.val('Shipment Warning'),
            'comment': comments_mapper,
            'credit_limit': mapper.val('Credit Limit'),
            'van_credit_limit': mapper.val('Vendor Credit Limit'),
            'credit_hold': mapper.bool_val('Credit Hold', ['yes'], ['no']),
            'cust_overdue': mapper.num('Overdue'),
            'supp_overdue': mapper.num('Vendor Overdue'),
            'cust_avg_days': mapper.num('Average Pay Days', default='0'),
            'cus_acc_bal': mapper.num('Sales Account Balance'),
            'van_acc_bal': mapper.num('Vendor Account Balance'),
            'credit_avl': mapper.num('Credit Available'),
            'van_credit_avl': mapper.num('Vendor Credit Available'),
            'curr_order': mapper.num('Current Orders'),
            'last_credit_rev': last_credit_mapper,
            'category_id/id': tags_mapper,
            'desc/id': mapper.m2o_map('import_customer_description', mapper.val('Customer Description')),
            'pur_desc_id/id': mapper.m2o_map('import_vendor_description', mapper.val('Vendor Description')),
        }

        res_partner_mapping = {
            'id': child_mapper,
            'parent_id/id': parent_mapper,
            'name': mapper.val('Name'),
            'old_account_id': mapper.val('Account ID'),
            'old_address_id': mapper.val('Address ID'),
            'customer': mapper.bool_val('Customer', ['true'], ['false']),
            'supplier': mapper.bool_val('Vendor', ['true'], ['false']),
            'is_supplier': mapper.bool_val('Vendor', ['true'], ['false']),
            'type_extend': mapper.map_val('Customer Address Type', address_mapping),
            'vendor_addr_type': mapper.map_val('Vendor Address Type', address_mapping),
            'type': address_type_mapper,
            'use_acc_comm': mapper.bool_val('Same as Account', ['true'], ['false']),
            'default_address': default_address_mapper,
            'company_type': mapper.map_val('Account Type', company_type_mapping),
            'comp_name': mapper.val('Company Name'),
            'street': mapper.val('Street Line 1'),
            'street2': mapper.val('Street Line 2'),
            'street3': mapper.val('Street Line 3'),
            'city': mapper.val('City'),
            'state_id': mapper.val('State'),
            'zip': mapper.val('Zipcode'),
            'country_id/id': mapper.map_val('Country', country_map),
            'icon_letters': mapper.val('Icon'),
            'email': mapper.val('Email '),
            'phone': mapper.val('Telephone'),
            'primary_tel_type/id': mapper.m2o_map('import_telephone_type', mapper.val('Telephone Type')),
            'alternate_communication_1': mapper.val('Other Communication 1'),
            'alternate_commu_type_1/id': mapper.m2o_map('import_other_communication_type', mapper.val('Other Communication 1 Type')),
            'alternate_communication_2': mapper.val('Other Communication 2'),
            'alternate_commu_type_2/id': mapper.m2o_map('import_other_communication_type_2', mapper.val('Other Communication 2 Type')),
            'website': mapper.val('Website'),
            'add_date_created': created_date_mapper,
            'add_last_used_date': last_used_date_mapper,
            'currency_id/id': sale_currency_mapper,
            'sal_currency_id/id': sale_currency_mapper,
            'property_purchase_currency_id/id': purchase_currency_mapper,
            'pur_currency_id/id': purchase_currency_mapper,
            'barcode': mapper.val('Account Barcode'),
            'sale_shipping_terms': mapper.map_val('Customer Shipping Terms', shipping_terms_mapping),
            'campaign_id': mapper.val('Campaign'),
            'medium_id': mapper.val('Medium'),
            'source_id': mapper.val('Source'),
            'referred': mapper.val('Referred By'),
            'property_product_pricelist/id': mapper.m2o_map('import_product_pricelist', mapper.val('Pricelist')),
            'property_payment_term_id/id': mapper.m2o_map('import_account_payment_term', mapper.val('Sales Payment Terms')),
            'property_supplier_payment_term_id/id': mapper.m2o_map('import_vendor_account_payment_term', mapper.val('Vendor Payment Terms')),
            'quotation_warn_msg': mapper.val('Quotation Warning'),
            'picking_warn_msg': mapper.val('Shipment Warning'),
            'comment': comments_mapper,
            'credit_limit': mapper.val('Credit Limit'),
            'van_credit_limit': mapper.val('Vendor Credit Limit'),
            'credit_hold': mapper.bool_val('Credit Hold', ['yes'], ['no']),
            'cust_overdue': mapper.num('Overdue'),
            'supp_overdue': mapper.num('Vendor Overdue'),
            'cust_avg_days': mapper.num('Average Pay Days', default='0'),
            'cus_acc_bal': mapper.num('Sales Account Balance'),
            'van_acc_bal': mapper.num('Vendor Account Balance'),
            'credit_avl': mapper.num('Credit Available'),
            'van_credit_avl': mapper.num('Vendor Credit Available'),
            'curr_order': mapper.num('Current Orders'),
            'last_credit_rev': last_credit_mapper,
            'category_id/id': tags_mapper,
            'desc/id': mapper.m2o_map('import_customer_description', mapper.val('Customer Description')),
            'pur_desc_id/id': mapper.m2o_map('import_vendor_description', mapper.val('Vendor Description')),
        }

        res_parent_mapping = {
            'id': child_mapper,
            'customer': mapper.const('0'),
            'supplier': mapper.const('0'),
        }

        processor.process(telephone_type_mapping, 'conf/files/communication.type.csv', {'model': 'communication.type', 'worker': self.workers, 'batch_size': self.size}, 'set')
        processor.process(other_communication_type_mapping, 'conf/files/other.communication.type.csv', {'model': 'communication.type', 'worker': self.workers, 'batch_size': self.size}, 'set')
        processor.process(other_communication_type_2_mapping, 'conf/files/other.communication.type.2.csv', {'model': 'communication.type', 'worker': self.workers, 'batch_size': self.size}, 'set')
        processor.process(product_pricelist_mapping, 'conf/files/product.pricelist.csv', {'model': 'product.pricelist', 'worker': self.workers, 'batch_size': self.size}, 'set')
        processor.process(account_payment_term_mapping, 'conf/files/account.payment.term.csv', {'model': 'account.payment.term', 'worker': self.workers, 'batch_size': self.size}, 'set')
        processor.process(vendor_account_payment_term_mapping, 'conf/files/vendor.account.payment.term.csv', {'model': 'account.payment.term', 'worker': self.workers, 'batch_size': self.size}, 'set')
        processor.process(customer_description_mapping, 'conf/files/customer.description.csv', {'model': 'customer.description', 'worker': self.workers, 'batch_size': self.size}, 'set')
        processor.process(vendor_description_mapping, 'conf/files/vendor.description.csv', {'model': 'vendor.description', 'worker': self.workers, 'batch_size': self.size}, 'set')
        processor.process(customer_tags_mapping, 'conf/files/res.partner.category.csv', {'model': 'res.partner.category', 'worker': self.workers, 'batch_size': self.size}, m2m=True)
        processor.process(vendor_tags_mapping, 'conf/files/res.partner.vendor.category.csv', {'model': 'res.partner.category', 'worker': self.workers, 'batch_size': self.size}, m2m=True)
        processor.process(res_partner_account_mapping, 'conf/files/res.partner.account.csv', {'model': 'res.partner', 'context': "{'tracking_disable': True}", 'worker': self.workers, 'batch_size': self.size}, 'set')
        processor.process(res_partner_mapping, 'conf/files/res.partner.csv', {'model': 'res.partner', 'context': "{'tracking_disable': True}", 'worker': self.workers, 'batch_size': self.size, 'groupby': 'parent_id/id'}, 'set')
        processor.process(res_parent_mapping, 'conf/files/res.child.csv', {'model': 'res.partner', 'context': "{'tracking_disable': True}", 'worker': self.workers, 'batch_size': self.size}, 'set')
        processor.write_to_file("conf/files/res_partner.sh", python_exe='', path='')
        with open("conf/files/res.partner.account.csv", "r") as file:
            lines = file.readlines()
        with open("conf/files/res.partner.account.csv", "w") as file:
            index = lines[0].split(';').index('"id"')
            for line in lines:
                if line.split(";")[index] != '""':
                    file.write(line)
        with open("conf/files/res.partner.csv", "r") as file:
            lines = file.readlines()
        with open("conf/files/res.partner.csv", "w") as file:
            index = lines[0].split(';').index('"id"')
            for line in lines:
                if line.split(";")[index] != '""':
                    file.write(line)
        with open("conf/files/res.child.csv", "r") as file:
            lines = file.readlines()
        with open("conf/files/res.child.csv", "w") as file:
            index = lines[0].split(';').index('"id"')
            for line in lines:
                if line.split(";")[index] != '""':
                    file.write(line)
        with open("conf/files/res_partner.sh", "r") as file:
            lines = file.readlines()
        with open("conf/files/res_partner.sh", "w") as file:
            for line in lines:
                old_string = 'conf/connection.conf'
                new_string = 'conf/connection.conf'
                if old_string in line:
                    line = line.replace(old_string, new_string)
                    file.write(line)
                else:
                    file.write(line)
        process = subprocess.Popen(['sh conf/files/res_partner.sh'], shell=True)
