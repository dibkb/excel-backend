from pydantic import BaseModel
from typing import Dict


class Specifications(BaseModel):
    technical: Dict[str, str] = None
    additional: Dict[str, str] = None
    details: Dict[str, str] = None