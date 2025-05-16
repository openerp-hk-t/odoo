# -*- coding: utf-8 -*-

from odoo import models, fields, api


class OpenerpHkResUsers(models.Model):
    _inherit = 'res.users'
    usr_name = fields.Char(string="name")
    sex = fields.Selection([('male', 'male'), ('female', 'female')], string="gender")
    work_phone = fields.Char(string="work phone")
    work_address = fields.Char(string="workplace")
    user_state = fields.Selection([('normal', 'normal'), ('disabled', 'disabled')], string="state", default="normal")

    authority_ids = fields.Many2many('openerphk.authority', string='User Permissions', relation='res_user_openerphk_authority_rel',
                                     column1='user_id', column2='authority_id')
    has_allocate_authority = fields.Boolean(string="Assign Role", compute="_compute_has_allocate_authority", store=True)

    @api.depends('authority_ids')
    def _compute_has_allocate_authority(self):
        for rec in self:
            if len(rec.authority_ids) > 0:
                rec.has_allocate_authority = True
            else:
                rec.has_allocate_authority = False

    def allocate_roles(self):
        self.ensure_one()
        return {
            'name': '分配角色',
            'view_mode': 'form',
            'res_model': 'res.users',
            'type': 'ir.actions.act_window',
            'views': [
                [self.env.ref('openerphk_authority.openerphk_res_users_authority_form').id, 'form']
            ],
            'res_id': self.id,
            'target': 'new'
        }
