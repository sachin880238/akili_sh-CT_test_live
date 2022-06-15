from odoo import api, fields,models, _
from datetime import datetime, date
import base64, urllib
from io import BytesIO
import xlrd
from odoo.exceptions import UserError

class ImportData(models.TransientModel):
    _name="import.leads"
    _description = 'Import Leads Data'

    upload_file=fields.Binary("File")
    
    def read_excel(self):
        if not self.upload_file:
            raise UserError(_("Error!, Please Select a File"))            
        else:
            val = base64.decodestring(self.upload_file )
            tempfile = BytesIO()
            tempfile.write(val)
            work_book = xlrd.open_workbook(file_contents=tempfile.getvalue()) 
        return work_book

    contract_template = fields.Binary(default=lambda self: self.env.ref('crm_import_utility.crm_lead_excel').datas,string="Template")

    @api.multi
    def get_contract_template(self):
        return {
        'type': 'ir.actions.act_url',
        'name': 'contract',
        'url': '/web/content/import.leads/%s/contract_template/LeadsImportTemplate.xls?download=true' %(self.id),

        }

    def data_upload_leads(self):
        wb = self.read_excel()
        sheet1= wb.sheet_by_index(0)
        sheet_rows=sheet1.nrows
        crm_leads_obj = self.env['crm.lead']
        country_obj = self.env['res.country']
        state_obj =   self.env['res.country.state']
        desc_obj = self.env['customer.description']
        catog_obj = self.env['crm.lead.tag']
        communication_obj = self.env['communication.type']
        lead_team_obj = self.env['crm.team']
        campaign_obj = self.env['utm.campaign']
        medium_id_obj = self.env['utm.medium']
        source_id_obj = self.env['utm.source']
        language_obj = self.env['res.lang']
        user_id_obj = self.env['res.users']
        count = 0
        for row in range(1,sheet_rows):
            data_dict={} 
            if sheet1.row_values(row)[1]:
                data_dict['contact_name'] = str(sheet1.row_values(row)[1])
            
            if sheet1.row_values(row)[2]: 
                data_dict['company_name'] = str(sheet1.row_values(row)[2])

            if sheet1.row_values(row)[3]: 
                data_dict['street'] = str(sheet1.row_values(row)[3])   
                
            if sheet1.row_values(row)[4]: 
                data_dict['street2'] = str(sheet1.row_values(row)[4])

            if sheet1.row_values(row)[5]: 
                data_dict['street3'] = str(sheet1.row_values(row)[5])   
                
            if sheet1.row_values(row)[6]: 
                data_dict['city'] = str(sheet1.row_values(row)[6])

            if sheet1.row_values(row)[7]:
                state_id = state_obj.search(['|',('name','=',sheet1.row_values(row)[7]),('code','=',sheet1.row_values(row)[7])])
                if state_id:
                    for state in state_id:
                        data_dict["state_id"]= state.id
            if sheet1.row_values(row)[8]: 
                data_dict['zip'] = str(sheet1.row_values(row)[8])

            if sheet1.row_values(row)[9]:
                country_id = country_obj.search(['|',('name','=',sheet1.row_values(row)[9]),('code','=',sheet1.row_values(row)[9])])
                if country_id:
                    data_dict["country_id"] = country_id.id

            if sheet1.row_values(row)[10]:
                des_id = desc_obj.search([('name', '=', sheet1.row_values(row)[10]), ('type', '=', 'contact')])
                if des_id:
                    data_dict["desc"]=des_id.id
                else:
                    description_id = desc_obj.create({'name' : sheet1.row_values(row)[10], 'type' : 'contact'})
                    data_dict["desc"]=description_id.id
            
            if sheet1.row_values(row)[11]: 
                data_dict['name'] = str(sheet1.row_values(row)[11]) 

            if sheet1.row_values(row)[12]: 
                data_dict['lead_icon_letters'] = str(sheet1.row_values(row)[12])

            if sheet1.row_values(row)[13]:
                catog_ids = catog_obj.search([('name','=',sheet1.row_values(row)[13])])
                if catog_ids:
                    data_dict["category_ids"]=[(6,0,[catog_ids.id])]
                else:               
                    category_id = catog_obj.create({'name':sheet1.row_values(row)[13]})
                    data_dict["category_ids"]=[(6,0,[category_id.id])]

            if sheet1.row_values(row)[14]: 
                data_dict['email_from'] = str(sheet1.row_values(row)[14])

            if sheet1.row_values(row)[15]: 
                data_dict['phone'] = str(sheet1.row_values(row)[15]) 

            if sheet1.row_values(row)[16]:
                primary_comm_type_id = communication_obj.search([('name','=',sheet1.row_values(row)[16])])
                if primary_comm_type_id:
                    data_dict['primary_tel_type'] = primary_comm_type_id.id
                else:
                    primary_comm_type_id = communication_obj.create({'name':sheet1.row_values(row)[16],'for_other':True})
                    data_dict['primary_tel_type']= primary_comm_type_id.id

            if sheet1.row_values(row)[17]: 
                data_dict['alternate_communication_1'] = str(sheet1.row_values(row)[17]) 

            if sheet1.row_values(row)[18]:
                alter_comm_type_id = communication_obj.search([('name','=',sheet1.row_values(row)[18])])
                if alter_comm_type_id:
                    data_dict['alternate_commu_type_1'] = alter_comm_type_id.id
                else:
                    alter_comm_type_id = communication_obj.create({'name':sheet1.row_values(row)[18],'for_other':True})
                    data_dict['alternate_commu_type_1']= alter_comm_type_id.id

            if sheet1.row_values(row)[19]: 
                data_dict['alternate_communication_2'] = str(sheet1.row_values(row)[19])

            if sheet1.row_values(row)[20]:
                alter_commu_type_id = communication_obj.search([('name','=',sheet1.row_values(row)[20])])
                if alter_commu_type_id:
                    data_dict['alternate_commu_type_2'] = alter_commu_type_id.id
                else:
                    alter_commu_type_id = communication_obj.create({'name':sheet1.row_values(row)[20],'for_other':True})
                    data_dict['alternate_commu_type_2']= alter_commu_type_id.id

            if sheet1.row_values(row)[21]: 
                data_dict['website'] = str(sheet1.row_values(row)[21])

            if sheet1.row_values(row)[22]:
                active_language = language_obj.search([])
                inactive_lang = language_obj.search([('active','=',False)])
                for lang in active_language:
                    if sheet1.row_values(row)[22] in lang.name:
                        data_dict["lang"] = lang.code
                        break
                if not data_dict.get("lang",False):
                    for lang in inactive_lang:
                        if sheet1.row_values(row)[22] in lang.name:
                            lang.write({'active':True})
                            data_dict["lang"] = lang.code
                            break

            if sheet1.row_values(row)[23]:
                lead_team_id = lead_team_obj.search([('name','=',sheet1.row_values(row)[23])])
                if lead_team_id:
                    data_dict['lead_team'] = lead_team_id.id
                else:
                    new_lead_team = lead_team_obj.create({'name':sheet1.row_values(row)[23]})
                    data_dict['lead_team']= new_lead_team.id

            # if sheet1.row_values(row)[24]:
            #     team_id = lead_team_obj.search([('name','=',sheet1.row_values(row)[24])])
            #     if team_id:
            #         data_dict['team_id'] = team_id.id
            #     else:
            #         sales_team = lead_team_obj.create({'name':sheet1.row_values(row)[24]})
            #         data_dict['team_id']= sales_team.id
            
            # if sheet1.row_values(row)[25]:
            #     user_id = user_id_obj.search([('name','=',sheet1.row_values(row)[25])])
            #     if user_id:
            #         data_dict['user_id'] = user_id.id
            #     else:
            #         new_id = user_id_obj.create({'name':sheet1.row_values(row)[25]})
            #         data_dict['user_id']= new_id.id

            if sheet1.row_values(row)[26]: 
                data_dict['description'] = str(sheet1.row_values(row)[26]) 

            if sheet1.row_values(row)[27]:
                date_created = datetime(*xlrd.xldate_as_tuple(sheet1.row_values(row)[27], 0))
                data_dict["created_date"]= date_created.strftime("%Y-%m-%d %H:%M:%S")

            if sheet1.row_values(row)[28]:
                campaign_id = campaign_obj.search([('name','=',sheet1.row_values(row)[28])])
                if campaign_id:
                    data_dict['campaign_id'] = campaign_id.id
                else:
                    new_campaign_id = campaign_obj.create({'name':sheet1.row_values(row)[27]})
                    data_dict['campaign_id']= new_campaign_id.id

            if sheet1.row_values(row)[29]:
                medium_id = medium_id_obj.search([('name','=',sheet1.row_values(row)[29])])
                if campaign_id:
                    data_dict['medium_id'] = medium_id.id
                else:
                    new_medium_id = medium_id_obj.create({'name':sheet1.row_values(row)[29]})
                    data_dict['medium_id']= new_medium_id.id

            if sheet1.row_values(row)[30]:
                source_id = source_id_obj.search([('name','=',sheet1.row_values(row)[30])])
                if source_id:
                    data_dict['source_id'] = source_id.id
                else:
                    new_source_id = source_id_obj.create({'name':sheet1.row_values(row)[30]})
                    data_dict['source_id']= new_source_id.id

            if sheet1.row_values(row)[31]: 
                data_dict['referred'] = str(sheet1.row_values(row)[31])
            crm_leads_obj = crm_leads_obj.with_context(needaction_menu_ref='crm.menu_crm_opportunities', default_type='lead', search_default_to_process=1, search_default_type='lead') 
            CRM_LEADS = crm_leads_obj.create(data_dict)

        message = 'All Leads uploaded successfully !!!!! '
        temp_id = self.env['wizard.message'].create({'text':message})
        return {
            'name':_("Test Result"),
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'wizard.message',
            'res_id': temp_id.id,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
           }

