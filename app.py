import streamlit as st
from llama_index.core.memory import ChatMemoryBuffer
from utils.chat_utils import get_chat_engine
from utils.constants import DATASINK, VECTORS
import uuid
from utils.tool_executor import ToolExecutor
from toolkits.tool_builder import ToolBuilder
import asyncio

# Initialize session state variables if not already present
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.memory = ChatMemoryBuffer.from_defaults(token_limit=3000)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar for session ID and country selection
with st.sidebar:
    st.write(f'Session ID: {st.session_state.session_id}')
    service_name = st.selectbox('Service', ('Select Service', 'Spanish Citizenship Service'))
    if service_name and service_name != 'Select Service':
        if st.button("Delete Chat History"):
            st.session_state.messages = []
            st.rerun()  # Force a rerun to clear chat history

st.title(f"{service_name} Chatbot")

USER_AVATAR = "👤"
BOT_AVATAR = "🤖"

datasink_db_name = DATASINK
vector_collection_name = VECTORS
session_id = st.session_state.session_id

tool_executor = ToolExecutor()


def get_chat_engine_with_memory(_session_id, _service_name):
    return get_chat_engine(_session_id, _service_name)

def get_tools(service_name):
    return ToolBuilder(service_name).build_tools()

def get_agent_response(message, service_name, session_id):
    tools = get_tools(service_name)
    return tool_executor.tool_executor(message, tools, session_id, service_name)


def filter_response(chat_engine, response, thresh=0.7):
    if response.source_nodes[0].score > thresh:
        return {
            "response": response.response,
            "url": response.source_nodes[0].metadata.get('url'),
            'title': response.source_nodes[0].metadata.get('title'),
            "chat_history": chat_engine.chat_history
        }
    else:
        support_text = '''
        If you need assistance on the platform, please reach out to the Jobbatical support team for guidance.
        '''
        return {
            "response": f'{response.response} \n {support_text}',
            "url": None,
            'title': None,
            "chat_history": chat_engine.chat_history
        }


if service_name and service_name != 'Select Service':
    chat_engine = get_chat_engine_with_memory(session_id, service_name)

    # Render chat history
    for message in st.session_state.messages:
        avatar = USER_AVATAR if message["role"] == "user" else BOT_AVATAR
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    # Input for new messages
    prompt = st.chat_input("Your question")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user", avatar=USER_AVATAR):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                agent_response = asyncio.run(get_agent_response(prompt, service_name, session_id))
                text_response = agent_response
                rel_score = 0.9 #response.source_nodes[0].score
                url =  None #response.source_nodes[0].metadata.get('url')

                # Remove duplicate output: do NOT display the raw response object
                # st.write(response)  # <-- This line is removed

                # Only display the assistant's response in the chat
                if rel_score > 0.7:
                    if url:
                        if not url.startswith("http://") and not url.startswith("https://"):
                            url = "http://" + url
                        url_markdown = f"[Learn More]({url})"
                        final_response = f'{text_response} \n\n {url_markdown}'
                        st.markdown(final_response)
                        message = {"role": "assistant", "content": final_response}
                        st.session_state.messages.append(message)
                    else:
                        # If the URL is None, just show the text response
                        st.markdown(text_response)
                        message = {"role": "assistant", "content": text_response}
                        st.session_state.messages.append(message)
                else:
                    support_text = '''
                        \n If you need assistance on the platform, please reach out to the Jobbatical support team for guidance.
                    '''
                    if url:
                        text_response = support_text
                        st.markdown(text_response)
                    else:
                        st.markdown(text_response)
                    message = {"role": "assistant", "content": text_response}
                    st.session_state.messages.append(message)

        st.rerun()
