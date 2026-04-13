from pydantic import BaseModel, ConfigDict, EmailStr


class User(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    email: EmailStr
    full_name: str
    password_hash: str
