from typing import Optional

from pydantic import BaseModel


class SettingState(BaseModel):
    wandb_username: Optional[str]
    wandb_project: Optional[str]
    wandb_api_key: Optional[str]
    openai_api_key: Optional[str]


class AppState(BaseModel):
    settings_state: Optional[SettingState] = None