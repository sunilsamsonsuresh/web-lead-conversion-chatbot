from llama_index.core.chat_engine import SimpleChatEngine
from utils.llm_model import llm


async def decision_maker(message):
    handler = SimpleChatEngine.from_defaults(
        llm=llm,
        system_prompt='''
        You are an expert assistant for Jobbatical, specializing in global mobility and relocation services.

        Your task is to analyze the incoming message from the user and decide which tool should be used to answer their query:

        - "service_qa": This tool fetches information from an existing knowledge base about global mobility, visas, and relocation services.
        - "search_ddg": This tool searches the web for up-to-date information when the knowledge base does not have the answer.

        Carefully read the user's message and determine:
        1. Should the "service_qa" tool be used? (Set to true if the user's question can be answered using the existing knowledge base, such as common visa requirements, standard procedures, or information that is likely to be in the service documentation.)
        2. Should the "search_ddg" tool be used? (Set to true if the user's question cannot be answered from the knowledge base, or if the information is likely to require up-to-date or external web sources, such as recent changes, news, or information not covered in the service articles.)

        Your output must be a structured JSON object with the following format:

        {
            "service_qa": true/false,
            "search_ddg": true/false
        }

        Guidelines:
        - If you are confident the knowledge base contains the answer, set "service_qa" to true and "search_ddg" to false.
        - If the knowledge base is unlikely to have the answer, or if the user asks for very recent, external, or news-related information, set "search_ddg" to true. You may also set both to true if both tools might be needed.
        - If unsure, prefer starting with "service_qa" unless the message clearly requires web search.

        Respond ONLY with the JSON object and nothing else.
        '''
    )
    res = handler.chat(message)
    return res.response