import os
from datetime import datetime,timezone
from fastapi import Depends,FastAPI,Header,HTTPException,Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import desc,func,select
from sqlalchemy.orm import Session,selectinload
from .database import Base,engine,get_db
from .models import AssessmentSession,AuditEvent,Measurement,Observation,Patient,SimulatedTelemetrySample,TwinStateVersion,utcnow
from .schemas import AssessmentCreate,AssessmentOut,ObservationOut,PatientOut,ProcessRequest,TwinStateOut
app=FastAPI(title='POLYPULSE Research API',version='0.1.0',description='Synthetic research prototype. Not for clinical use.')
origins=[x.strip() for x in os.getenv('CORS_ORIGINS','http://localhost:5173,http://127.0.0.1:5173').split(',') if x.strip()]
app.add_middleware(CORSMiddleware,allow_origins=origins,allow_credentials=False,allow_methods=['GET','POST','OPTIONS'],allow_headers=['Content-Type','Idempotency-Key'])
Base.metadata.create_all(bind=engine)
def aware_utc(value:datetime|None):
 if value is None:return None
 if value.tzinfo is None or value.utcoffset() is None:return value.replace(tzinfo=timezone.utc)
 return value.astimezone(timezone.utc)
def oq():return select(Observation).options(selectinload(Observation.measurements))
@app.get('/api/health')
def health(db:Session=Depends(get_db)):
 db.execute(select(1));return {'status':'ok','database':'connected','provenance':'synthetic_demo'}
@app.get('/api/patients',response_model=list[PatientOut])
def patients(db:Session=Depends(get_db)):return db.scalars(select(Patient).order_by(Patient.display_name)).all()
@app.get('/api/patients/{patient_id}',response_model=PatientOut)
def patient(patient_id:str,db:Session=Depends(get_db)):
 row=db.get(Patient,patient_id)
 if not row:raise HTTPException(404,'Patient not found')
 return row
@app.get('/api/patients/{patient_id}/observations',response_model=list[ObservationOut])
def observations(patient_id:str,db:Session=Depends(get_db)):
 if not db.get(Patient,patient_id):raise HTTPException(404,'Patient not found')
 return db.scalars(oq().where(Observation.patient_id==patient_id).order_by(desc(Observation.observed_at))).all()
@app.get('/api/observations/{observation_id}',response_model=ObservationOut)
def observation(observation_id:str,db:Session=Depends(get_db)):
 row=db.scalar(oq().where(Observation.id==observation_id))
 if not row:raise HTTPException(404,'Observation not found')
 return row
@app.post('/api/assessments',response_model=AssessmentOut,status_code=201)
def create_assessment(payload:AssessmentCreate,db:Session=Depends(get_db)):
 if not db.get(Patient,payload.patient_id):raise HTTPException(404,'Patient not found')
 row=AssessmentSession(patient_id=payload.patient_id,status='ready',config={'duration_seconds':payload.duration_seconds,'mode':'simulated','algorithm':'deterministic_demo_algorithm'})
 db.add(row);db.flush();db.add(AuditEvent(event_type='assessment.created',entity_id=row.id,details={'patient_id':payload.patient_id,'synthetic':True}));db.commit();db.refresh(row);return row
@app.get('/api/assessments/{assessment_id}',response_model=AssessmentOut)
def get_assessment(assessment_id:str,db:Session=Depends(get_db)):
 row=db.get(AssessmentSession,assessment_id)
 if not row:raise HTTPException(404,'Assessment not found')
 return row
