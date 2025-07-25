from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.chat_engine import CondensePlusContextChatEngine
from utils.create_faiss_store import load_index
from utils.llm_model import llm
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

def get_faiss_index(service_name):
    index_dir = f"{service_name.lower().replace(' ', '-')}-faiss-index"
    return load_index(index_dir=index_dir)


def get_chat_engine(session_id, service_name):

    if "memory" not in st.session_state or st.session_state.session_id != session_id:
        st.session_state.session_id = session_id
        st.session_state.memory = ChatMemoryBuffer.from_defaults(token_limit=3000)

    system_template = """   
        Objective: To respond to queries from possible customers of the service.

        Instructions:
        
        1. Query Understanding: Understand the query from the user.
        2. Concise Response: Provide a brief, accurate response based on the information from the service.
        3. If you dont have relevant information, please ask the user to reach out to the service support team.
        Response Template:
        
        [Provide a concise and accurate response based on the service articles]
        
        Example:
        User Query: What are the requirements for a Spanish citizenship?
        
        Response:
        The requirements for a Spanish citizenship include maintaining full-time enrollment, providing \n
        proof of financial support, and demonstrating academic progress.
 
        Implementation:
        
        Ensure the response is relevant to the query and is derived from the service articles.
        Maintain a professional and helpful tone throughout the interaction.
        
        chat_history: 
        {}
        """

    vector_index = get_faiss_index(service_name=service_name)
    # cohere_rerank = CohereRerank(api_key=cohere_api, top_n=3)
    retriever = vector_index.as_retriever(similarity_top_k=5)

    chat_engine = CondensePlusContextChatEngine.from_defaults(
        retriever=retriever,
        llm=llm,
        system_prompt=system_template,
        memory=st.session_state.memory,
        # node_postprocessors=[cohere_rerank],
        verbose=False
    )

    return chat_engine

# if __name__ == '__main__':
#     datasink_db_name = 'ds-orca'
#     vector_collection_name = 'vectors'
#     country_code = 'ESP'
#     platform_type = 'AGENT'
#     from db_utils import mongo_client

#     vector_index, filters = get_vector_index(mongo_client, datasink_db_name, vector_collection_name, platform_type, country_code)
#     # cohere_rerank = CohereRerank(api_key=cohere_api, top_n=3)
#     retriever = vector_index.as_retriever(filters=filters, similarity_top_k=5)

#     chat_engine = CondensePlusContextChatEngine.from_defaults(
#         retriever=retriever,
#         llm=llm,
#         # node_postprocessors=[cohere_rerank],
#         verbose=False
#     )

#     res = chat_engine.chat('where can i find data on my profile')
#     print(res)