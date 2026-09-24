from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.models.enums import DataSourceType

class DocumentUploadResponse(BaseModel):
    document_id: int
    file_name: str
    sha256: str
    processing_status: str
    data_source_type: DataSourceType
    message: str

class DocumentChunkSchema(BaseModel):
    id: int
    document_id: int
    chunk_index: int
    text: str
    page_number: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)