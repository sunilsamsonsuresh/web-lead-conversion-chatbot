from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
import os
from llama_index.core.tools import FunctionTool
from utils.llm_model import llm
from llama_index.core.tools import ToolMetadata
from utils.prompts import web_search_prompt
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class WebSearchTool:
    """
    Class for searching queries using DuckDuckGo via an OpenAI Agent.
    """

    @staticmethod
    def web_search(query: str, service_name: str) -> str:
        """
        Search Web for the given query using the agent.
        """
        tools = [{
            "type": "web_search_preview",
        }]

        response = client.responses.create(
            model="gpt-4o-mini",
            input=[
                {"role": "system", "content": web_search_prompt.format(service_name=service_name)},
                {"role": "user", "content": query}
            ],
            tools=tools
        )
        return response.output_text

    def create_search_tool(self):
        return FunctionTool.from_defaults(
            fn=self.web_search,
            tool_metadata=ToolMetadata(
                name='web_search',
                description='Use this tool to search the web for up-to-date information using OpenAI.'
            )
        )