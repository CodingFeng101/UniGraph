from typing import Dict, List

from celery import Task

from backend.common.core_layer.unigraph.module.kg_constructor import SemanticKGConstructor
from backend.common.core_layer.unigraph.module.kg_infer import SemanticKGInfer


async def create_kg(
    kg_schema: List,
    schema_definition: Dict,
    documents_dir_path: str,
    api_key: str,
    base_url: str,
    model: str,
    task_client: Task,
):
    """
    Create KG from documents in the specified directory based on the schema and schema definition provided.
    """
    api_result = list()
    constructor = SemanticKGConstructor(kg_schema, schema_definition)
    semantic_kg, structure_kg, triple_source = await constructor.extract_kg(
        dir_path=documents_dir_path,
        api_key=api_key,
        base_url=base_url,
        model=model,
        task_client=task_client,
    )
    api_result.append({
        'file_name': 'all',
        'semantic_kg': semantic_kg,
        'structure_kg': structure_kg,
        'triple_source': triple_source,
    })
    return api_result


async def create_infer_kg(
    kg: list,
    api_key: str,
    base_url: str,
    model: str,
    task_client: Task,
):
    """
    Create infer KG from the KGs created based on the schema.
    """
    infer = SemanticKGInfer()
    infer_kg = await infer.infer_kg(
        kg=kg,
        api_key=api_key,
        base_url=base_url,
        model=model,
        task_client=task_client,
    )
    # validated_infer_kg, web_source, triple_source = validator.validate_kg(infer_kg)
    validated_infer_kg, web_source, triple_source = infer_kg, [], []
    api_result = {'infer_kg': validated_infer_kg, 'web_source': web_source, 'triple_source': triple_source}

    return api_result
