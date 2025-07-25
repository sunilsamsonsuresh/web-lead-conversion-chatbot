
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.chat_engine import CondensePlusContextChatEngine
from llama_index.core.tools import FunctionTool, ToolMetadata
from utils.llm_model import llm
import streamlit as st
from utils.create_faiss_store import load_index

def get_faiss_index(service_name):
    index_dir = f"{service_name.lower().replace(' ', '-')}-faiss-index"
    return load_index(index_dir=index_dir)

class ServiceChatTool:
    """
    Tool for answering service-related queries using a retrieval-augmented chat engine.
    """

    def __init__(self, service_name):
        self.service_name = service_name
        self.vector_index = get_faiss_index(service_name=service_name)
        self.retriever = self.vector_index.as_retriever(similarity_top_k=5)
        self.system_template = """   
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

    @staticmethod
    def _ensure_memory(session_id):
        if "memory" not in st.session_state or st.session_state.session_id != session_id:
            st.session_state.session_id = session_id
            st.session_state.memory = ChatMemoryBuffer.from_defaults(token_limit=3000)
        return st.session_state.memory

    def answer_query(self, query: str, session_id: str) -> str:
        """
        Answer a user query using the chat engine and service knowledge base.
        """
        memory = self._ensure_memory(session_id)
        chat_engine = CondensePlusContextChatEngine.from_defaults(
            retriever=self.retriever,
            llm=llm,
            system_prompt=self.system_template,
            memory=memory,
            verbose=False
        )
        response = chat_engine.chat(query)
        return response

    def create_service_tool(self):
        return FunctionTool.from_defaults(
            fn=lambda query, session_id: self.answer_query(query, session_id),
            tool_metadata=ToolMetadata(
                name='service_qa',
                description=f'Use this tool to answer questions about the {self.service_name} using the service knowledge base.'
            )
        )
