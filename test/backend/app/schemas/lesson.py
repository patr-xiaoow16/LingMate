from pydantic import BaseModel, Field


class SourcePayload(BaseModel):
    type: str = "url"
    url: str = ""
    transcript: str | None = None
    fileName: str | None = None
    mimeType: str | None = None


class ImportMaterialRequest(BaseModel):
    mode: str = "mock_url_import"
    source: SourcePayload


class ModuleActionRequest(BaseModel):
    action: str = Field(default="interact")
    label: str | None = Field(default=None)
    message: str | None = Field(default=None)
