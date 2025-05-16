/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { FileInput } from "@web/core/file_input/file_input";
import { useX2ManyCrud } from "@web/views/fields/relational_utils";

import { Component, useRef, useState, onWillStart, onRendered } from "@odoo/owl";

export class ZTREEMany2ManyField extends Component {
    static template = "openerphk_authority.ZTREEMany2ManyField";
//    static components = {
//        FileInput,
//    };
    static props = {
        ...standardFieldProps,
        acceptedFileExtensions: { type: String, optional: true },
        className: { type: String, optional: true },
        numberOfFiles: { type: Number, optional: true },
    };

    setup() {
        super.setup();
        let self = this;
        let isInit = false;
        this.orm = useService("orm");
//        this.menuService = useService("menu");
//        this.allMenu = this.menuService.getAll();
        this.move_right = useRef('move_right');
        this.move_right_app = useRef('move_right_app');
        this.sub_authority_warp = useRef('sub_authority_warp');
        this.sub_authority_warp_app = useRef('sub_authority_warp_app');
        this.notification = useService("notification");
        this.operations = useX2ManyCrud(() => this.props.record.data[this.props.name], true);
        this.allMenuTree = []
        this.authorityMenuTree = []
        this.appMenuTree = []
        this.appAuthorityMenuTree = []
        this.tempAuth = {
            hide: true,
            authority_data: {
                openerphk_write: true,
                openerphk_create: true,
                openerphk_delete: true,
                openerphk_export: true,
            }
        }
        this.state = useState({
            moveAction: this.moveAction,
            allMenuSetting: this.allMenuSetting,
            authorityMenuSetting: this.authorityMenuSetting,
            appMenuTree: this.appMenuTree,
            appAuthorityMenuTree: this.appAuthorityMenuTree,
        });

        onWillStart(async () => {
            await this.getCurrentTreeData();
        });

        onRendered(async () => {
            if(!self.isInit){
                setTimeout(() => {
                  $(document).ready(function(){
                        $.fn.zTree.init($("#AllMenutree"), self.state.allMenuSetting, self.state.allMenuTree);
                        let authorityMenutree = $.fn.zTree.init($("#authorityMenutree"), self.state.authorityMenuSetting, self.state.authorityMenuTree);
                        authorityMenutree.expandAll(true);
                        $.fn.zTree.init($("#AllMenutree_app"), self.state.allMenuSetting, self.state.appMenuTree);
                        $.fn.zTree.init($("#authorityMenutree_app"), self.state.authorityMenuSetting, self.state.appAuthorityMenuTree);
                    });
                }, 500);
            }
            self.isInit = true;
        });
    }

    async getCurrentTreeData() {
        const res = await this.orm.call(this.props.record.resModel, "get_menu_tree", [this.props.record.resId]);
        this.state.allMenuTree = res['all_menu'];
        this.state.authorityMenuTree = res['authority_menu'];
        this.state.appMenuTree = res['all_app_menu'];
        this.state.appAuthorityMenuTree = res['authority_app_menu'];
    }

    async getClickMenuAuthority(menuId) {
        const res = await this.orm.call(
        this.props.record.resModel,
        "get_click_menu_authority",
        [this.props.record.resId, menuId]
        );
        return res;
    }

