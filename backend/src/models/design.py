from pydantic import BaseModel


class ProjectDesign(BaseModel):
    id: str
    project_id: str
    title: str
    description: str
    file_url: str
    file_type: str
    uploaded_by: str
    uploaded_at: str


class ProjectDesignCreate(BaseModel):
    title: str
    description: str
    file_url: str
    file_type: str
