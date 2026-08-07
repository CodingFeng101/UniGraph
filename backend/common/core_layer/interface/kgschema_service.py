from backend.common.core_layer.unigraph.module.schema_construction.schema_construction import SchemaConstruction
from backend.common.core_layer.unigraph.module.schema_construction.suggestion_generation import SuggestionGeneration


async def create_schema(
    file_path_list,
    aim,
    api_key,
    base_url,
    model: str,
    embedding_api_key: str,
    embedding_base_url: str,
    embedding_model: str,
    progress_callback=None,
):
    construction = SchemaConstruction(kg_schema=[], definition={})
    modify_info = {'add_entity': [], 'add_relationship': [], 'del_entity': [], 'del_relationship': []}
    schema, definition = await construction.extract_from_path(
        file_path_list=file_path_list,
        aim=aim,
        info=modify_info,
        directional_suggestion='',
        api_key=api_key,
        base_url=base_url,
        model=model,
        embedding_api_key=embedding_api_key,
        embedding_base_url=embedding_base_url,
        embedding_model=embedding_model,
        progress_callback=progress_callback,
    )
    return schema, definition


async def update_schema(
    file_path_list,
    aim,
    kg_schema,
    definition,
    modify_info,
    suggestion,
    api_key,
    base_url,
    model: str,
    embedding_api_key: str,
    embedding_base_url: str,
    embedding_model: str,
    progress_callback=None,
):
    construction = SchemaConstruction(kg_schema=kg_schema, definition=definition)

    schema, definition = await construction.extract_from_path(
        file_path_list=file_path_list,
        aim=aim,
        info=modify_info,
        directional_suggestion=suggestion,
        api_key=api_key,
        base_url=base_url,
        model=model,
        embedding_api_key=embedding_api_key,
        embedding_base_url=embedding_base_url,
        embedding_model=embedding_model,
        progress_callback=progress_callback,
    )

    return schema, definition


async def suggestion_generation(
    info,
    pre_suggestion,
    api_key,
    base_url,
    model,
):
    suggestion_generator = SuggestionGeneration(
        info=info,
        pre_suggestion=pre_suggestion,
    )
    suggestion, info = await suggestion_generator.generate_suggestion(api_key=api_key, base_url=base_url, model=model)
    return suggestion, info