    async getClickMenuAuthorityApp(menuId) {
        const res = await this.orm.call(
        this.props.record.resModel,
        "get_click_menu_authority_app",
        [this.props.record.resId, menuId]
        );
        return res;
    }

//    切换选择框状态
    toggleCheckbox(e) {
        e.preventDefault();
        e.stopPropagation();
        let $span = $(e.target);
        if($span.attr('id') == undefined){
            $span = $(e.target).find('span');
        }
        $span.toggleClass(
            'checkbox-custom-clicked',
            !$span.hasClass('checkbox-custom-clicked')
        );
        $span.attr('value', !($span.attr('value') == "true"));
    }

//    更新菜单子权限：增删改导出
    async onAuthorityClicked(e) {
        e.preventDefault();
        e.stopPropagation();
        let $sub_authority_warp = $(this.sub_authority_warp.el);
        let menuId = $sub_authority_warp.attr("menuId");
        let $span = $(e.target);
        if($span.attr('id') == undefined){
            $span = $(e.target).find('span');
        }
        this.toggleCheckbox(e);
        let write_data = {
        }
        let key = $span.attr('id')
        write_data[$span.attr('id')] = ($span.attr('value')=="true")
        const res = await this.orm.call(
            this.props.record.resModel,
            "update_sub_authority",
            [this.props.record.resId, parseInt(menuId), write_data]
        );
        if(res){
            this.notification.add("更新当前权限成功。", { type: "success" });
        }else{
            this.toggleCheckbox(e);
            this.notification.add("无法更新当前权限，请刷新页面重试。", { type: "danger" });
        }
    }

//    更新app菜单子权限：增删改导出
    async onAppAuthorityClicked(e) {
        function removeSuffix(str, suffix) {
            if (str.endsWith(suffix)) {
                return str.substring(0, str.length - suffix.length);
            }
            return str;
        }
        let $sub_authority_warp = $(this.sub_authority_warp_app.el);
        let menuId = $sub_authority_warp.attr("menuId");
        let $span = $(e.target);
        if($span.attr('id') == undefined){
            $span = $(e.target).find('span');
        }
        this.toggleCheckbox(e);
        let write_data = {
        }
        let key = removeSuffix($span.attr('id'), "_app");
        write_data[key] = ($span.attr('value')=="true")
        const res = await this.orm.call(
            this.props.record.resModel,
            "update_sub_authority_app",
            [this.props.record.resId, parseInt(menuId), write_data]
        );
        if(res){
            this.notification.add("更新当前权限成功。", { type: "success" });
        }else{
            this.toggleCheckbox(e);
            this.notification.add("无法更新当前权限，请刷新页面重试。", { type: "danger" });
        }
    }

    async onCellKeydown(e, aa){
        if(e.keyCode == 13){
            let zTree = $.fn.zTree.getZTreeObj("AllMenutree");
            let value = $(e.target).val();
            let nodes = zTree.getNodesByParamFuzzy("name", value, null);
        　　 for(var i = nodes.length-1; i >= 0; i--) {
                zTree.selectNode(nodes[i]);
            }
        }
    }

    convertToZNodes(menus) {
        const zNodes = [];

        // 创建一个映射以便快速查找菜单项
        const menuMap = {};
        menus.forEach(menu => {
            menuMap[menu.id] = { id: menu.id, name: menu.name, pId: 0 }; // 初始化每个菜单项
        });

        // 遍历 menus 数组，构建 zNodes
        menus.forEach(menu => {
            // 如果有 children，设置 pId
            if (menu.children && menu.children.length > 0) {
                menu.children.forEach(childId => {
                    if (menuMap[childId]) {
                        // 设置子节点的 pId 为当前菜单的 id
                        menuMap[childId].pId = menu.id;
                    }
                });
            }
        });

        // 将根节点（pId 为 0）添加到 zNodes
        for (const id in menuMap) {
            if (menuMap[id].pId === 0) {
                menuMap[id]['open'] = true;
                zNodes.push(menuMap[id]);
            } else {
                zNodes.push(menuMap[id]); // 添加子节点
            }
        }

        return zNodes;
    }

