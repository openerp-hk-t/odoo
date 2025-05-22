from odoo import api,fields,models

class LLMConfig(models.Model):
    _name = 'llm.config'
    _inherit = ['mail.thread']
    _description = 'LLM Configuration'

    name = fields.Char('Model Name',required=True)
    temperature = fields.Float('Temperature',required=True,default=0.0)
    model = fields.Char('Model',required=True)
    model_URL = fields.Char('Model host',required=True,default='https://odoollm.cpolar.top/v1')

    is_out_default = fields.Boolean('Default Arrange Model',default=False,copy=False)
    is_chat_default = fields.Boolean('Default Chat Model',default=False,copy=False)
    note = fields.Text('Note')
    prompt = fields.Text('Prompt')

    @api.onchange('is_out_default')
    def check_is_out_default(self):
        if self.is_out_default is True:
            config_ids = self.env['llm.config'].sudo().search([])
            config_ids.sudo().write({'is_out_default': False})
            self.sudo().write({'is_out_default': True})

    @api.onchange('is_chat_default')
    def check_is_chat_default(self):
        if self.is_chat_default is True:
            config_ids = self.env['llm.config'].sudo().search([])
            config_ids.sudo().write({'is_chat_default': False})
            self.sudo().write({'is_chat_default': True})