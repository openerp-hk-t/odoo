/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
export class NumberField extends Component {
    static template = "web.ThresholdWidget";  // 使用模板
    static props = {
        ...standardFieldProps,  // 引入标准字段属性
        threshold: { type: Number, optional: true },  // 阈值属性
    };

    setup() {
        this.state = useState({
            displayValue: this.props.record.data[this.props.name] || 0,
        });
    }

    // 返回展示的数值，保留两位小数
    get displayValue() {
        return this.state.displayValue.toFixed(2);
    }

    // 判断当前数值是否大于阈值
    get isOverThreshold() {
        return this.props.threshold && this.state.displayValue > this.props.threshold;
    }

    // 根据值是否超过阈值设置颜色
    get color() {
        return this.isOverThreshold ? "red" : "green";  // 超过阈值显示红色，否则显示绿色
    }
}

export const numberField = {
    component: NumberField,
    supportedTypes: ["integer", "float"],  // 支持的字段类型：整数和浮动数字
    extractProps(fieldInfo, dynamicInfo) {
        return {
            readonly: dynamicInfo.readonly,  // 提取只读属性
            threshold: fieldInfo.options?.threshold ? parseFloat(fieldInfo.options.threshold) : undefined,
        };
    },
};

// 注册该组件为自定义的字段类型
registry.category("fields").add("ThresholdWidget", numberField);
