/** @odoo-module */

import {extractFieldsFromArchInfo} from "@web/model/relational_model/utils";
import {ListRenderer} from "@web/views/list/list_renderer";
import {FormRenderer} from "@web/views/form/form_renderer";
import {Record} from "@web/model/relational_model/record";
import {markRaw, onWillStart, useState} from "@odoo/owl";
import {useService} from "@web/core/utils/hooks";
import {parseXML} from "@web/core/utils/xml";
import {registry} from "@web/core/registry";

const viewRegistry = registry.category("views");


export class TreeFormRenderer extends ListRenderer {
    setup() {
        super.setup();
        this.formViewService = useService("view");
        this.treeFrom = useState({});
        this.numSwitch = true;
        onWillStart(async () => {
            const resModel = this.props.list.resModel;
            const {fields, relatedModels, views: {form: {arch}}} = await this.formViewService.loadViews({
                context: this.props.list.context,
                resModel,
                views: [[false, 'form']]
            }, {
                actionId: this.env.config.actionId,
            })
            const archXmlDoc = parseXML(arch);
            const viewProps = {
                arch: archXmlDoc,
                fields: fields,
                relatedModels: markRaw(relatedModels),
                resModel,
            }
            const view = viewRegistry.get('form');
            const {archInfo} = view.props(viewProps, view);
            const {activeFields} = extractFieldsFromArchInfo(
                archInfo,
                fields
            );
            Object.assign(this.treeFrom, {
                archInfo,
                fields,
                activeFields
            });
            if (this.props.list.count) {
                this.onCellClicked(this.props.list.records[0]);
            }
        })
    }

    onStartTreeFormReSize(ev) {
        const parent = ev.target.parentElement;
        const left = parent.querySelector('.tree-form-tree');
        const right = parent.querySelector('.tree-form-form');
        const initialX = ev.clientX;

        const leftWidth = left.getBoundingClientRect().width;
        const rightWidth = right.getBoundingClientRect().width;

        const leftTable = left.querySelector('.o_list_table');
        const leftThElements = leftTable?.querySelectorAll('thead th') || [];
        const leftTdElements = leftTable?.querySelectorAll('tbody td') || [];

        // 计算初始列宽比例
        const FIXED_WIDTHS = [40, 40];
        const fixedCols = [0, 1];
        const initialColumnWidths = Array.from(leftThElements).map(th => th.getBoundingClientRect().width);
        
        // 只计算非固定列的总宽度
        const totalVariableWidth = initialColumnWidths.reduce((sum, width, index) => 
            fixedCols.includes(index) ? sum : sum + width, 0);
            
        // 计算每列占可变宽度的比例（固定列设为0）
        const columnProportions = initialColumnWidths.map((width, index) => 
            fixedCols.includes(index) ? 0 : width / totalVariableWidth);

        const resizeStoppingEvents = ["keydown", "pointerdown", "pointerup"];

        const setColWidth = (ths, tds, totalWidth) => {
            // 计算固定列宽度总和
            const totalFixedWidth = FIXED_WIDTHS.reduce((a, b) => a + b, 0);
            // 计算可变列的可用宽度
            const variableWidth = totalWidth - totalFixedWidth;
            
            // 计算非固定列的总比例
            const totalVariableProportion = columnProportions.reduce((sum, prop, i) => 
                fixedCols.includes(i) ? sum : sum + prop, 0);

            ths.forEach((th, i) => {
                let w;
                if (fixedCols.includes(i)) {
                    w = FIXED_WIDTHS[fixedCols.indexOf(i)];
                } else {
                    // 根据该列在可变列中的比例分配宽度
                    w = Math.floor(variableWidth * (columnProportions[i] / totalVariableProportion));
                }
                th.style.width = `${w}px`;
                th.style.minWidth = `${w}px`;
                th.style.maxWidth = `${w}px`;
                th.style.overflow = "hidden";
                th.style.textOverflow = "ellipsis";
            });

            tds.forEach((td, i) => {
                const colIndex = i % ths.length;
                let w;
                if (fixedCols.includes(colIndex)) {
                    w = FIXED_WIDTHS[fixedCols.indexOf(colIndex)];
                } else {
                    w = Math.floor(variableWidth * (columnProportions[colIndex] / totalVariableProportion));
                }
                td.style.width = `${w}px`;
                td.style.minWidth = `${w}px`;
                td.style.maxWidth = `${w}px`;
                td.style.overflow = "hidden";
                td.style.textOverflow = "ellipsis";
            });
        };
        const startReSize = (ev) => {
            ev.preventDefault();
            ev.stopPropagation();

            const delta = ev.clientX - initialX;
            const leftNewWidth = Math.max(10, leftWidth + delta);
            const rightNewWidth = Math.max(10, rightWidth - delta);

            left.style.width = `${Math.floor(leftNewWidth)}px`;
            right.style.width = `${Math.floor(rightNewWidth)}px`;

            if (leftTable) {
                leftTable.style.width = `${Math.floor(leftNewWidth)}px`;
                setColWidth(Array.from(leftThElements), Array.from(leftTdElements), leftNewWidth);
            }
        };

        const stopReSize = (ev) => {
            if (ev.type === "pointerdown" && ev.button === 0) return;
            ev.preventDefault();
            ev.stopPropagation();

            window.removeEventListener("pointermove", startReSize);
            for (const eventType of resizeStoppingEvents) {
                window.removeEventListener(eventType, stopReSize);
            }

            /** 重新设置左栏列宽，保持原比例 **/
            if (leftTable && leftThElements.length > 0) {
                const newLeftWidth = left.getBoundingClientRect().width;
                leftTable.style.width = `${Math.floor(newLeftWidth)}px`;
                setColWidth(Array.from(leftThElements), Array.from(leftTdElements), newLeftWidth);
            }

            document.activeElement.blur();
        };

        window.addEventListener("pointermove", startReSize);
        for (const eventType of resizeStoppingEvents) {
            window.addEventListener(eventType, stopReSize);
        }
    }


    onRecordChanged(record, change) {
        this.props.onFormChange(record, change);
    }

    async onCellClicked(record, column, ev) {
        if(this.treeFrom.current_record) {
            this.props.onClickSave();
        }
        const records = await this.props.list.model._loadRecords(
            {
                resModel: this.props.list.resModel,
                resIds: [record.resId],
                activeFields: this.treeFrom.activeFields,
                fields: this.treeFrom.fields,
                context: this.props.list.context
            }
        );
        const model = this.props.list.model;
        model.hooks.onRecordChanged = this.onRecordChanged.bind(this);
        this.treeFrom.current_record = new Record(model, {
            ...this.props.list.model.config,
            mode: 'edit',
            isMonoRecord: true,
            resId: record.resId,
            resIds: [record.resId],
            resModel: this.props.list.resModel,
            activeFields: this.treeFrom.activeFields,
            fields: this.treeFrom.fields,
            context: this.props.list.context,
        }, records[0]);

        this.props.openRecord(this.treeFrom.current_record)
    }

    getRowClass(record) {
        let result = super.getRowClass(record);
        if (this.treeFrom.current_record && record.resId === this.treeFrom.current_record.resId) {
            result += ' active';
        }
        return result
    }
}

TreeFormRenderer.template = "openerphk_widget.TreeFormRenderer";
TreeFormRenderer.components = {
    ...ListRenderer.components,
    FormRenderer
}
TreeFormRenderer.props.push('onFormChange?');
TreeFormRenderer.props.push('onClickSave?');