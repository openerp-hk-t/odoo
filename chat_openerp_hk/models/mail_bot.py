from markupsafe import Markup
import requests
from odoo import api,fields,models,exceptions
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatOpenAI
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import logging


_logger = logging.getLogger(__name__)


class MailBot(models.AbstractModel):
    _inherit = 'mail.bot'


    def _get_answer(self, record, body, values, command):
        user_lang = self.env.user.lang  # 获取用户语言
        type = self.detect_type_and_prompt_user(record,user_lang,body)
        print(type)
        if type == 'query database':
            result = self.send_data_to_api(body)
            print(result)
            sql = result['sql']
            if sql == 'None':
                if user_lang == 'zh_CN':
                    return '未获取到sql'
                else:
                    return 'SQL not obtained'
            else:
                out_llm_id = self.env['llm.config'].sudo().search([('is_out_default', '=', True)])
                if not out_llm_id:
                    return '没有找到默认优化模型，请检查模型配置'
                prompt_id = self.env['prompt.config'].sudo().search([('default_prompt','=',True)])
                prompt_system = f"""{prompt_id.system}

                            {prompt_id.output_format}"""
                prompt_system += """问题：{question}"""
                prompt = [
                    ('system', f"""{prompt_system}
                                            """
                     )
                ]
                out_chain = self.out_langchain(out_llm_id,prompt)
                query_result = self.execute_sql_query(sql)
                if query_result is None:
                    if user_lang == 'zh_CN':
                        return Markup(f"未查询到相关内容")
                    else:
                        return Markup(f"No relevant content found")

                else:
                    # result = self.generate_product_html(query_result)
                    result = out_chain.invoke({
                        'question': f'用户提出的问题是{body}，数据库查询的数据是{query_result}，你需要通过用户提出的问题和数据库查出的数据帮我整理返回最终的数据，只需要结果不需要你的分析过程，最终把数据的名称和值提取在每一行列出来再做一个总结，返回的数据是要放到div标签中的'})
                    return Markup(f"{result.content}")
        elif type == 'normal chat':
            chat_llm_id = self.env['llm.config'].sudo().search([('is_chat_default', '=', True)])
            if not chat_llm_id:
                return '没有找到默认聊天模型，请检查模型配置'
            chain = self.chat_langchain(chat_llm_id)
            return Markup(f"{chain.invoke(body).content}")
        else:
            return Markup(f"{type}")

    def generate_product_html(self,data):
        html = ['<div class="data-container">']

        for item in data:
            html.append('<div class="item">')

            # 标题显示：尝试识别 en_US 和 zh_CN 格式
            name = item.get('product_name', {})
            if isinstance(name, dict) and 'en_US' in name and 'zh_CN' in name:
                html.append(f'<h3>info: {name["en_US"]} ({name["zh_CN"]})</h3>')
            else:
                html.append('<h3>info</h3>')

            html.append('<ul>')
            for key, value in item.items():
                # 如果是字典类型，尝试展开
                if isinstance(value, dict):
                    html.append(f'<li>{key}:')
                    html.append('<ul>')
                    for sub_key, sub_val in value.items():
                        html.append(f'<li>{sub_key}: {sub_val}</li>')
                    html.append('</ul></li>')
                else:
                    html.append(f'<li>{key}: {value}</li>')
            html.append('</ul>')
            html.append('</div>')

        html.append('</div>')

        # 合并成 HTML 字符串
        html_output = '\n'.join(html)

        return html_output

    def send_data_to_api(self,question):
        config_params = self.env['ir.config_parameter'].sudo()
        IP = config_params.get_param('chat_openerp_hk.IP')
        if not IP:
            raise exceptions.UserError('未设置接口地址')
        # 要发送的数据
        params = {
            "question": f'{question}'
        }

        # 目标接口地址
        url = f"{IP}/chat_openerp_hk/answer"

        try:
            # 发送 POST 请求
            response = requests.post(url, params=params)

            # 检查响应状态码
            if response.status_code == 200:
                return response.json()
            else:
                return {"status": "error", "code": response.status_code, "text": response.text}
        except Exception as e:
            return {"status": "exception", "error": str(e)}

    def execute_sql_query(self, query):
        """
        默认查询当前数据库并执行 SQL 语句，自动处理事务异常和结构化结果。
        """

        parsed_result = []

        try:
            # 使用 savepoint 以便 SQL 出错后不影响整个事务
            with self.env.cr.savepoint():
                self.env.cr.execute(query)

                # 获取查询结果和字段名
                result = self.env.cr.fetchall()
                colnames = [desc[0] for desc in self.env.cr.description]

                # 处理结构化结果
                for row in result:
                    row_dict = dict(zip(colnames, row))

                    # 多语言字段展示
                    if 'en_US' in row_dict:
                        row_dict['en_US_name'] = row_dict['en_US']
                    if 'zh_CN' in row_dict:
                        row_dict['zh_CN_name'] = row_dict['zh_CN']

                    parsed_result.append(row_dict)

        except Exception as e:
            # 打印错误并回滚事务（保险起见也 rollback 一次）
            # self.env.cr.rollback()
            _logger.exception("执行 SQL 查询失败: %s", e)
            return None

        return parsed_result

    # 优化模型
    def out_langchain(self,out_llm_id,prompt):
        # 使用 OpenAI 或其他 LLM
        llm = ChatOpenAI(
            openai_api_base=out_llm_id.model_URL,  # LM Studio API 地址
            openai_api_key="12",  # 随便填一个（LM Studio 不验证）
            model=out_llm_id.model,  # 确保与 LM Studio 里运行的模型名称匹配
            temperature=out_llm_id.temperature
        )
        prompt = ChatPromptTemplate.from_messages(prompt)
        chain = prompt | llm
        return chain

    def chat_langchain(self,chat_llm_id):
        # 使用 OpenAI 或其他 LLM
        llm = ChatOpenAI(
            openai_api_base=chat_llm_id.model_URL,  # LM Studio API 地址
            openai_api_key="12",  # 随便填一个（LM Studio 不验证）
            model=chat_llm_id.model,  # 确保与 LM Studio 里运行的模型名称匹配
            temperature=chat_llm_id.temperature
        )
        # prompt = ChatPromptTemplate.from_messages(eval(chat_llm_id.prompt))
        chain = llm
        return chain

    def get_prompt_template(self, question):
        # 获取提示模板
        template_id = self.env['prompt.config'].search([('default_prompt','=',True)])
        if not template_id:
            templates = self.env['prompt.config'].search([])
            # 提取模板的名称和任务目标
            template_names = [t.name for t in templates]
            template_objectives = [t.task_objective for t in templates]

            # 使用预训练的 sentence transformer 模型进行向量化
            model = SentenceTransformer('all-MiniLM-L6-v2')

            # 所有模板的 task_objective 向量化
            template_vectors = model.encode(template_objectives, normalize_embeddings=True)

            # 用户输入的问题
            user_question = question  # 传入的用户问题
            user_vector = model.encode([user_question], normalize_embeddings=True)

            # 计算用户问题与模板任务目标之间的相似度
            sims = cosine_similarity(user_vector, template_vectors)[0]

            # 获取最相似的模板的索引
            best_index = int(np.argmax(sims))

            # 获取最匹配的模板
            template_id = templates[best_index]

        # 拼接完整的 prompt
        full_prompt = f"""
           角色定义: {template_id.role_definition}

           任务目标: {template_id.task_objective}

           计算步骤: {template_id.computational_procedure if template_id.computational_procedure else '无'}

           整理格式: {template_id.output_format}

           用户问题: {question}
           """
        print('提示词模板',full_prompt)
        return full_prompt

    def detect_type_and_prompt_user(self, record,lang, body):
        """ 检测模型的类型，并根据用户语言发送选择模式的消息 """

        # 检测当前模型的 type 是否是 'None'
        if record.type == 'None':
            # 获取用户的语言

            # 根据用户的语言发送不同的消息
            if lang == 'zh_CN':
                message = "当前模式为 '无'，请选择一个模式：\n1. 查询数据库\n2. 普通聊天"
            else:
                message = "The current mode is 'None'. Please choose a mode:\n1. Query Database\n2. Normal Chat"
            if '1' in body or '数据库' in body:
                # 设置模式为查询数据库
                record.write({'type': 'query database'})
                if lang == 'zh_CN':
                    return "你已选择查询数据库模式。"
                else:
                    return "You have selected Query Database mode."
            elif '2' in body or '聊天' in body:
                # 设置模式为普通聊天
                record.write({'type': 'normal chat'})
                if lang == 'zh_CN':
                    return "你已选择普通聊天模式。"
                else:
                    return "You have selected Normal Chat mode."
            # 发送消息给用户
            return message
        else:
            if '1' in body or '数据库' in body:
                # 设置模式为查询数据库
                record.write({'type': 'query database'})
                if lang == 'zh_CN':
                    return "你已选择查询数据库模式。"
                else:
                    return "You have selected Query Database mode."
            elif '2' in body or '聊天' in body:
                # 设置模式为普通聊天
                record.write({'type': 'normal chat'})
                if lang == 'zh_CN':
                    return "你已选择普通聊天模式。"
                else:
                    return "You have selected Normal Chat mode."
            return record.type


class ChatDiscussChannel(models.Model):
    _inherit = 'discuss.channel'

    type = fields.Selection([('None','无'),('query database','查询数据库'),('normal chat','普通聊天')],string='模式',default='None')

    def _reset_type_to_none(self):
        self.write({'type': 'None'})