    get moveAction() {
        let self = this;
        return {
            dragTree2Dom: function(treeId, treeNodes) {
                return !treeNodes[0].isParent;
            },
            prevTree: function(treeId, treeNodes, targetNode) {
                return !targetNode.isParent && targetNode.parentTId == treeNodes[0].parentTId;
            },
            nextTree: function(treeId, treeNodes, targetNode) {
                return !targetNode.isParent && targetNode.parentTId == treeNodes[0].parentTId;
            },
            innerTree: function(treeId, treeNodes, targetNode) {
                return targetNode!=null && targetNode.isParent && targetNode.tId == treeNodes[0].parentTId;
            },
            dragMove: function(e, treeId, treeNodes) {
                return;
            },
            dropTree2Dom: function(e, treeId, treeNodes, targetNode, moveType) {
                e.preventDefault(); // 阻止默认行为
                e.stopPropagation(); // 阻止事件传播

                if ( treeId == 'AllMenutree' && $(e.target).parents("#authorityMenutree").length > 0) {
                    let parentNode = treeNodes[0].getParentNode();
                    let zTree = $.fn.zTree.getZTreeObj("authorityMenutree");
                    let newParentNode = zTree.getNodeByParam('id', parentNode.id)
                    let newCurrentNode = zTree.getNodeByParam('id', treeNodes[0].id)
                    if(!!newCurrentNode){
                        zTree.selectNode(newCurrentNode);
                        return;
                    }
                    self.saveRecord(treeNodes[0].id);
                    let nodes = zTree.addNodes(newParentNode, {id:treeNodes[0].id, name: treeNodes[0].name});
                    zTree.selectNode(nodes[0]);
                    self.state.moveAction.updateType();
                }else if( treeId == 'AllMenutree_app' && $(e.target).parents("#authorityMenutree_app").length > 0){
                    let parentNode = treeNodes[0].getParentNode();
                    let zTree = $.fn.zTree.getZTreeObj("authorityMenutree_app");
                    let newParentNode = zTree.getNodeByParam('id', parentNode.id)
                    let newCurrentNode = zTree.getNodeByParam('id', treeNodes[0].id)
                    if(!!newCurrentNode){
                        zTree.selectNode(newCurrentNode);
                        return;
                    }
                    self.saveAppRecord(treeNodes[0].id);
                    let nodes = zTree.addNodes(newParentNode, {id:treeNodes[0].id, name: treeNodes[0].name});
                    zTree.selectNode(nodes[0]);
                }else{
                    return;
                }
            },
            authorityTree2Dom: function(e, treeId, treeNodes, targetNode, moveType) {
                e.preventDefault(); // 阻止默认行为
                e.stopPropagation(); // 阻止事件传播

                if ( treeId == 'authorityMenutree' ) {
                    var zTree = $.fn.zTree.getZTreeObj("authorityMenutree");
                    self.removeRecord(treeNodes[0].id);
                    zTree.removeNode(treeNodes[0]);
                    self.state.moveAction.updateType();
                }else if( treeId == 'authorityMenutree_app' ){
                    var zTree = $.fn.zTree.getZTreeObj("authorityMenutree_app");
                    self.removeAppRecord(treeNodes[0].id);
                    zTree.removeNode(treeNodes[0]);
                }
            },
            dom2Tree: function(e, treeId, treeNode) {
                return;
            },
            treeClick: async function(e, treeId, treeNode, clickFlag) {
                if ( treeId == 'authorityMenutree' ) {
                    let $move_right = $(self.move_right.el);
                    let $sub_authority_warp = $(self.sub_authority_warp.el);
                    let openerphk_write = $sub_authority_warp.find("[id='openerphk_write']")
                    let openerphk_create = $sub_authority_warp.find("[id='openerphk_create']")
                    let openerphk_delete = $sub_authority_warp.find("[id='openerphk_delete']")
                    let openerphk_export = $sub_authority_warp.find("[id='openerphk_export']")
                    let openerphk_menu_name = $sub_authority_warp.find("[id='openerphk_menu_name']")
                    let cls = 'checkbox-custom-clicked'
                    if(!treeNode.isParent){
                        openerphk_menu_name.text(treeNode.name);
                        $sub_authority_warp.attr("menuId", treeNode.id);
                        $move_right.removeClass('o_hidden');
                        $sub_authority_warp.removeClass('o_hidden');
                        let res = await self.getClickMenuAuthority(treeNode.id);
                        res.openerphk_write?openerphk_write.addClass(cls).attr('value', res.openerphk_write):openerphk_write.removeClass(cls).attr('value', res.openerphk_write);
                        res.openerphk_create?openerphk_create.addClass(cls).attr('value', res.openerphk_create):openerphk_create.removeClass(cls).attr('value', res.openerphk_create);
                        res.openerphk_delete?openerphk_delete.addClass(cls).attr('value', res.openerphk_delete):openerphk_delete.removeClass(cls).attr('value', res.openerphk_delete);
                        res.openerphk_export?openerphk_export.addClass(cls).attr('value', res.openerphk_export):openerphk_export.removeClass(cls).attr('value', res.openerphk_export);
                    }else{
                        $sub_authority_warp.attr("menuId", 0);
                        $move_right.addClass('o_hidden');
                        $sub_authority_warp.addClass('o_hidden');
                    }
                }else if ( treeId == 'authorityMenutree_app' ){
                    let $move_right = $(self.move_right_app.el);
                    let $sub_authority_warp = $(self.sub_authority_warp_app.el);
                    let openerphk_write = $sub_authority_warp.find("[id='openerphk_write_app']")
                    let openerphk_create = $sub_authority_warp.find("[id='openerphk_create_app']")
                    let openerphk_delete = $sub_authority_warp.find("[id='openerphk_delete_app']")
                    let openerphk_export = $sub_authority_warp.find("[id='openerphk_export_app']")
                    let openerphk_menu_name = $sub_authority_warp.find("[id='openerphk_menu_name_app']")
                    let cls = 'checkbox-custom-clicked'
                    if(!treeNode.isParent){
                        openerphk_menu_name.text(treeNode.name);
                        $sub_authority_warp.attr("menuId", treeNode.id);
                        $move_right.removeClass('o_hidden');
                        $sub_authority_warp.removeClass('o_hidden');
                        let res = await self.getClickMenuAuthorityApp(treeNode.id);
                        res.openerphk_write?openerphk_write.addClass(cls).attr('value', res.openerphk_write):openerphk_write.removeClass(cls).attr('value', res.openerphk_write);
                        res.openerphk_create?openerphk_create.addClass(cls).attr('value', res.openerphk_create):openerphk_create.removeClass(cls).attr('value', res.openerphk_create);
                        res.openerphk_delete?openerphk_delete.addClass(cls).attr('value', res.openerphk_delete):openerphk_delete.removeClass(cls).attr('value', res.openerphk_delete);
                        res.openerphk_export?openerphk_export.addClass(cls).attr('value', res.openerphk_export):openerphk_export.removeClass(cls).attr('value', res.openerphk_export);
                    }else{
                        $sub_authority_warp.attr("menuId", 0);
                        $move_right.addClass('o_hidden');
                        $sub_authority_warp.addClass('o_hidden');
                    }
                }
            },
            updateType: function() {
                var zTree = $.fn.zTree.getZTreeObj("authorityMenutree"),
                nodes = zTree.getNodes();
                for (var i=0, l=nodes.length; i<l; i++) {
                    var num = nodes[i].children ? nodes[i].children.length : 0;
                    nodes[i].name = nodes[i].name.replace(/ \(.*\)/gi, "") + " (" + num + ")";
                    zTree.updateNode(nodes[i]);
                }
            },
        }
    }

