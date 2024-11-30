from PIL import Image as PILImage
import os
from typing import Annotated
from typing_extensions import TypedDict

from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

from common.config import load_config

config = load_config()

memory = MemorySaver()


class State(TypedDict):
    messages: Annotated[list, add_messages]


# Создание графа
graph_builder = StateGraph(State)


# --Создание модели чат-бота--
llm = ChatOpenAI(model='gpt-4o-mini', api_key=config.openai.api_key)


# Нода чат-бота
def chatbot(state: State):
    return {'messages': [llm.invoke(state['messages'])]}


# Добавление ноды в граф
graph_builder.add_node('chatbot', chatbot)


# --Инструмент TAVILY--
tool = TavilySearchResults(max_results=2)
tools = [tool]
# Создание ноды инструментов
tool_node = ToolNode(tools=[tool])
# Добавление ноды в граф
graph_builder.add_node('tools', tool_node)


# --CREATING EDGES--

# Условное ветвление с ноды CHATBOT
graph_builder.add_conditional_edges(
    'chatbot',
    tools_condition,
    {'tools': 'tools', END: END}
)

# Ребра
graph_builder.add_edge(START, 'chatbot')
graph_builder.add_edge('tools', 'chatbot')


# --Компиляция графа--
graph = graph_builder.compile()


# Функция для обработки ввода пользователя и вывода ответов модели
def stream_graph_updates(user_input: str):
    for event in graph.stream({'messages': [('user', user_input)]}):
        for value in event.values():
            print('AI: ', value['messages'][-1])


# Основной цикл общения с моделью
while True:
    try:
        user_input = input('User: ')
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break

        stream_graph_updates(user_input=user_input)

    except Exception as e:
        print(f"An error occurred: {e}")
        break


# Отображение картинки
try:
    # Ensure the 'pics' directory exists
    os.makedirs('./pics', exist_ok=True)

    # Get image data from the method
    image_data = graph.get_graph().draw_mermaid_png()

    # Save the image data to a file
    image_path = './pics/graph.png'
    with open(image_path, 'wb') as f:
        f.write(image_data)

    # Open and display the image using PIL
    img = PILImage.open(image_path)
    img.show()
except Exception as e:
    print(f"An error occurred: {e}")
