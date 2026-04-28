from sqlmodel import SQLModel


class Document(SQLModel):
    key: str
    text: str


class DocumentPublic(Document):
    pass