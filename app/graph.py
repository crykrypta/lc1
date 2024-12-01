import os
from dotenv import load_dotenv

from PIL import Image as PILImage

from typing import Annotated
from typing_extensions import TypedDict

from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.runnables.config import RunnableConfig
from langchain_core.messages import AIMessage, ToolMessage

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

from common.config import load_config

# Загрузка конфигурации
config = load_config()

# Создание экземпляра памяти
memory = MemorySaver()


# Загрузка переменных окружения
load_dotenv()
tavily_apik = os.getenv("TAVILY_API_KEY")

if not tavily_apik:
    raise ValueError("API KEY is not set in the environment.")


# Создание структуры для State Graph
# На основе TypedDict
class State(TypedDict):
    messages: Annotated[list, add_messages]


# Создание графа
graph_builder = StateGraph(State)


# --Инструмент TAVILY--
tool = TavilySearchResults(max_results=2)
tools = [tool]
# Создание ноды инструментов
tool_node = ToolNode(tools=[tool])

# --Создание модели чат-бота--
llm = ChatOpenAI(model='gpt-4o-mini', api_key=config.openai.api_key)
# Привязка инструментов к модели
llm_with_tools = llm.bind_tools(tools=tools)


# Нода чат-бота
def chatbot(state: State):
    # print('CHATBOT STATE: ', state)
    # response = llm_with_tools.invoke(state['messages'])
    # print('RESPONSE: ', response)
    return {'messages': [llm_with_tools.invoke(state['messages'])]}


# --ADDING NODES--
# Добавление ноды инструментов в граф
graph_builder.add_node('tools', tool_node)
# Добавление ноды чатбота в граф
graph_builder.add_node('chatbot', chatbot)

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
graph = graph_builder.compile(checkpointer=memory)


memory_config = RunnableConfig(configurable={'thread_id': 1})
# Основной цикл общения с моделью
while True:
    try:
        user_input = input('User: ')
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break

        events = graph.stream(
            {'messages': [('user', user_input)]},
            config=memory_config,
            stream_mode='values'
        )

        for event in events:
            if 'messages' in event:
                for message in event['messages']:
                    if isinstance(message, AIMessage):
                        print('AI: ', message.content)
                    elif isinstance(message, ToolMessage):
                        print('Tool: ', message.content)
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
