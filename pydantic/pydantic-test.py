from pydantic import BaseModel


class User(BaseModel):
    idnum: int
    # username: str

    # @field_validator("username", mode="after")
    # @classmethod
    # def is_josh(cls, value: str) -> str:
    #     if value != 'josh':
    #         raise ValueError(f'idek')
    #     return value


u = User(idnum=8, username="josh")
