from .base import PromptTemplateFactory


class QueryBuilderPromptTemplate(PromptTemplateFactory):
    prompt: str = """You are an AI language model assistant. Your task is to generate a query based
    on the user fields of interest to search for related {platform}.
    Fields of Interest: {fields}
    """

    def create_template(self, fields: str, platform: str) -> str:
        return self.prompt.format(platform=platform, fields=fields).replace("\n", "")


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

    def create_template(self, question, seperator: str, expand_to_n: int) -> str:
        return self.prompt.format(question=question, separator=seperator, expand_to_n=expand_to_n)


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

    def create_template(self, question: str) -> str:
        return self.prompt.format(question=self.question)
