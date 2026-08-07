from backend.app.admin.crud.crud_llm_create import LlmCreateCRUD
from backend.app.admin.crud.crud_llm_provider import llm_provider_dao
from backend.app.admin.model.llm_model import LlmModel
from backend.app.admin.model.llm_provider_model import LlmProvider
from backend.database.db_mysql import async_db_session

# {"name": "", "type": "text-generation", "status": 0},
# {"name": "", "type": "image-generation", "status": 0},
# {"name": "", "type": "video-generation", "status": 0},
# {"name": "", "type": "text-embedding", "status": 0},
# {"name": "", "type": "audio-generation", "status": 0},

llm_providers_data = {
    'NO.1 API': [
        {
            'group_name': 'OpenAI',
            'models': [
                {'name': 'gpt-3.5-turbo', 'type': 'text-generation', 'status': 0},
                {'name': 'gpt-4', 'type': 'text-generation', 'status': 0},
                {'name': 'gpt-4-turbo', 'type': 'text-generation', 'status': 0},
                {'name': 'gpt-4o', 'type': 'text-generation', 'status': 0},
                {'name': 'gpt-4o-2024-08-06', 'type': 'text-generation', 'status': 0},
                {'name': 'gpt-4o-mini', 'type': 'text-generation', 'status': 0},
                {'name': 'gpt-4o-mini-2024-07-18', 'type': 'text-generation', 'status': 0},
                {'name': 'chatgpt-4o-latest', 'type': 'text-generation', 'status': 0},
                {'name': 'o1-mini', 'type': 'text-generation', 'status': 0},
                {'name': 'o1-mini-2024-09-12', 'type': 'text-generation', 'status': 0},
                {'name': 'o1-preview', 'type': 'text-generation', 'status': 0},
                {'name': 'dall-e-2', 'type': 'image-generation', 'status': 0},
                {'name': 'dall-e-3', 'type': 'image-generation', 'status': 0},
                {'name': 'text-embedding-3-large', 'type': 'text-embedding', 'status': 0},
                {'name': 'text-embedding-3-small', 'type': 'text-embedding', 'status': 0},
                {'name': 'text-embedding-v1', 'type': 'text-embedding', 'status': 0},
            ],
        },
        {
            'group_name': 'Claude',
            'models': [
                {'name': 'claude-2.1', 'type': 'text-generation', 'status': 0},
                {'name': 'claude-3-5-sonnet-20240620', 'type': 'text-generation', 'status': 0},
                {'name': 'claude-3-haiku-20240307', 'type': 'text-generation', 'status': 0},
                {'name': 'claude-3-7-sonnet-20250219', 'type': 'text-generation', 'status': 0},
            ],
        },
        {
            'group_name': 'DeepSeek',
            'models': [
                {'name': 'deepseek-chat', 'type': 'text-generation', 'status': 0},
                {'name': 'deepseek-coder', 'type': 'text-generation', 'status': 0},
                {'name': 'deepseek-reasoner', 'type': 'text-generation', 'status': 0},
            ],
        },
        {
            'group_name': 'Midjourney',
            'models': [
                {'name': 'mj_fast_blend', 'type': 'text-generation', 'status': 0},
                {'name': 'mj_fast_custom_zoom', 'type': 'text-generation', 'status': 0},
                {'name': 'mj_fast_describe', 'type': 'text-generation', 'status': 0},
                {'name': 'mj_fast_imagine', 'type': 'image-generation', 'status': 0},
            ],
        },
        {
            'group_name': 'SUNO音乐',
            'models': [
                {'name': 'suno_lyrics', 'type': 'audio-generation', 'status': 0},
                {'name': 'suno_music', 'type': 'audio-generation', 'status': 0},
                {'name': 'suno-v3', 'type': 'audio-generation', 'status': 0},
                {'name': 'suno-v3.5', 'type': 'audio-generation', 'status': 0},
            ],
        },
        {
            'group_name': 'Google',
            'models': [
                {'name': 'gemini-1.5-flash', 'type': 'text-generation', 'status': 0},
                {'name': 'gemini-1.5-pro', 'type': 'text-generation', 'status': 0},
                {'name': 'gemini-1.5-pro-002', 'type': 'text-generation', 'status': 0},
                {'name': 'gemini-1.5-pro-latest', 'type': 'text-generation', 'status': 0},
            ],
        },
        {
            'group_name': '百度千帆',
            'models': [
                {'name': 'ERNIE-4.0-8K', 'type': 'text-generation', 'status': 0},
                {'name': 'ERNIE-Bot-4', 'type': 'text-generation', 'status': 0},
            ],
        },
    ],
    '腾讯混元': [
        {'group_name': 'Embedding', 'models': [{'name': 'hunyuan-embedding', 'type': 'text-embedding', 'status': 0}]},
        {
            'group_name': 'Hunyuan',
            'models': [
                {'name': 'hunyuan-pro', 'type': 'text-generation', 'status': 0},
                {'name': 'hunyuan-standard', 'type': 'text-generation', 'status': 0},
                {'name': 'hunyuan-lite', 'type': 'text-generation', 'status': 0},
                {'name': 'hunyuan-standard-256k', 'type': 'text-generation', 'status': 0},
                {'name': 'hunyuan-vision', 'type': 'text-generation', 'status': 0},
                {'name': 'hunyuan-code', 'type': 'text-generation', 'status': 0},
                {'name': 'hunyuan-role', 'type': 'text-generation', 'status': 0},
                {'name': 'hunyuan-turbo', 'type': 'text-generation', 'status': 0},
                {'name': 'hunyuan-turbos-latest', 'type': 'text-generation', 'status': 0},
            ],
        },
    ],
    'DeepSeek': [
        {'group_name': 'DeepSeek Chat', 'models': [{'name': 'deepseek-chat', 'type': 'text-generation', 'status': 0}]},
        {
            'group_name': 'DeepSeek Reasoner',
            'models': [{'name': 'deepseek-reasoner', 'type': 'text-generation', 'status': 0}],
        },
    ],
    '火山引擎': [
        {
            'group_name': 'DeepSeek',
            'models': [
                {'name': 'DeepSeek-R1', 'type': 'text-generation', 'status': 0},
                {'name': 'DeepSeek-V3', 'type': 'text-generation', 'status': 0},
                {'name': 'DeepSeek-R1-Distill-Qwen-7B', 'type': 'text-generation', 'status': 0},
                {'name': 'DeepSeek-R1-Distill-Qwen-32B', 'type': 'text-generation', 'status': 0},
            ],
        },
        {
            'group_name': '豆包',
            'models': [
                {'name': 'Doubao-1.5-vision-pro-32k', 'type': 'text-generation', 'status': 0},
                {'name': 'Doubao-1.5-pro-32k', 'type': 'text-generation', 'status': 0},
                {'name': 'Doubao-1.5-lite-32k', 'type': 'text-generation', 'status': 0},
                {'name': 'Doubao-1.5-pro-256k', 'type': 'text-generation', 'status': 0},
                {'name': 'Doubao-embedding-vision', 'type': 'text-embedding', 'status': 0},
                {'name': 'Doubao-视频生成-Seaweed', 'type': 'video-generation', 'status': 0},
                {'name': 'Doubao-音乐大模型', 'type': 'audio-generation', 'status': 0},
                {'name': 'Doubao-同声传译', 'type': 'audio-generation', 'status': 0},
                {'name': 'Doubao-录音文件识别', 'type': 'audio-generation', 'status': 0},
            ],
        },
        {
            'group_name': '月之暗面',
            'models': [
                {'name': 'Moonshot-v1-128k', 'type': 'text-generation', 'status': 0},
                {'name': 'Moonshot-v1-32k', 'type': 'text-generation', 'status': 0},
                {'name': 'Moonshot-v1-8k', 'type': 'text-generation', 'status': 0},
            ],
        },
    ],
    'Gemini': [
        {
            'group_name': 'Gemini 1.5',
            'models': [
                {'name': 'Gemini 1.5 Flash', 'type': 'text-generation', 'status': 0},
                {'name': 'Gemini 1.5 Flash (8B)', 'type': 'text-generation', 'status': 0},
                {'name': 'Gemini 1.5 Pro', 'type': 'text-generation', 'status': 0},
            ],
        },
        {
            'group_name': 'Gemini 2.0',
            'models': [
                {'name': 'Gemini 2.0 Flash', 'type': 'text-generation', 'status': 0},
            ],
        },
    ],
    '月之暗面': [
        {
            'group_name': 'moonshot-v1',
            'models': [
                {'name': 'moonshot-v1-auto', 'type': 'text-generation', 'status': 0},
            ],
        }
    ],
    '百川': [
        {
            'group_name': 'Baichuan3',
            'models': [
                {'name': 'Baichuan3 Turbo', 'type': 'text-generation', 'status': 0},
                {'name': 'Baichuan3 Turbo 128k', 'type': 'text-generation', 'status': 0},
            ],
        },
        {'group_name': 'Baichuan4', 'models': [{'name': 'Baichuan4', 'type': 'text-generation', 'status': 0}]},
    ],
    '阿里云百炼': [
        {
            'group_name': 'qwen-coder',
            'models': [
                {'name': 'qwen-coder-plus', 'type': 'text-generation', 'status': 0},
            ],
        },
        {
            'group_name': 'qwen-max',
            'models': [
                {'name': 'qwen-max', 'type': 'text-generation', 'status': 0},
            ],
        },
        {
            'group_name': 'qwen-plus',
            'models': [
                {'name': 'qwen-plus', 'type': 'text-generation', 'status': 0},
            ],
        },
        {
            'group_name': 'qwen-turbo',
            'models': [
                {'name': 'qwen-turbo', 'type': 'text-generation', 'status': 0},
            ],
        },
        {
            'group_name': 'qwen-vl',
            'models': [
                {'name': 'qwen-vl-plus', 'type': 'text-generation', 'status': 0},
            ],
        },
    ],
    '硅基流动': [
        {
            'group_name': 'BAAI',
            'models': [
                {'name': 'BAAI/bge-m3', 'type': 'text-embedding', 'status': 0},
            ],
        },
        {
            'group_name': 'Qwen',
            'models': [
                {'name': 'Qwen2.5-7B-Instruct', 'type': 'text-embedding', 'status': 0},
            ],
        },
        {
            'group_name': 'deepseek-ai',
            'models': [
                {'name': 'deepseek-ai/DeepSeek-R1', 'type': 'text-generation', 'status': 0},
                {'name': 'deepseek-ai/DeepSeek-V3', 'type': 'text-generation', 'status': 0},
            ],
        },
        {
            'group_name': 'meta-llama',
            'models': [
                {'name': 'meta-llama/Llama-3.3-70B-Instruct', 'type': 'text-generation', 'status': 0},
            ],
        },
    ],
}


