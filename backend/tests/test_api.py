from datetime import datetime,timezone,timedelta
from fastapi.testclient import TestClient
from app.main import app,aware_utc
from app.seed import seed
client=TestClient(app)
def test_timezone_normalization():
 naive=datetime(2026,1,1,12);aware=datetime(2026,1,1,14,tzinfo=timezone(timedelta(hours=2)))
 assert aware_utc(naive).utcoffset()==timedelta(0);assert aware_utc(aware)==datetime(2026,1,1,12,tzinfo=timezone.utc)
def test_health_endpoint():
 r=client.get('/api/health');assert r.status_code==200;assert r.json()['status']=='ok'
def test_patient_and_observation_routes():
 seed();patients=client.get('/api/patients').json();assert len(patients)>=2
 p=next(x for x in patients if x['code']=='PP-DEMO-001');rows=client.get(f"/api/patients/{p['id']}/observations");assert rows.status_code==200;assert len(rows.json())>=3
