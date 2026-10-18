from datetime import datetime,timezone
from uuid import uuid4
from sqlalchemy import Boolean,DateTime,Float,ForeignKey,Index,Integer,JSON,String,Text,UniqueConstraint
from sqlalchemy.orm import Mapped,mapped_column,relationship
from .database import Base
def utcnow(): return datetime.now(timezone.utc)
class Patient(Base):
 __tablename__='patients'
 id:Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid4()))
 code:Mapped[str]=mapped_column(String(32),unique=True,index=True)
 display_name:Mapped[str]=mapped_column(String(100)); age_band:Mapped[str]=mapped_column(String(30),default='Fictional adult')
 synthetic:Mapped[bool]=mapped_column(Boolean,default=True,nullable=False); created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow,nullable=False)
 assessments:Mapped[list['AssessmentSession']]=relationship(back_populates='patient',cascade='all, delete-orphan'); observations:Mapped[list['Observation']]=relationship(back_populates='patient',cascade='all, delete-orphan')
class AssessmentSession(Base):
 __tablename__='assessment_sessions'
 id:Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid4())); patient_id:Mapped[str]=mapped_column(ForeignKey('patients.id',ondelete='CASCADE'),index=True)
 status:Mapped[str]=mapped_column(String(20),default='ready',nullable=False); started_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow,nullable=False); completed_at:Mapped[datetime|None]=mapped_column(DateTime(timezone=True))
 config:Mapped[dict]=mapped_column(JSON,default=dict,nullable=False); provenance:Mapped[str]=mapped_column(String(60),default='synthetic_simulation'); error_message:Mapped[str|None]=mapped_column(Text); idempotency_key:Mapped[str|None]=mapped_column(String(100),unique=True)
 patient:Mapped['Patient']=relationship(back_populates='assessments'); observation:Mapped['Observation|None']=relationship(back_populates='assessment',uselist=False)
class Observation(Base):
 __tablename__='observations'; __table_args__=(UniqueConstraint('assessment_id',name='uq_observation_assessment'),Index('ix_observation_patient_time','patient_id','observed_at'))
 id:Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid4())); patient_id:Mapped[str]=mapped_column(ForeignKey('patients.id',ondelete='CASCADE'),index=True); assessment_id:Mapped[str]=mapped_column(ForeignKey('assessment_sessions.id',ondelete='CASCADE'),unique=True)
 observed_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow,nullable=False); longest_mm:Mapped[float]=mapped_column(Float); width_mm:Mapped[float]=mapped_column(Float); depth_mm:Mapped[float|None]=mapped_column(Float); volume_mm3:Mapped[float|None]=mapped_column(Float)
 unit:Mapped[str]=mapped_column(String(12),default='mm'); method:Mapped[str]=mapped_column(String(100),default='deterministic_demo_algorithm'); provenance:Mapped[str]=mapped_column(String(60),default='synthetic_simulation'); quality:Mapped[dict]=mapped_column(JSON,default=dict); synthetic:Mapped[bool]=mapped_column(Boolean,default=True)
 patient:Mapped['Patient']=relationship(back_populates='observations'); assessment:Mapped['AssessmentSession']=relationship(back_populates='observation'); measurements:Mapped[list['Measurement']]=relationship(back_populates='observation',cascade='all, delete-orphan')
class Measurement(Base):
 __tablename__='measurements'
 id:Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid4())); observation_id:Mapped[str]=mapped_column(ForeignKey('observations.id',ondelete='CASCADE'),index=True); kind:Mapped[str]=mapped_column(String(40)); value:Mapped[float]=mapped_column(Float); unit:Mapped[str]=mapped_column(String(12),default='mm'); method:Mapped[str]=mapped_column(String(100),default='deterministic_demo_algorithm'); quality:Mapped[str]=mapped_column(String(30),default='illustrative'); observation:Mapped['Observation']=relationship(back_populates='measurements')
class SimulatedTelemetrySample(Base):
 __tablename__='simulated_telemetry_samples'
 id:Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid4())); assessment_id:Mapped[str]=mapped_column(ForeignKey('assessment_sessions.id',ondelete='CASCADE'),index=True); sample_index:Mapped[int]=mapped_column(Integer); progress:Mapped[float]=mapped_column(Float); signal_quality:Mapped[float]=mapped_column(Float); recorded_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow)
class TwinStateVersion(Base):
 __tablename__='twin_state_versions'
 id:Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid4())); patient_id:Mapped[str]=mapped_column(ForeignKey('patients.id',ondelete='CASCADE'),index=True); observation_id:Mapped[str]=mapped_column(ForeignKey('observations.id',ondelete='CASCADE'),unique=True); version:Mapped[int]=mapped_column(Integer); created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow)
class AuditEvent(Base):
 __tablename__='audit_events'
 id:Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid4())); event_type:Mapped[str]=mapped_column(String(60)); entity_id:Mapped[str]=mapped_column(String(36),index=True); created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow); details:Mapped[dict]=mapped_column(JSON,default=dict)
