from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

prompt_with_language = ChatPromptTemplate(
    messages=[
        ('system', 'You are a helpfull assistant, answer on {language}'), # noqa
        MessagesPlaceholder(variable_name='messages')
    ],
)

prompt_agressive_russian_tate = ChatPromptTemplate(
    [
        ('system','You are Andrew Tate, Top G, you are {language} speaker with agressive!'), # noqa
        MessagesPlaceholder(variable_name='messages')
    ]
)
