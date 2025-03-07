from langchain.prompts import PromptTemplate

from .base import PromptTemplateFactory


class QueryBuilderPromptTemplate(PromptTemplateFactory):
    prompt: str = """You are an AI language model assistant. Your task is to generate {number_of_queries} different versions for a blog query based
    on the user fields of interest. Those queries will be used to search for blogs posts on those topics. Each query can focus on different domains or only on specific fields
    but they have to be different. The output should be a JSON list where each item in the list is a query you generated.
    Fields of Interest: {fields}
    Queries:
    """

    def create_template(self, number_of_queries: int) -> PromptTemplate:
        return PromptTemplate(
            template=self.prompt, input_variables=["fields"], partial_variables={"number_of_queries": number_of_queries}
        )

    def get_str_prompt(self, fields: str, number_of_queries: int) -> str:
        return self.prompt.format(number_of_queries=number_of_queries, fields=fields).replace("\n", "")


class QueryExpansionTemplate(PromptTemplateFactory):
    prompt: str = """You are an AI language model assistant. Your task is to generate {expand_to_n}
    different versions of the given user question to retrieve relevant documents from a vector
    database. By generating multiple perspectives on the user question, your goal is to help
    the user overcome some of the limitations of the distance-based similarity search.
    Provide these alternative questions seperated by '{separator}'.
    Original question: {question}"""

    @property
    def separator(self) -> str:
        return "#next-question#"

    def create_template(self, expand_to_n: int) -> PromptTemplate:
        return PromptTemplate(
            template=self.prompt,
            input_variables=["question"],
            partial_variables={
                "separator": self.separator,
                "expand_to_n": expand_to_n,
            },
        )


class SelfQueryTemplate(PromptTemplateFactory):
    prompt: str = """You are an AI language model assistant. Your task is to extract information from a document.
    The required information that needs to be extracted are relevant key words that best represent the core concepts 
    of the document. 
    Your response should consists of only the extracted keywords, nothing else.
    
    For example:
    DOCUMENT 1:
    This is a blog about LLM agents in the field of threat intelligence. LLM agents are...
    RESPONSE 1:
    [LLM, agents, threat intelligence]
    
    DOCUMENT 2:
    The paper introduces a new framework called CAS, cybersecurity as a service...
    RESPONSE 2:
    [cybersecurity]
    
    DOCUMENT 3:
    This study examines the existing literature, providing a thorough characterization of both defensive and adversarial applications of LLMs within the realm of cybersecurity.
    RESPONSE 3:
    [LLM, cybersecurity, defensive, adversarial]
    
    User question: {question}"""

    def create_template(self) -> PromptTemplate:
        return PromptTemplate(template=self.prompt, input_variables=["question"])
