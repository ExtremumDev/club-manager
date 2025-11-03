import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel

import json

class Settings(BaseSettings):
    BOT_TOKEN: str

    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    
    # DATABASE_SQLITE = 'sqlite+aiosqlite:///data/db.sqlite3'
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    )

    def get_db_url(self):
        return (f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@"
                f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}")


class ChatSettings(BaseModel):
    GROUP_ID: str

    # topics in supergroup

    DATING_PROFILES_THREAD_ID: int
    INITIATIVES_THREAD_ID: int
    BUISNESS_MEETS_THREAD_ID: int
    WOMEN_MEETS_THREAD_ID: int
    FRENCH_CLUB_THREAD_ID: int
    TABLE_GAME_THREAD_ID: int

    ADMIN_CHAT_ID: int

    @classmethod
    def load_from_json(cls, json_file: str):
        with open(json_file, 'r') as f:
            data = json.load(f)
        return cls.parse_obj(data)

        
settings = Settings()

chat_settings = ChatSettings.load_from_json("chat_settings.json")