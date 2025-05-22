# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ChatOpenerpHkSetting(models.TransientModel):
    _inherit = 'res.config.settings'

    IP = fields.Char(string='Interface Address',default='https://odooai.cpolar.top')



    def set_values(self):
        super(ChatOpenerpHkSetting, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('chat_openerp_hk.IP', self.IP)

    def get_values(self):
        res = super(ChatOpenerpHkSetting, self).get_values()
        config_params = self.env['ir.config_parameter'].sudo()
        res.update(
            IP=config_params.get_param('chat_openerp_hk.IP'),
        )
        return res
