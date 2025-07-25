import logging
import json
import os
import asyncio
# from utils.decision_agent import decision_maker
import streamlit as st
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from toolkits.tool_builder import ToolBuilder

logger = logging.getLogger(__name__)

class ToolExecutor:
    """
    Executes a sequence of tools (service_qa and search_ddg) for a given message and context.
    Streamlit-compliant: all methods are synchronous.
    """

    def __init__(self):
        pass

    # Streamlit-compliant: synchronous version
    async def execute_tool(self, tool, message):
        """
        Executes a tool using its _sync_fn method (must be synchronous for Streamlit).
        If message is a tuple, it will be unpacked as arguments.
        """
        if hasattr(tool, '_async_fn'):
            if isinstance(message, tuple):
                return await tool._async_fn(*message)
            else:
                return await tool._async_fn(message)
        else:
            raise AttributeError(f"Tool {tool} does not have a _async_fn method.")

    async def tool_executor(self, message, tools, session_id, service_name):
        """
        Executes service_qa, and if it has source_nodes, returns its response.
        Otherwise, executes search_ddg and returns its output.
        """
        tool_map = {tool.metadata.name: tool for tool in tools}
        tool_outputs = {}
        tool_sequence = []
        step_output = None

        # 1. Try service_qa first
        service_qa_tool = tool_map.get('service_qa')
        if not service_qa_tool:
            logger.error("service_qa tool not found.")
            return None, tool_outputs, tool_sequence

        tool_sequence.append('service_qa')
        try:
            if st is not None:
                with st.spinner("Running service_qa..."):
                    step_output = await self.execute_tool(service_qa_tool, (message, session_id))
            else:
                step_output = await self.execute_tool(service_qa_tool, (message, session_id))
            tool_outputs['service_qa'] = step_output
        except Exception as e:
            logger.error(f"Error executing service_qa: {e}")
            if st is not None:
                st.error(f"Error executing service_qa: {e}")
            step_output = None

        # Check for source_nodes in step_output
        has_sources = False
        source_nodes = None
        if step_output is not None:
            if hasattr(step_output, "source_nodes"):
                source_nodes = getattr(step_output, "source_nodes", None)
            elif isinstance(step_output, dict) and "source_nodes" in step_output:
                source_nodes = step_output["source_nodes"]
            if source_nodes and isinstance(source_nodes, (list, tuple)) and len(source_nodes) > 0:
                has_sources = True

        if has_sources:
            # Return the response from service_qa as the final response
            if hasattr(step_output, "response"):
                final_response = step_output.response
            elif isinstance(step_output, dict) and "response" in step_output:
                final_response = step_output["response"]
            else:
                final_response = step_output
            logger.info("service_qa provided sources. Returning its response.")
            return final_response

        # 2. If no sources, try web_search
        web_search_tool = tool_map.get('web_search')
        if not web_search_tool:
            logger.info("No sources from service_qa and web_search tool not found.")
            return None

        tool_sequence.append('web_search')
        try:
            if st is not None:
                with st.spinner("Running web_search..."):
                    web_search_output = await self.execute_tool(web_search_tool, (message, service_name))
            else:
                web_search_output = await self.execute_tool(web_search_tool, (message, service_name))
            tool_outputs['web_search'] = web_search_output
        except Exception as e:
            logger.error(f"Error executing web_search: {e}")
            if st is not None:
                st.error(f"Error executing web_search: {e}")
            web_search_output = None

        logger.info("Returning web_search output as final response.")
        return web_search_output

if __name__ == "__main__":
    tool_executor = ToolExecutor()
    message = "What is the cost of the Spanish citizenship package?"
    tools = ToolBuilder("spanish-citizenship-service").build_tools()
    session_id = "123"
    agent_response = asyncio.run(tool_executor.tool_executor(message, tools, session_id, "spanish-citizenship-service"))
    print(agent_response)