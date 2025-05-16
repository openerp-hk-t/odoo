# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import base64
import xlrd


class ImportAuthorityWizard(models.TransientModel):
    _name = 'import.authority.wizard'
    _description = 'import wizard'

    file = fields.Binary(string='Excel File')
    filename = fields.Char()
    authority_id = fields.Many2one('openerphk.authority', string='permission')

    def action_confirm(self):
        self.ensure_one()
        if not self.file:
            raise ValidationError('请先上传导入再进行导入!')
        xls = base64.decodebytes(self.file)
        try:
            book = xlrd.open_workbook(file_contents=xls, encoding_override='utf-8')
        except Exception as e:
            raise ValidationError('文件解析失败请联系管理员!')
        sheet = book.sheet_by_index(0)
        if self._context.get('import_type', '') == 'user':
            self.parse_user_data(sheet)
        if self._context.get('import_type', '') == 'group':
            self.parse_group_data(sheet)

    def parse_group_data(self, sheet):
        """
        [群组名称]
        """
        error = ''
        group_env = self.env['res.groups'].sudo()
        for row in range(1, sheet.nrows):
            val = sheet.row_values(row)
            groups = group_env.search([('name', '=', val[0])], limit=1)
            if not groups:
                error += f'第{row}行, 未找到群组: {val[0]}\n'
            else:
                for group in groups.mapped('users'):
                    self.authority_id.user_ids = [(4, group.id)]

        if error:
            raise ValidationError(error)

    def parse_user_data(self, sheet):
        """
        [名称，登录]
        """
        error = ''
        user_env = self.env['res.users'].sudo()
        for row in range(1, sheet.nrows):
            val = sheet.row_values(row)
            user = user_env.search([('name', '=', val[0]), ('login', '=', val[1])], limit=1)
            if not user:
                error += f'第{row}行, 未找到用户: {val[0]}\n'
            else:
                self.authority_id.user_ids = [(4, user.id)]

        if error:
            raise ValidationError(error)
