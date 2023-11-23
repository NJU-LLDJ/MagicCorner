from pydantic import BaseModel


class BaseConfig(BaseModel):
    @classmethod
    def from_file(cls, path: str):
        with open(path) as file:
            return cls.model_validate_json(file.read())
