from datetime import datetime
from typing import Any
from pydantic import BaseModel,ConfigDict,Field
class PatientOut(BaseModel):
 model_config=ConfigDict(from_attributes=True)
 id:str; code:str; display_name:str; age_band:str; created_at:datetime; synthetic:bool
class MeasurementOut(BaseModel):
 model_config=ConfigDict(from_attributes=True)
 id:str; kind:str; value:float; unit:str; method:str; quality:str
class ObservationOut(BaseModel):
 model_config=ConfigDict(from_attributes=True)
 id:str; patient_id:str; assessment_id:str; observed_at:datetime; longest_mm:float; width_mm:float; depth_mm:float|None; volume_mm3:float|None; unit:str; method:str; provenance:str; quality:dict[str,Any]; synthetic:bool; measurements:list[MeasurementOut]=[]
class AssessmentCreate(BaseModel): patient_id:str; duration_seconds:int=Field(default=12,ge=5,le=120)
class AssessmentOut(BaseModel):
 model_config=ConfigDict(from_attributes=True)
 id:str; patient_id:str; status:str; started_at:datetime; completed_at:datetime|None; config:dict[str,Any]; observation_id:str|None; error_message:str|None
class ProcessRequest(BaseModel): note:str|None=None
class TwinStateOut(BaseModel): patient_id:str; observation:ObservationOut|None; version:int; provenance:str
