# -*- coding: utf-8 -*-

from odoo import models, fields, api


class OpenerpHkAuthority(models.Model):
    _name = 'openerphk.authority'
    _description = 'Permission configuration'

    name = fields.Char(string="Permission Name")
    menu_ids = fields.Many2many('ir.ui.menu', string='Permission menu configuration')
    app_menu_ids = fields.Many2many('app.menu', string='App permission menu configuration')
    user_ids = fields.Many2many('res.users', string='Effective user', relation='res_user_openerphk_authority_rel',
                                column1='authority_id', column2='user_id')
    sub_authority_ids = fields.One2many('sub.menu.authority', 'authority_id', string='Sub permission group')
    app_authority_ids = fields.One2many('app.menu.authority', 'authority_id', string='App sub permission group')

    def download_template(self):
        self.ensure_one()
        if self._context.get('import_type', '') == 'user':
            url = '/openerphk_authority/static/template/生效用户导入模板-用户.xlsx'
        else:
            url = '/openerphk_authority/static/template/生效用户导入模板-群组.xlsx'

        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': url
        }

    def import_user_data(self):
        """
        导入数据
        """
        self.ensure_one()
        view = self.env.ref('openerphk_authority.import_authority_wizard_form')
        return {
            'type': 'ir.actions.act_window',
            'name': '导入',
            'res_model': 'import.authority.wizard',
            'view_mode': 'form',
            'views': [[view.id, 'form']],
            'target': 'new',
            'context': {
                'default_authority_id': self.id,
                'import_type': 'user'
            }
        }

    def import_group_data(self):
        """
        导入数据
        """
        self.ensure_one()
        view = self.env.ref('openerphk_authority.import_authority_wizard_form')
        return {
            'type': 'ir.actions.act_window',
            'name': '导入',
            'res_model': 'import.authority.wizard',
            'view_mode': 'form',
            'views': [[view.id, 'form']],
            'target': 'new',
            'context': {
                'default_authority_id': self.id,
                'import_type': 'group'
            }
        }

    def get_menu_tree(self, with_user=False):
        """
        获取zTree数据格式的菜单树
        参数 orm的resId 不然无法获取已有权限菜单项
        :return: {
            'all_menu': all_menu,
            'authority_menu': authority_menu,
            'all_app_menu': all_app_menu,
            'authority_app_menu': authority_app_menu,
        }
        """
        menus = self.env['ir.ui.menu'].load_menus('self._uid')
        all_menu = []
        all_app_menu = [{
                        "id": "app_root",
                        "name": "APP all menu",
                        "isParent": True,
                        "pId": 0,
                        "open": True
                    }]
        authority_menu = []
        authority_app_menu = [{
                        "id": "app_root",
                        "name": "APP permission menu",
                        "isParent": True,
                        "pId": 0,
                        "open": True
                    }]
        res = {
            'all_menu': all_menu,
            'authority_menu': authority_menu,
            'all_app_menu': all_app_menu,
            'authority_app_menu': authority_app_menu,
        }
        if not with_user:
            for i in menus:
                if menus[i]['name'] == 'root':
                    all_menu.append({
                        "id": "root",
                        "name": "All menus",
                        "pId": 0,
                        "open": True
                    })
                    authority_menu.append({
                        "id": "root",
                        "name": "Permission menu",
                        "pId": 0,
                        "open": True
                    })
                elif menus[i]['name'] != 'root':
                    all_menu.append({
                        "id": menus[i]['id'],
                        "name": menus[i]['name'],
                        "pId": menus[i]['parent_id'][0] if bool(menus[i]['parent_id']) else 'root',
                    })
                    if bool(menus[i]['children']) or menus[i]['id'] in self.menu_ids.ids:
                        authority_menu.append({
                            "id": menus[i]['id'],
                            "name": menus[i]['name'],
                            "pId": menus[i]['parent_id'][0] if bool(menus[i]['parent_id']) else 'root',
                            "isParent": True if bool(menus[i]['children']) else False,
                            'xmlid': menus[i]['xmlid']
                        })
            # app
            for i in self.env['app.menu'].search([]):
                all_app_menu.append({
                    "id": i.id,
                    "name": i.name,
                    "pId": i.parent_id.id if i.parent_id.id else 'app_root',
                    "isParent": True if i.child_ids else False
                })
                if i.child_ids or i.id in self.app_menu_ids.ids:
                    authority_app_menu.append({
                        "id": i.id,
                        "name": i.name,
                        "pId": i.parent_id.id if i.parent_id.id else 'app_root',
                        "isParent": True if i.child_ids else False
                    })

        else:
            records = self.sudo().search([])
            menu_mix = []
            app_mix = []
            for record in records:
                if self.env.uid in record.user_ids.ids:
                    if record.menu_ids.ids:
                        menu_mix += record.menu_ids.ids
                    for app_menu in  record.app_menu_ids:
                        app_authoritys = record.app_authority_ids.search([('menu_id', '=', app_menu.id)])
                        app_mix.append({
                            "name": app_menu.name,
                            "write": bool(app_authoritys.filtered(lambda authority: authority.openerphk_write)),
                            "create": bool(app_authoritys.filtered(lambda authority: authority.openerphk_create)),
                            "delete": bool(app_authoritys.filtered(lambda authority: authority.openerphk_delete)),
                            "export": bool(app_authoritys.filtered(lambda authority: authority.openerphk_export)),
                        })

            if not menu_mix: # 代表没有配置任何菜单权限   默认不受权限控制
                res = {
                    'all_menu': [],
                    'authority_menu': []
                }
            for i in menus:
                if menus[i]['name'] != 'root' and menus[i]['id'] not in menu_mix and not menus[i]['children']:
                    authority_menu.append({
                        "id": menus[i]['id'],
                        "name": menus[i]['name'],
                        "pId": menus[i]['parent_id'][0] if bool(menus[i]['parent_id']) else 'root',
                        'children': [],
                        "isParent": False,
                        'xmlid': menus[i]['xmlid']
                    })
                if menus[i]['name'] != 'root':
                    all_menu.append({
                        "id": menus[i]['id'],
                        "name": menus[i]['name'],
                        "pId": menus[i]['parent_id'][0] if bool(menus[i]['parent_id']) else 'root',
                        'children': menus[i]['children'] if menus[i]['children'] else []
                    })
            res.update({
                'app_mix': app_mix
            })
        return res

    def get_click_menu_authority(self, menu_id):
        """
        获取点击菜单权限
        参数resId, menuId
        :return:{
            'openerphk_write': authority.openerphk_write,
            'openerphk_create': authority.openerphk_create,
            'openerphk_delete': authority.openerphk_delete,
            'openerphk_export': authority.openerphk_export,
        }
        """
        authority = self.env['sub.menu.authority'].search([
            ('authority_id', '=', self.id), ('menu_id', '=', menu_id)
        ], limit=1)
        if not authority:
            authority = self.env['sub.menu.authority'].create({
                'authority_id': self.id,
                'menu_id': menu_id,
            })
        res = {
            'openerphk_write': authority.openerphk_write,
            'openerphk_create': authority.openerphk_create,
            'openerphk_delete': authority.openerphk_delete,
            'openerphk_export': authority.openerphk_export,
        }
        return res

    def get_click_menu_authority_app(self, menu_id):
        """
        获取点击菜单权限
        参数resId, menuId
        :return:{
            'openerphk_write': authority.openerphk_write,
            'openerphk_create': authority.openerphk_create,
            'openerphk_delete': authority.openerphk_delete,
            'openerphk_export': authority.openerphk_export,
        }
        """
        authority = self.env['app.menu.authority'].search([
            ('authority_id', '=', self.id), ('menu_id', '=', menu_id)
        ], limit=1)
        if not authority:
            authority = self.env['app.menu.authority'].create({
                'authority_id': self.id,
                'menu_id': menu_id,
            })
        res = {
            'openerphk_write': authority.openerphk_write,
            'openerphk_create': authority.openerphk_create,
            'openerphk_delete': authority.openerphk_delete,
            'openerphk_export': authority.openerphk_export,
        }
        return res

    def update_sub_authority(self, menu_id, write_data=False):
        """
        更新菜单子权限
        参数resId, menuId， write_data
        :return: boolean
        """
        authority = self.env['sub.menu.authority'].search([
            ('authority_id', '=', self.id), ('menu_id', '=', menu_id)
        ])
        if authority and write_data:
            authority.write(write_data)
            self.env.cr.commit()
            return True
        else:
            return False

    def update_authority_app(self, menu_id, mode):
        if mode=="add":
            self.app_menu_ids = [(4, menu_id)]
        elif mode=="delete":
            self.app_menu_ids = [(3, menu_id)]

    def update_sub_authority_app(self, menu_id, write_data=False):
        """
        更新菜单子权限
        参数resId, menuId， write_data
        :return: boolean
        """
        authority = self.env['app.menu.authority'].search([
            ('authority_id', '=', self.id), ('menu_id', '=', menu_id)
        ])
        if authority and write_data:
            authority.write(write_data)
            self.env.cr.commit()
            return True
        else:
            return False

    def get_users_menu(self):
        """
        用户获取权限菜单
        :return:
        """

        def is_subarray(arr1, arr2):
            for a1 in arr1:
                if a1 not in arr2:
                    return False
            return True
        menu_tree = self.get_menu_tree(with_user=True)
        hide = [item['id'] for item in menu_tree['authority_menu']]
        root_hide = []
        for item in menu_tree['all_menu']:
            if is_subarray(item['children'], hide):
                root_hide.append(item['id'])
        root = [item['id'] for item in menu_tree['all_menu']]
        root = [item for item in root if item not in root_hide]
        res = {
            "root": root,
            "hide": hide
        }
        if menu_tree['app_mix']:
            res.update({
                "app": menu_tree['app_mix']
            })
        return res


    def get_model_access(self, uid, model_name, tree):
        """
        获取用户对应菜单模型的权限
        :return:
        """
        records = self.search([('user_ids.id', '=', uid)])

        # 若没有视图动作，则直接返回
        if not self.env.context.get('openerphk_action_id') or self.env.uid == 2:
            return {
                'flag': 'pass'
            }

        _openerphk_write = False
        _openerphk_create = False
        _openerphk_delete = False
        _openerphk_export = False
        if not records:
            return {
                'flag': 'edit',
                'openerphk_write': False,
                'openerphk_create': False,
                'openerphk_delete': False,
                'openerphk_export': False,
            }
        for record in records:
            menuitems = self.env['ir.model.data'].sudo().search([
                ('res_id', 'in', record.menu_ids.ids),
                ('model', '=', 'ir.ui.menu')
            ])
            for menu in menuitems:
                action = self.env.ref(menu.complete_name).sudo().action
                if action.id == self.env.context.get('openerphk_action_id') and action.res_model == model_name:
                    _res = record.get_click_menu_authority(menu.res_id)
                    if _res['openerphk_write']:
                        _openerphk_write = True
                    if _res['openerphk_create']:
                        _openerphk_create = True
                    if _res['openerphk_delete']:
                        _openerphk_delete = True
                    if _res['openerphk_export']:
                        _openerphk_export = True
        res = {
            'flag': 'edit',
            'openerphk_write': _openerphk_write,
            'openerphk_create': _openerphk_create,
            'openerphk_delete': _openerphk_delete,
            'openerphk_export': _openerphk_export,
        }
        return res


