from datetime import datetime,timedelta,timezone
from sqlalchemy import select
from .database import Base,SessionLocal,engine
from .models import Measurement,Observation,Patient,AssessmentSession,TwinStateVersion
def seed():
 Base.metadata.create_all(bind=engine)
 with SessionLocal() as db:
  if db.scalar(select(Patient.id).limit(1)):print('Seed skipped: records already exist.');return
  now=datetime.now(timezone.utc);p1=Patient(code='PP-DEMO-001',display_name='Avery Morgan',age_band='30–39 (fictional)',synthetic=True);p2=Patient(code='PP-DEMO-002',display_name='Jordan Ellis',age_band='40–49 (fictional)',synthetic=True);db.add_all([p1,p2]);db.flush()
  for idx,(days,longest,width,depth) in enumerate([(90,11.2,6.4,4.9),(60,11.5,6.5,5.0),(30,11.8,6.7,5.1)]):
   started=now-timedelta(days=days,minutes=3);sess=AssessmentSession(id=f'seed-assessment-{idx+1}',patient_id=p1.id,status='completed',started_at=started,completed_at=started+timedelta(minutes=1),config={'mode':'simulated','seeded':True},provenance='synthetic_seed');db.add(sess);db.flush()
   obs=Observation(id=f'seed-observation-{idx+1}',patient_id=p1.id,assessment_id=sess.id,observed_at=now-timedelta(days=days),longest_mm=longest,width_mm=width,depth_mm=depth,volume_mm3=round(3.14159/6*longest*width*depth,2),unit='mm',method='deterministic_demo_algorithm',provenance='synthetic_seed',quality={'synthetic':True,'geometry':'illustrative'},synthetic=True);db.add(obs);db.flush()
   for kind,value in [('longest',longest),('width',width),('depth',depth)]:db.add(Measurement(observation_id=obs.id,kind=kind,value=value,unit='mm',method='deterministic_demo_algorithm',quality='illustrative'))
   db.add(TwinStateVersion(patient_id=p1.id,observation_id=obs.id,version=idx+1))
  db.commit();print('Seeded 2 fictional patients and 3 historical observations.')
if __name__=='__main__':seed()
