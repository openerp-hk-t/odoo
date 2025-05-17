# -*- coding: utf-8 -*-
from odoo import http
from odoo.addons.web.controllers.home import Home
from odoo.http import request
from odoo.models import fields


class HomeExtend(Home):
    @http.route()
    def web_login(self, *args, **kw):
        result = super(HomeExtend, self).web_login(*args, **kw)
        if request.httprequest.method == 'POST' and request.params.get('login_success', False):
            environ = request.httprequest.headers.environ
            request.env['login.log'].create({
                'user_id': request.env.user.id,
                'user_name': request.env.user.name,
                'login_ip': environ.get('REMOTE_ADDR'),
                'operating_system': environ.get('HTTP_SEC_CH_UA_PLATFORM'),
                'browser': environ.get('HTTP_USER_AGENT') or environ.get('HTTP_SEC_CH_UA'),
                'login_time': fields.Datetime.now()
            })
        return result
