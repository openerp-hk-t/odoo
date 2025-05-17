# -*- coding: utf-8 -*-

from odoo import models, fields, api


class LoginLog(models.Model):
    _name = 'login.log'
    _description = '登录日志'

    user_id = fields.Integer(string='用户ID')
    user_name = fields.Char(string='用户姓名')
    login_ip = fields.Char(string='登录IP')
    operating_system = fields.Char(string='操作系统')
    browser = fields.Char(string='浏览器')
    login_time = fields.Datetime(string='登录时间')
