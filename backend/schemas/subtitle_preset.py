from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Literal
from datetime import datetime
import uuid

FontName = Literal[
    "Arial", 
    "Roboto", 
    "Montserrat", 
    "Bebas Neue", 
    "Anton", 
    "Oswald", 
    "Impact"
]

AlignmentType = Literal["Left", "Center", "Right"]

class SubtitlePresetBase(BaseModel):
    name: str
    font_name: FontName = "Roboto"
    font_size: int = Field(default=48, ge=10, le=200)
    primary_color: str = "#FFFFFF"
    outline_color: str = "#000000"
    back_color: str = "#00000080"  # rgba or similar, ASS format
    margin_v: int = Field(default=20, ge=0)
    margin_l: int = Field(default=20, ge=0)
    margin_r: int = Field(default=20, ge=0)
    
    max_lines: int = Field(default=2, ge=1, le=5)
    uppercase: bool = False
    word_wrap: bool = True
    alignment: AlignmentType = "Center"

class SubtitlePresetCreate(SubtitlePresetBase):
    pass

class SubtitlePresetUpdate(BaseModel):
    name: Optional[str] = None
    font_name: Optional[FontName] = None
    font_size: Optional[int] = Field(default=None, ge=10, le=200)
    primary_color: Optional[str] = None
    outline_color: Optional[str] = None
    back_color: Optional[str] = None
    margin_v: Optional[int] = Field(default=None, ge=0)
    margin_l: Optional[int] = Field(default=None, ge=0)
    margin_r: Optional[int] = Field(default=None, ge=0)
    
    max_lines: Optional[int] = Field(default=None, ge=1, le=5)
    uppercase: Optional[bool] = None
    word_wrap: Optional[bool] = None
    alignment: Optional[AlignmentType] = None

class SubtitlePresetResponse(SubtitlePresetBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
