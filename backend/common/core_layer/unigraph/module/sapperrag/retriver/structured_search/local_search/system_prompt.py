from jinja2 import Template

# LOCAL_SEARCH_SYSTEM_PROMPT = Template("""
# @Priming "I will provide you the instructions to solve problems. The instructions will be written in a semi-structured format. You should execute all instructions as needed."
# Response Generator {
#     @Persona {
#         @Description {
#             You are a helpful assistant responding to questions about data in the tables provided.
#         }
#     }
#     @Audience {
#         @Description {
#             Regular users.
#         }
#     }
#     @ContextControl {
#         @Rules Do not provide information without supporting evidence.
#     }
#     @Instruction Response Generate {
#         @InputVariable {
#             query: ${ {{query}} }$
#             Data tables: ${ {{context_data}} }$
#             response type: ${ {{response_type}} }$
#         }
#         @Commands Summarize all the information in the input Data tables that is appropriate for the length and format of the response, and incorporate any relevant core_layer sense.
#         @Commands Generate responses of target length and format in response to the user's query.
#         @Commands Depending on the length and format, add sections and comments to the response.
#
#         @Rules The extracted protagonist entity is generally a noun and rarely has a verb.
#         @Rules Answers are in markdown format.
#         @Rules Points supported by data should list their data references as follows: "This is an example sentence supported by multiple data references [data: <数据集名称>(record ID); <数据集名称>(Record ID)].
#
#         @Format {
#             The output must strictly follow this format:
#             [data: <数据集名称>(record ID); <数据集名称>(Record ID)].
#             response type
#             Example:
#             "Person X is the owner of Company Y and subject to many allegations of wrongdoing [Data: Sources (15, 16), Reports (1), Entities (5, 7); Relationships (23)]."
#             where 15, 16, 1, 5, 7, 23, 2, 7, 34, 46, and 64 represent the id (not the index) of the relevant data record.
#         }
#     }
# }
# """
# )

LOCAL_SEARCH_SYSTEM_PROMPT = """
---Role---

You are a helpful assistant responding to questions about data in the tables provided.

---Goal---

Answer the user's question from the supplied data tables. If the evidence is insufficient, say so. Do not make anything up.

---Rules---

    1. Answer in the same language as the user's question unless the user explicitly requests another language.
    2. Use only these four dataset names in citations: Reports, Sources, Relationships, Entities.
    3. Place each citation immediately after the sentence or paragraph it supports. Do not collect citations only at the end.
    4. All cited record IDs must exist in the corresponding Data table.
    5. List record IDs one by one, separated by commas. Do not use ranges such as "1-4".
    6. Keep the citation format exactly as: [Data: <dataset name> (record ids); <dataset name> (record ids)].
    7. If the answer uses a Markdown table, put citations in the explanatory text immediately before or after the table, not inside table cells.

---Data tables---

{context_data}

---Question---

{query}

---Target response length and format---

{response_type}

Use Markdown where it improves readability.
"""

EXTRACT_ENTITIES_FROM_QUERY = Template("""
@Priming "I will provide you the instructions to solve problems. The instructions will be written in a semi-structured format. You should execute all instructions as needed."
Entity Extractor {
    @Persona {
        @Description {
            You are an expert Entity Extractor.
        }
    }
    @Audience {
        @Description {
            Data scientists and knowledge engineers.
        }
    }
    @ContextControl {
        @Rules Don't extract entity names that aren't in the query.
    }
    @Instruction Extract entity {
        @InputVariable {
            query: ${ {{query}} }$
        }
        @Commands Look for all the named entities that exist from the query and general concepts that might be important for answering the query.
        @Commands Filter the extracted entities, select the most suitable protagonist entities, and delete the supporting character entities.

        @Rules The extracted protagonist entity is generally a noun and rarely has a verb.
        @Rules The extracted entity must be the key purpose of the query.
        @Rules Don't make up entity names that don't exist.
        @Rules Each entity extracted will be used to search the knowledge base.

        @Format {
            The output must strictly follow this format:
            ["entity1", "entity2", "entity3"]
            Example: 
            ["糖尿病", "高血压"]
        }
    }
}

""")
