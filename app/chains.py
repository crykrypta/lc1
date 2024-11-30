from operator import itemgetter

from langchain_openai import ChatOpenAI

from langchain_core.chat_history import (BaseChatMessageHistory,         # Для типизации              # noqa
                                         InMemoryChatMessageHistory)     # Для реализации памяти      # noqa

from langchain_core.runnables.history import RunnableWithMessageHistory  # Для "оборачивания" модели  # noqa
from langchain_core.runnables.config import RunnableConfig
from langchain_core.runnables import RunnablePassthrough

from langchain_core.messages import HumanMessage, trim_messages

from app.prompt_tmp import prompt_agressive_russian_tate
from common.config import load_config

config = load_config()


# Новая чат-модель
llm = ChatOpenAI(model='gpt-3.5-turbo',
                 api_key=config.openai.api_key)


# Триммер сообщений
trimmer = trim_messages(
    max_tokens=64,
    strategy='last',
    token_counter=llm,
    include_system=True,
    allow_partial=False,
    start_on='human',
)
# chain = prompt_agressive_russian_tate | llm
chain = (
    RunnablePassthrough.assign(messages=itemgetter('messages') | trimmer)
    | prompt_agressive_russian_tate
    | llm
)

# Временное хранилище истории сообщений
store = {}


# Функция для получения истории сессии
def get_session_history(session_id) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]


# Оборачиваем модель
chain_with_memory = RunnableWithMessageHistory(
    chain,   # type: ignore
    get_session_history,
    input_messages_key='messages'
)


while True:
    query = input('User: ')
    if query in ['stop', 'exit', 'стоп']:
        break
    # Создаем обьект Конфигурации истории диалога
    runnable_config = RunnableConfig(configurable={'session_id': 1})
    # Даем запрос в модель
    print('AI:', end=' ')
    try:
        for chunk in chain_with_memory.stream(
                {
                    'messages': [HumanMessage(content=query)],
                    'language': 'Russian'
                },
                config=runnable_config
        ):
            # print(f'AI: {chunk.content}')

            print(chunk.content, end='', flush=True)
        print()
    except Exception as e:
        print(f'Ошибка: {e}')
