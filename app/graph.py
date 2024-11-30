from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from langchain_openai import ChatOpenAI
from common.config import load_config

from PIL import Image as PILImage
import os

config = load_config()


class State(TypedDict):
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)

llm = ChatOpenAI(model='gpt-3.5-turbo', api_key=config.openai.api_key)


# Нода чат-бота
def chatbot(state: State):
    return {'messages': [llm.invoke(state['messages'])]}


# Добавление ноды
graph_builder.add_node('chatbot', chatbot)
# Создание связей
graph_builder.add_edge(START, 'chatbot')
graph_builder.add_edge('chatbot', END)
# Компиляция графа
graph = graph_builder.compile()


# Функция для обработки ввода пользователя и вывода ответов модели
def stream_graph_updates(user_input: str):
    for event in graph.stream({'messages': [('user', user_input)]}):
        for value in event.values():
            print('AI: ', value['messages'][-1].content)


# Основной цикл общения с моделью
while True:
    try:
        user_input = input('User: ')
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break

        stream_graph_updates(user_input=user_input)  # IMPORTANT

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