    get allMenuSetting() {
        return {
            edit: {
                enable: true,
                showRemoveBtn: false,
                showRenameBtn: false,
                drag: {
                    prev: this.moveAction.prevTree,
                    next: this.moveAction.nextTree,
                    inner: this.moveAction.innerTree
                }
            },
            data: {
                keep: {
                    parent: true,
                    leaf: true
                },
                simpleData: {
                    enable: true
                }
            },
            callback: {
                beforeDrag: this.moveAction.dragTree2Dom,
                onDrop: this.moveAction.dropTree2Dom,
                onDragMove: this.moveAction.dragMove,
                onMouseUp: this.moveAction.dom2Tree
            },
            view: {
                selectedMulti: false
            }
        };
    }

    get authorityMenuSetting() {
        return {
            edit: {
                enable: true,
                showRemoveBtn: false,
                showRenameBtn: false,
                drag: {
                    prev: this.moveAction.prevTree,
                    next: this.moveAction.nextTree,
                    inner: this.moveAction.innerTree
                }
            },
            data: {
                keep: {
                    parent: true,
                    leaf: true
                },
                simpleData: {
                    enable: true
                }
            },
            callback: {
                beforeDrag: this.moveAction.dragTree2Dom,
                onDrop: this.moveAction.authorityTree2Dom,
                onDragMove: this.moveAction.dragMove,
                onClick: this.moveAction.treeClick
            },
            view: {
                selectedMulti: false
            }
        };
    }

    get value() {
        return this.props.record.data[this.props.name];
    }

    async saveRecord(id) {
        await this.operations.saveRecord([id]);
    }

    async saveAppRecord(id) {
        await this.orm.call(
            this.props.record.resModel,
            "update_authority_app",
            [this.props.record.resId, id, "add"]
        );
    }

    async removeRecord(deleteId) {
        const record = this.props.record.data[this.props.name].records.find(
            (record) => record.resId === deleteId
        );
        this.operations.removeRecord(record);
    }

    async removeAppRecord(deleteId) {
        await this.orm.call(
            this.props.record.resModel,
            "update_authority_app",
            [this.props.record.resId, deleteId, "delete"]
        );
    }
}

export const zTreeMany2ManyField = {
    component: ZTREEMany2ManyField,
    supportedOptions: [
        {
            label: _t("Accepted file extensions"),
            name: "accepted_file_extensions",
            type: "string",
        },
        {
            label: _t("Number of files"),
            name: "number_of_files",
            type: "integer",
        },
    ],
    supportedTypes: ["many2many"],
    isEmpty: () => false,
    relatedFields: [
        { name: "name", type: "char" },
    ],
    extractProps: ({ attrs, options }) => ({
        acceptedFileExtensions: options.accepted_file_extensions,
        className: attrs.class,
        numberOfFiles: options.number_of_files,
    }),
};

registry.category("fields").add("ztree_many2many", zTreeMany2ManyField);
