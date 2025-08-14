from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class FolderBase(BaseModel):
    name: str
    parent_id: Optional[int] = None

class FolderCreate(FolderBase):
    pass

class Folder(FolderBase):
    id: int
    created_at: datetime
    children: List['Folder'] = []

    class Config:
        from_attributes = True  # orm_modeの代わりにfrom_attributesを使用

# 循環参照を解決するために、後から追加
Folder.update_forward_refs()