@app.post('/api/assessments/{assessment_id}/process',response_model=ObservationOut)
def process(assessment_id:str,payload:ProcessRequest,idempotency_key:str|None=Header(default=None,alias='Idempotency-Key'),db:Session=Depends(get_db)):
 session=db.scalar(select(AssessmentSession).where(AssessmentSession.id==assessment_id).with_for_update())
 if not session:raise HTTPException(404,'Assessment not found')
 if session.status=='cancelled':raise HTTPException(409,'Cancelled assessment cannot be processed')
 existing=db.scalar(oq().where(Observation.assessment_id==assessment_id))
 if existing:return existing
 if session.status=='completed':raise HTTPException(409,'Assessment completed but observation missing; inspect database')
 now=utcnow();started=aware_utc(session.started_at);elapsed=max(0,(aware_utc(now)-started).total_seconds()) if started else 0
 seed=sum(map(ord,session.id))%17;longest=round(10.5+seed*.31,2);width=round(6.2+(seed%7)*.27,2);depth=round(4.8+(seed%5)*.22,2);volume=round(3.14159/6*longest*width*depth,2)
 try:
  session.status='processing';db.flush()
  obs=Observation(patient_id=session.patient_id,assessment_id=session.id,observed_at=now,longest_mm=longest,width_mm=width,depth_mm=depth,volume_mm3=volume,unit='mm',method='deterministic_demo_algorithm',provenance='synthetic_simulation',quality={'elapsed_seconds':round(elapsed,2),'signal_quality':.94,'geometry':'illustrative','synthetic':True},synthetic=True)
  db.add(obs);db.flush()
  for kind,value in [('longest',longest),('width',width),('depth',depth)]:db.add(Measurement(observation_id=obs.id,kind=kind,value=value,unit='mm',method='deterministic_demo_algorithm',quality='illustrative'))
  for i in range(11):db.add(SimulatedTelemetrySample(assessment_id=session.id,sample_index=i,progress=i/10,signal_quality=round(.88+((seed+i)%10)/100,2),recorded_at=now))
  version=(db.scalar(select(func.max(TwinStateVersion.version)).where(TwinStateVersion.patient_id==session.patient_id)) or 0)+1
  db.add(TwinStateVersion(patient_id=session.patient_id,observation_id=obs.id,version=version));session.status='completed';session.completed_at=now;session.error_message=None
  if idempotency_key:session.idempotency_key=idempotency_key[:100]
  db.add(AuditEvent(event_type='assessment.completed',entity_id=session.id,details={'observation_id':obs.id,'synthetic':True}));db.commit()
  return db.scalar(oq().where(Observation.id==obs.id))
 except Exception:db.rollback();raise
@app.post('/api/assessments/{assessment_id}/cancel',response_model=AssessmentOut)
def cancel(assessment_id:str,db:Session=Depends(get_db)):
 row=db.get(AssessmentSession,assessment_id)
 if not row:raise HTTPException(404,'Assessment not found')
 if row.status=='completed':raise HTTPException(409,'A completed assessment cannot be cancelled')
 row.status='cancelled';row.completed_at=utcnow();db.add(AuditEvent(event_type='assessment.cancelled',entity_id=row.id,details={'synthetic':True}));db.commit();db.refresh(row);return row
@app.get('/api/patients/{patient_id}/twin-state',response_model=TwinStateOut)
def twin(patient_id:str,db:Session=Depends(get_db)):
 if not db.get(Patient,patient_id):raise HTTPException(404,'Patient not found')
 latest=db.scalar(oq().where(Observation.patient_id==patient_id).order_by(desc(Observation.observed_at)).limit(1));version=db.scalar(select(func.max(TwinStateVersion.version)).where(TwinStateVersion.patient_id==patient_id)) or 0
 return {'patient_id':patient_id,'observation':latest,'version':version,'provenance':'synthetic_simulation' if latest else 'no_observation'}
@app.get('/api/patients/{patient_id}/comparisons')
def compare(patient_id:str,from_id:str=Query(...),to_id:str=Query(...),db:Session=Depends(get_db)):
 if from_id==to_id:raise HTTPException(400,'Choose two different observations')
 rows=[db.scalar(oq().where(Observation.id=oid,Observation.patient_id==patient_id)) for oid in (from_id,to_id)]
 if any(r is None for r in rows):raise HTTPException(404,'Observation not found for this patient')
 a,b=rows;ta,tb=aware_utc(a.observed_at),aware_utc(b.observed_at);interval=abs((tb-ta).total_seconds())/86400
 return {'from':ObservationOut.model_validate(a),'to':ObservationOut.model_validate(b),'interval_days':round(interval,2),'deltas':{'longest_mm':round(b.longest_mm-a.longest_mm,2),'width_mm':round(b.width_mm-a.width_mm,2),'depth_mm':round(b.depth_mm-a.depth_mm,2) if a.depth_mm is not None and b.depth_mm is not None else None,'volume_mm3':round(b.volume_mm3-a.volume_mm3,2) if a.volume_mm3 is not None and b.volume_mm3 is not None else None}}
