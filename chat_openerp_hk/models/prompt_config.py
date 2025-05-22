from odoo import api,fields,models


class PromptConfig(models.Model):
    _name = 'prompt.config'
    _description = '提示词模板'

    name = fields.Char('Prompt Name',required=True)
    default_prompt = fields.Boolean(string='Default Prompt',default=False)

    system = fields.Text('System',required=True)
    user = fields.Text('User')
    output_format = fields.Text('Output',required=True)

