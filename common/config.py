from dataclasses import dataclass
from environs import Env
from pydantic import SecretStr


@dataclass
class Bot:
    api_key: str


@dataclass
class OpenAI:
    api_key: SecretStr


@dataclass
class Config:
    bot: Bot
    openai: OpenAI


def load_config() -> Config:
    env = Env()
    env.read_env()
    return Config(
        bot=Bot(
            api_key=env.str("BOT_API_KEY")
        ),
        openai=OpenAI(
            api_key=SecretStr(env.str("OPENAI_API_KEY"))
        )
    )
