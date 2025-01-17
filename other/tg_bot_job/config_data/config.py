from dataclasses import dataclass
from environs import Env
from dotenv import load_dotenv
import os
load_dotenv()

GROUP_CHAT_ID = os.getenv('GROUP_CHAT_ID') 

@dataclass
class TgBot: 
    token: str 

@dataclass
class Config: 
    tg_bot: TgBot


def load_config(path: str | None = None) -> Config: 
    env = Env()
    env.read_env(path)
    return Config(tg_bot=TgBot(token=env('JOB_BOT_TOKEN'))
                  )

