import os
import json

from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import ToolMessage
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()
os.getenv("TAVILY_API_KEY")


# Создание инструмента TAVILY
tool = TavilySearchResults(max_results=2)
tools = [tool]


# Создание базового класса для ноды-инструментов
class BaseToolNode:
    def __init__(self, tools) -> None:
        self.tools_dict = {tool.name: tool for tool in tools}

    def __call__(self, inputs: dict):
        if messages := inputs.get('messages', []):
            message = messages[-1]
        else:
            raise ValueError('No messages provided')

        outputs = []

        for tool_call in message.tool_calls:
            tools_result = self.tools_dict[tool_call['name']].invoke(
                tool_call['args']
            )
            outputs.append(
                ToolMessage(
                    content=json.dumps(tools_result),
                    name=tool_call['name'],
                    tool_call_id=tool_call['id'],
                )
            )
        return {'messages': outputs}