class LlmCreateService:
    @staticmethod
    async def add_llm_providers(user_uuid: str):
        providers = [
            ('NO.1 API', 'https://api.rcouyi.com/v1', 'https://api.rcouyi.com/', 'https://api.rcouyi.com/', 1),
            (
                'OpenAI',
                'https://api.openai.com',
                'https://platform.openai.com/docs',
                'https://api.openai.com/v1/models',
                0,
            ),
            (
                'Anthropic',
                'https://api.anthropic.com',
                'https://docs.anthropic.com',
                'https://api.anthropic.com/v1/models',
                0,
            ),
            ('Cohere', 'https://api.cohere.ai', 'https://docs.cohere.ai', 'https://api.cohere.ai/v1/models', 0),
            (
                '硅基流动',
                'https://api.siliconflow.cn',
                'https://docs.siliconflow.cn',
                'https://api.siliconflow.cn/v1/models',
                0,
            ),
            ('O3', 'https://api.o3.fan', 'https://docs.o3.fan/', 'https://docs.o3.fan/models', 0),
            ('AiHubMix', 'https://aihubmix.com', 'https://doc.aihubmix.com/', 'https://aihubmix.com/models', 0),
            (
                'DeepSeek',
                'https://api.deepseek.com',
                'https://api-docs.deepseek.com/zh-cn',
                'https://api-docs.deepseek.com/zh-cn/quick_start/pricing',
                0,
            ),
            (
                'ocoolAI',
                'https://api.ocoolai.com',
                'https://docs.ocoolai.com/',
                'https://api.ocoolai.com/info/models/',
                0,
            ),
            (
                'Ollama',
                'http://localhost:11434',
                'https://github.com/ollama/ollama/tree/main/docs',
                'https://ollama.com/library',
                0,
            ),
            ('LM Studio', 'http://localhost:1234', 'https://lmstudio.ai/docs', 'https://lmstudio.ai/models', 0),
            (
                'Azure OpenAI',
                'https://api.anthropic.com/',
                'https://docs.anthropic.com/en/docs/',
                'https://docs.anthropic.com/en/docs/about-claude/models/all-models',
                0,
            ),
            (
                'Gemini',
                'https://generativelanguage.googleapis.com',
                'https://ai.google.dev/gemini-api/docs',
                'https://ai.google.dev/gemini-api/docs/models/gemini',
                0,
            ),
            (
                'GitHub Models',
                'https://models.inference.ai.azure.com/',
                'https://docs.github.com/en/github-models',
                'https://github.com/marketplace/models',
                0,
            ),
            (
                'DMXAPI',
                'https://www.dmxapi.cn',
                'https://dmxapi.cn/models.html#code-block',
                'https://www.dmxapi.cn/pricing',
                0,
            ),
            (
                '零一万物',
                'https://api.lingyiwanwu.com',
                'https://platform.lingyiwanwu.com/docs',
                'https://platform.lingyiwanwu.com/docs#%E6%A8%A1%E5%9E%8B',
                0,
            ),
            (
                '智谱AI',
                'https://open.bigmodel.cn/api/paas.v4/',
                'https://open.bigmodel.cn/dev/howuse/introduction',
                'https://open.bigmodel.cn/modelcenter/square',
                0,
            ),
            (
                '月之暗面',
                'https://api.moonshot.cn',
                'https://platform.moonshot.cn/docs/intro',
                'https://platform.moonshot.cn/docs/intro#%E6%A8%A1%E5%9E%8B%E5%88%97%E8%A1%A8',
                0,
            ),
            (
                '百川',
                'https://api.baichuan-ai.com',
                'https://platform.baichuan-ai.com/docs',
                'https://platform.baichuan-ai.com/price',
                0,
            ),
            (
                '阿里云百炼',
                'https://dashscope.aliyuncs.com/compatible-mode/v1/',
                'https://help.aliyun.com/zh/model-studio/getting-started/',
                'https://bailian.console.aliyun.com/model-market#/model-market',
                0,
            ),
            (
                '火山引擎',
                'https://ark.cn-beijing.volces.com/api/v3/',
                'https://www.volcengine.com/docs/82379/1182403',
                'https://console.volcengine.com/ark/region:ark+cn-beijing/endpoint',
                0,
            ),
            (
                'OpenRouter',
                'https://openrouter.ai/api/v1/',
                'https://openrouter.ai/docs/',
                'https://openrouter.ai/docs/models',
                0,
            ),
            (
                '腾讯混元',
                'https://api.hunyuan.cloud.tencent.com',
                'https://cloud.tencent.com/document/product/1729/111007',
                'https://cloud.tencent.com/document/product/1729/104753',
                0,
            ),
            (
                '腾讯云TI',
                'https://api.lkeap.cloud.tencent.com',
                'https://cloud.tencent.com/document/product/1772',
                'https://console.cloud.tencent.com/tione/v2/aimarket',
                0,
            ),
        ]

        objects = []
        for name, api_url, document_url, llm_model_url, status in providers:
            objects.append(
                LlmProvider(
                    user_uuid=user_uuid,
                    name=name,
                    api_key='',
                    api_url=api_url,
                    document_url=document_url,
                    llm_model_url=llm_model_url,
                    status=status,
                )
            )

        async with async_db_session() as db:
            await LlmCreateCRUD.create_providers(db, objects, commit=True)

        async with async_db_session() as db:
            all_providers = await llm_provider_dao.get_all(db, user_uuid=user_uuid)

        # 组织模型数据
        model_objects = []

        for provider in all_providers:
            if provider.name in llm_providers_data.keys():
                for group in llm_providers_data[provider.name]:
                    group_name = group['group_name']
                    for model in group['models']:
                        model_objects.append(
                            LlmModel(
                                provider_uuid=provider.uuid,
                                group_name=group_name,
                                name=model['name'],
                                type=model['type'],
                                status=model['status'],
                            )
                        )

        if len(model_objects) != 0:
            async with async_db_session() as db:
                await LlmCreateCRUD.create_models(db, model_objects, commit=True)

    @staticmethod
    async def test(base_url: str, api_key: str, model_name: str, model_type: str = 'llm'):
        from backend.common.clients import openai_client_registry
        from backend.common.security.outbound_url import validate_outbound_http_url

        await validate_outbound_http_url(base_url)
        client = await openai_client_registry.get(api_key=api_key, base_url=base_url)
        if model_type == 'embedding':
            await client.embeddings.create(
                model=model_name,
                input=['connection test'],
            )
            return
        await client.chat.completions.create(
            model=model_name,
            messages=[
                {'role': 'system', 'content': 'You are a helpful assistant'},
                {'role': 'user', 'content': 'Hello'},
            ],
            stream=False,
        )


llm_create_service = LlmCreateService()
