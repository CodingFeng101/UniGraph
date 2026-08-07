# from jinja2 import Template
#
# REPORT_GENERATE = Template("""
# @Priming "I will provide you the instructions to solve problems. The instructions will be written in a semi-structured format. You should execute all instructions as needed."
# Community Report Generator {
#     @Persona {
#         @Description {
#             You are an expert Community Report Generator.
#         }
#     }
#     @Audience {
#         @Description {
#             Data scientists and knowledge engineers.
#         }
#     }
#     @ContextControl {
#         @Rules The content of this report includes an overview of the key entities of the community, their legal compliance, technical capabilities, reputation, and notable attributes.
#         @Rules Information discovery is the process of identifying and evaluating relevant information related to certain entities in a network, such as organizations and individuals.
#     }
#     @Instruction  Generate Report {
#         @InputVariable {
#             community: ${ {{community}} }$
#         }
#         @Commands Write a comprehensive report of the community, given a list of entities that belong to the community, their relationships and optional associated attributes.
#         @Commands The content of this report includes an overview of the key entities of the community, their legal compliance, technical capabilities, reputation, and notable attributes.
#         @Commands Title: The name of the community that represents its key entity – The title should be short but specific. If possible, include representative named entities in the title.
#         @Commands Summary: An executive summary of the community's overall structure, how its entities are related to each other, and significant information associated with its entities.
#         @Commands IMPACT SEVERITY RATING: a float score between 0-10 that represents the severity of IMPACT posed by entities within the community.  IMPACT is the scored importance of a community.
#         @Commands RATING EXPLANATION: Give a single sentence explanation of the IMPACT severity rating.
#         @Commands DETAILED FINDINGS: A list of 2-3 key insights about the community. Each insight should have a short summary followed by multiple paragraphs of explanatory text grounded according to the grounding rules below. Be comprehensive.
#
#         @Rules The extracted protagonist entity is generally a noun and rarely has a verb.
#         @Rules The extracted entity must be the key purpose of the query.
#         @Rules Don't make up entity names that don't exist.
#         @Rules Each entity extracted will be used to search the knowledge base.
#         @Rules The content corresponding to each field in the community report is in Chinese.
#
#         @Format {
#             {
#                 "title": "<report_title>",
#                 "summary": "<executive_summary>",
#                 "rating": <impact_severity_rating>,
#                 "rating_explanation": "<rating_explanation>",
#                 "findings": [
#                     {
#                         "summary": "<insight_1_summary>",
#                         "explanation": "<insight_1_explanation>"
#                     },
#                     {
#                         "summary": "<insight_2_summary>",
#                         "explanation": "<insight_2_explanation>"
#                     }
#                 ]
#             }
#         }
#     }
# """
# )


REPORT_GENERATE = """
You are an AI assistant that helps a human analyst to perform general information discovery. Information discovery is the process of identifying and assessing relevant information associated with certain entities (e.g., organizations and individuals) within a network.

# Goal
Write a comprehensive report of a community, given a list of entities that belong to the community as well as their relationships and optional associated attributes. The report will be used to inform decision-makers about information associated with the community and their potential impact. The content of this report includes an overview of the community's key entities, their legal compliance, technical capabilities, reputation, and noteworthy attributes.

# Report Structure

The report should include the following sections:

- TITLE: community's name that represents its key entities - title should be short but specific. When possible, include representative named entities in the title.
- SUMMARY: An executive summary of the community's overall structure, how its entities are related to each other, and significant information associated with its entities.
- IMPACT SEVERITY RATING: a float score between 0-10 that represents the severity of IMPACT posed by entities within the community.  IMPACT is the scored importance of a community.
- RATING EXPLANATION: Give a single sentence explanation of the IMPACT severity rating.
- DETAILED FINDINGS: A list of 2-3 key insights about the community. Each insight should have a short summary followed by multiple paragraphs of explanatory text grounded according to the grounding rules below. Be comprehensive.

Return output_try as a well-formed JSON-formatted string with the following format:
    {{
        "title": "<report_title>",
        "summary": "<executive_summary>",
        "rating": <impact_severity_rating>,
        "rating_explanation": "<rating_explanation>",
        "findings": [
            {{
                "summary": "<insight_1_summary>",
                "explanation": "<insight_1_explanation>"
            }},
            {{
                "summary": "<insight_2_summary>",
                "explanation": "<insight_2_explanation>"
            }}
        ]
    }}

# Grounding Rules

The language of the output community report is the same as the language of the input text.
The community report should not have multiple line breaks in a row.

# Real Data

Use the following text for your answer. Do not make anything up in your answer.

Text:
{input_text}

Output:
"""