class SubMenuAuthority(models.Model):
    _name = 'sub.menu.authority'

    menu_id = fields.Many2one('ir.ui.menu')
    authority_id = fields.Many2one('openerphk.authority')
    openerphk_write = fields.Boolean('edit', default=True)
    openerphk_create = fields.Boolean('create', default=True)
    openerphk_delete = fields.Boolean('delete', default=True)
    openerphk_export = fields.Boolean('export', default=True)


class APPMenu(models.Model):
    _name = 'app.menu'

    name = fields.Char('menu name')
    parent_id = fields.Many2one('app.menu')
    child_ids = fields.One2many('app.menu', 'parent_id')


class APPMenuAuthority(models.Model):
    _name = 'app.menu.authority'

    menu_id = fields.Many2one('app.menu')
    authority_id = fields.Many2one('openerphk.authority')
    openerphk_write = fields.Boolean('edit', default=True)
    openerphk_create = fields.Boolean('create', default=True)
    openerphk_delete = fields.Boolean('delete', default=True)
    openerphk_export = fields.Boolean('export', default=True)




class ViewExt(models.Model):
    _inherit = 'ir.ui.view'

    def _postprocess_access_rights(self, tree):
        """
        Apply group restrictions: elements with a 'groups' attribute should
        be removed from the view to people who are not members.

        Compute and set on node access rights based on view type. Specific
        views can add additional specific rights like creating columns for
        many2one-based grouping views.
        """
        # print('调用')
        access = self.env['openerphk.authority'].get_model_access(self.env.uid, tree.get('model_access_rights'), tree)
        # print(access)
        if access.get('flag') == 'edit':
            openerphk_create = '1' if access['openerphk_create'] else '0'
            openerphk_export = '1' if access['openerphk_export'] else '0'
            openerphk_delete = '1' if access['openerphk_delete'] else '0'
            openerphk_write = '1' if access['openerphk_write'] else '0'
            # 如果增删改在视图上本来就设置为0的，则不改。
            if tree.get('create') != '0':
                tree.set('create', openerphk_create)
            tree.set('export_xlsx', openerphk_export)
            if tree.get('delete') != '0':
                tree.set('delete', openerphk_delete)
            if tree.get('edit') != '0':
                tree.set('edit', openerphk_write)
            for node in tree.xpath('//button[@string="新增"]'):
                node.set('invisible', f'0 == {openerphk_create}')
            for node in tree.xpath('//button[@string="编辑"]'):
                node.set('invisible', f'0 == {openerphk_write}')
            for node in tree.xpath('//button[@string="导出"]'):
                node.set('invisible', f'0 == {openerphk_export}')
        tree = super()._postprocess_access_rights(tree)
        return tree


class Model(models.AbstractModel):
    _inherit = 'base'

    _date_name = 'date'

    @api.model
    def get_view(self, view_id=None, view_type='form', **options):
        result = super(Model, self.with_context(openerphk_action_id=options.get('action_id'))).get_view(view_id, view_type, **options)
        return result