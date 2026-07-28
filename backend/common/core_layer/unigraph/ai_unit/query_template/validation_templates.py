from typing import Tuple

from jinja2 import Template

from .base_template import InstructionTemplate


class EntityKnowledgeTemplate(InstructionTemplate):
    @staticmethod
    def get_template():
        template = """
Answer the question about entity knowledge.
Ensure the correctness and purity of the output content format, without attaching any explanations or labels.

Example:
input: What is the primary simple information of the teacher?
output: The main job of teachers is to teach and educate students, and they are active in the field of technical education in various universities.
input: What is the primary simple information of the student?
output: Students are the main body of the school, and their main task is to learn knowledge.

Query:
input: What is the primary simple information of the {{entity}}?
output:
        """
        return Template(template)

    @staticmethod
    def render_template(entity: str):
        return EntityKnowledgeTemplate.get_template().render(entity=entity)


class ClaimTemplate(InstructionTemplate):
    @staticmethod
    def get_template():
        template = """
Determine whether the claim is correct based on the Knowledge of entities.
Ensure the correctness and purity of the output content format, without attaching any explanations or labels.

Example:
Entities Knowledge:
The main job of teachers is to teach and educate students, and they are active in the field of technical education in various universities.
Students are the main body of the school, and their main task is to learn knowledge.
input: Based on the knowledge above, "teacher teach student"  is reasonable.
output: Correct.

Entities Knowledge:
The primary simple information about a country typically includes its geographical location, population size, capital city, official language(s), and currency.
Firefighters are emergency responders trained to combat and extinguish fires, rescue people and animals from dangerous situations, and provide medical assistance in emergencies. They often work for fire departments or emergency services agencies and undergo rigorous training to handle various types of emergencies.
input: Based on the knowledge above, "country eat firefighters" is reasonable.
output: Incorrect.

Query:
Entities Knowledge:
{{domain_knowledge}}
input: Based on the knowledge above, "{{directional_entity}} {{relation}} {{directed_entity}}" is reasonable.  
output:
        """
        return Template(template)

    @staticmethod
    def render_template(domain_knowledge, inferred_triple: Tuple):
        directional_entity, relation, directed_entity = inferred_triple
        return ClaimTemplate.get_template().render(
            domain_knowledge=domain_knowledge,
            directional_entity=directional_entity,
            relation=relation,
            directed_entity=directed_entity,
        )


class GenerateOptionTemplate(InstructionTemplate):
    @staticmethod
    def get_template():
        template = """

Given two entities, generate three irrational relationships between them. 
Ensure the irrationality of generating entity relationships.
Ensure the correctness and purity of the output content format, without attaching any explanations or labels.

Example:
input: cat, car
output: drive, eat, manufacture
input: 树, 计算机
output: 计算, 成长, 充电

Query:
input: {{entities}}
output:        
        """
        return Template(template)

    @staticmethod
    def render_template(entities: str):
        return GenerateOptionTemplate.get_template().render(entities=entities)


class JudgementTemplate(InstructionTemplate):
    @staticmethod
    def get_template():
        template = """
Choose the best entity relationship.
Ensure the correctness and purity of the output content format, without attaching any explanations or labels.

Example:
input: 
triple: (operate system, ?, memory)
choices: eat, grow, run, manage
output: manage

input:
triple: (student, ,math)
choices: learn, make, play, operate
output: learn

Query:
input:
triple: {{infer_triple}}
choices: {{choices}}
output:
        """
        return Template(template)

    @staticmethod
    def render_template(infer_triple: str, choices: str):
        return JudgementTemplate.get_template().render(infer_triple=infer_triple, choices=choices)


class GenerationTemplate(InstructionTemplate):
    @staticmethod
    def get_template():
        template = """
Generate the corresponding text in reverse based on triples.
Pay attention to generating source information as rich as possible while maintaining its accuracy.
If accurate text cannot be provided, respond with "No"
Ensure the correctness and purity of the output content format, without attaching any explanations or labels.

Example:
input:(学习, 是, 积累过程)
output:学习是一种积累的过程，通过不断地学习和实践，我们可以逐步积累知识和经验。正如老话所说，学习是没有尽头的，每一步的积累都会为未来打下坚实的基础。

Query:
input:{{inferred_triple}}
output:
        """
        return Template(template)

    @staticmethod
    def render_template(inferred_triple: Tuple):
        return GenerationTemplate.get_template().render(inferred_triple=inferred_triple)
