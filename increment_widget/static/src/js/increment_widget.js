/** @odoo-module **/

import { Component, useState, onMounted, onWillUnmount } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
export class NumberField extends Component {
    static template = "web.IncrementWidget";  // 指定模板
    static props = {
        ...standardFieldProps,  // 引入标准字段属性
    };

    // 用于存储当前递增的数值
    setup() {
        // 初始化 displayValue 为 0
        this.state = useState({
            displayValue: 0,
        });

        // 定时器 ID，用于清除定时器
        this.intervalId = null;

        // 在组件挂载时启动递增动画
        onMounted(() => {
            const targetValue = this.props.record.data[this.props.name] || 0; // 获取目标值，默认为0

            // 通过 setInterval 实现平滑递增
            this.intervalId = setInterval(() => {
                if (this.state.displayValue < targetValue) {
                    this.state.displayValue += 1;  // Increment by 1 (adjust as needed)
                } else {
                    clearInterval(this.intervalId);  // 达到目标值时清除定时器
                }
            }, 30);  // 设置递增的间隔时间（30ms）
        });

        // 在组件卸载时清除定时器，防止内存泄漏
        onWillUnmount(() => {
            if (this.intervalId) {
                clearInterval(this.intervalId);
            }
        });
    }

    // 获取当前的递增数值
    get displayValue() {
        return this.state.displayValue;
    }
}

export const numberField = {
    component: NumberField,
    supportedTypes: ["integer", "float"],  // 支持的字段类型：整数和浮动数字
    extractProps(fieldInfo, dynamicInfo) {
        return {
            readonly: dynamicInfo.readonly,  // 提取只读属性
        };
    },
};

registry.category("fields").add("IncrementWidget", numberField);  // 注册为数值字段
