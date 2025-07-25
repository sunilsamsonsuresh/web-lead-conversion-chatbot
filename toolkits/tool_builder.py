import logging
from toolkits.chat_tool import ServiceChatTool
from toolkits.web_search import WebSearchTool

logger = logging.getLogger(__name__)


class ToolBuilder:
    def __init__(self, service_name):
        self.service_name = service_name

    def build_tools(self):

        service_chat_tool = ServiceChatTool(self.service_name).create_service_tool()
        web_search_tool = WebSearchTool().create_search_tool()

        tools = [service_chat_tool, web_search_tool]
        
        return tools
