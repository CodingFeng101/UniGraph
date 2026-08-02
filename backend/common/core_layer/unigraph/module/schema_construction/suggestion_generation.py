from pathlib import Path

from jinja2 import Template

from backend.common.core_layer.unigraph.ai_unit.llm.response_getter import GenericResponseGetter
from backend.common.core_layer.unigraph.module.schema_construction.utils import is_chinese_more_than_english


class SuggestionGeneration:
    def __init__(self, info, pre_suggestion):
        # self.client = OpenAI(
        #     api_key=llm_parameter.openai_api_key,
        #     base_url=llm_parameter.base_url,
        # )
        self.info = info
        self.pre_suggestion = pre_suggestion

    @staticmethod
    def load_prompt(filename: str) -> str:
        prompt_path = Path(__file__).resolve().parent / 'prompt' / filename
        return prompt_path.read_text(encoding='utf-8')

    async def chatresponse(self, prompt, api_key, base_url, model):
        server = GenericResponseGetter()
        response = await server.get_response(query=prompt, model=model, api_key=api_key, base_url=base_url)
        return response

    async def initial_generate_suggestion(
        self,
        api_key,
        base_url,
        model,
    ):
        if (self.info.get('add_entity') and self.info['add_entity']) or (
            self.info.get('del_entity') and self.info['del_entity']
        ):
            actual_modify_entity_string = ''
            if self.info.get('add_entity') and self.info['add_entity']:
                actual_modify_entity_string += (
                    f"User's expected entity category:{','.join(self.info['add_entity'])}    "
                )
            if self.info.get('del_entity') and self.info['del_entity']:
                actual_modify_entity_string += (
                    f'Entity categories that users do not need:{",".join(self.info["del_entity"])}'
                )
            all_entities = self.info['add_entity'] + self.info['del_entity']
            language = 'Chinese' if is_chinese_more_than_english(','.join(all_entities)) else 'English'
            need_modify_prompt = Template(self.load_prompt('suggestion_generation_agent.txt'))
            need_modify_prompt = need_modify_prompt.render(
                actual_modify_entity_string=actual_modify_entity_string, language=language
            )
            directional_suggestion = await self.chatresponse(need_modify_prompt, api_key, base_url, model)
            return directional_suggestion, self.info
        else:
            return '', self.info

    async def following_generate_suggestion(
        self,
        api_key,
        base_url,
        model,
    ):
        if (self.info.get('add_entity') and self.info['add_entity']) or (
            self.info.get('del_entity') and self.info['del_entity']
        ):
            modify_entity_string = ''
            if self.info.get('add_entity') and self.info['add_entity']:
                modify_entity_string += f"User's expected entity category:{','.join(self.info['add_entity'])}    "
            if self.info.get('del_entity') and self.info['del_entity']:
                modify_entity_string += f'Entity categories that users do not need:{",".join(self.info["del_entity"])}'
            all_entities = self.info['add_entity'] + self.info['del_entity']
            language = 'Chinese' if is_chinese_more_than_english(','.join(all_entities)) else 'English'
            suggestion_improve_prompt = Template(self.load_prompt('suggestion_improve_agent.txt'))
            suggestion_improve_prompt = suggestion_improve_prompt.render(
                modify_entity_string=modify_entity_string, pre_suggestion=self.pre_suggestion, language=language
            )
            improved_user_need = await self.chatresponse(
                suggestion_improve_prompt,
                api_key,
                base_url,
                model,
            )

            return improved_user_need, self.info
        else:
            return self.pre_suggestion, self.info

    async def generate_suggestion(self, api_key, base_url, model):
        if self.pre_suggestion != ' ':
            return await self.following_generate_suggestion(api_key, base_url, model)
        else:
            return await self.initial_generate_suggestion(api_key, base_url, model=model)
