from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Tuple

from ..ai_unit.executor.ai_executor import AIExecutor


class InferKGValidator:
    def __init__(self):
        self.ai_executor = AIExecutor()

    @staticmethod
    def _2rdf_triple(infer_triple: Dict):
        """
        Convert triple data to rdf triple
        """
        return (
            infer_triple['DirectedEntity']['Name'],
            infer_triple['Relation']['Name'],
            infer_triple['DirectionalEntity']['Name'],
        )

    def _validate_triple(self, inferred_triple: Tuple):
        """
        Validate rdf triple
        """
        response = self.ai_executor.execute(self, inferred_triple=inferred_triple)
        return response

    def validate_kg(self, infer_kg: List):
        """
        Validate infer_kg
        """
        # web search validate & 3 vs 1 validate
        validated_kg = list()
        triple_web_source = list()
        web_source = list()  # as new seed to iterate schema

        with ThreadPoolExecutor(max_workers=4) as executor:
            future_tasks = {
                executor.submit(self._validate_triple, self._2rdf_triple(triple_dic)): index  # infer kg index
                for index, triple_dic in enumerate(infer_kg)
            }
            for future in as_completed(future_tasks):
                judgement, web_triple_source = future.result()
                index = future_tasks[future]  # infer kg index
                if judgement:
                    validated_kg.append(infer_kg[index])
                    if web_triple_source:
                        web_source.extend(web_triple_source)  # extend seed source # combine triple source
                        triple_web_source.append({
                            'ID': infer_kg[index]['ID'],
                            'TripleSource': web_triple_source,
                        })  # save triple source
        return validated_kg, web_source, triple_web_source  # return new validated infer_kg & triple source csv
