from ..chains.extraction_chain import run_extraction_chain
from ..chains.inference_chain import run_inference_chain
from ..chains.multiple_validation import run_validation
from ..llm.response_getter import ResponseGetterFactory


class AIExecutor:
    def __init__(self):
        self.response_getter_factory = ResponseGetterFactory()

    async def execute(self, module_executor, **kwargs):
        # 内部导入，避免循环
        from ...module.kg_constructor import SemanticKGConstructor
        from ...module.kg_infer import SemanticKGInfer
        from ...module.kg_validate import InferKGValidator

        ai_response_getter = self.response_getter_factory.create()  # rely on the parameter in the config.py
        # 以三个模块执行器的对象类型为判断依据，决定执行哪个chain
        # llm_parameter所决定的各类response_getter，由对应的chain执行工厂方法。
        if isinstance(module_executor, SemanticKGConstructor):
            return await run_extraction_chain(
                ai_response_getter=ai_response_getter, **kwargs
            )  # 这里还需要传入ai_response_getter
        elif isinstance(module_executor, SemanticKGInfer):
            return await run_inference_chain(ai_response_getter=ai_response_getter, **kwargs)
        elif isinstance(module_executor, InferKGValidator):
            return await run_validation(ai_response_getter=ai_response_getter, **kwargs)
        else:
            pass
