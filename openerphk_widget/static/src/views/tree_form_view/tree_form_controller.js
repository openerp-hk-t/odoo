/** @odoo-module */

import {ListController} from "@web/views/list/list_controller";
import {executeButtonCallback} from "@web/views/view_button/view_button_hook";
import { download } from "@web/core/network/download";


export class TreeFormController extends ListController {
    setup() {
        super.setup();
        this.isFormChange = false;
    }

    async onClickDiscard() {
        return executeButtonCallback(this.rootRef.el, async () => {
                this.isFormChange = false;
                await this.editedRecord.discard();
                await this.editedRecord.load();
                this.render();
            }
        );
    }

    async onClickSave() {
        if (!this.isFormChange)return ;
        return executeButtonCallback(this.rootRef.el, async () => {
            const saved = await this.editedRecord.save();
            if (saved) {
                await this.editedRecord.load();
                await this.model.load();
                this.isFormChange = false;
                this.render();
            }
        });
    }

    async openRecord(record) {
        this.editedRecord = record;
    }

    onFormChange(record, change) {
        this.isFormChange = true;
        this.render();
    }

    async onClickExport(e){

        await download({
            data: {
                data: JSON.stringify({
                    model: this.env.config.getDisplayName(),
                    resModel: this.props.resModel,
                    domain: this.env.searchModel.domain,
                    context: this.props.context
                }),
            },
            url: `/web/export/xls_view_tree_form`,
        });
    }
}

TreeFormController.template = 'openerphk_widget.TreeFormView';
