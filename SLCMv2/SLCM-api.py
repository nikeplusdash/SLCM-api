import uvicorn
import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI,status,HTTPException,Depends,Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from base64 import b64encode

LOGIN_URL = 'https://slcm.manipal.edu/'
getDetails = lambda soup: {'__EVENTVALIDATION': soup.select('#__EVENTVALIDATION')[0]['value'],'__VIEWSTATEGENERATOR': soup.select('#__VIEWSTATEGENERATOR')[0]['value'],'__VIEWSTATE': soup.select('#__VIEWSTATE')[0]['value']}
login_payload = {
    'txtUserid': '',
    'txtpassword': '',
    'btnLogin': 'Sign%20in',
}
tags_metadata = [
    {
        'name': 'SLCM-api',
        'description': 'Retrieval of User data, attendance, academics'
    },
    {
        'name': 'Authenticate',
        'description': 'Verification of User for account creation purposes'
    }
]

class UserData(BaseModel):
    reg_no: str
    app_no: str
    name: str
    acad_year: str
    branch: str
    date_of_join: str
    birthday: str
    sex: str
    phone_no: str
    email: str

class Verify(BaseModel):
    status: int
    message: str
    body: UserData

class User(BaseModel):
    session: bool

s =  requests.Session()
security = HTTPBasic()
app = FastAPI(title='SLCM-api',description='Helps retrieval of data from https://slcm.manipal.edu',redoc_url=None,openapi_tags=tags_metadata)

def auth_required(credentials: HTTPBasicCredentials = Depends(security)):
    try:
        username,password = credentials.username,credentials.password
        login_payload.update({'txtUserid': username,'txtpassword': password})
        soup = BeautifulSoup(s.get(LOGIN_URL,timeout=10).text,'html.parser')
        login_payload.update(getDetails(soup))
        r = s.post(LOGIN_URL, data=login_payload,timeout=10)
        if len(r.history) == 1:
            return True
        else:
            raise requests.exceptions.RequestException
    except requests.exceptions.ConnectionError:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='Connection Error')
    except requests.exceptions.ReadTimeout:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail='Connection Timed out')
    except requests.exceptions.RequestException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Incorrect email or password",headers={"WWW-Authenticate": "Basic"})
    except Exception as e:
        raise HTTPException(status_code=418,detail='Unknown Error Occurred ({})'.format(e))

@app.get('/',tags=['SLCM-api','Authenticate'],summary='Navigation for API')
async def root():
    return {
        '[GET] /': 'Landing Page',
        '[POST] /login': 'to login',
        '[POST] /attendance': 'returns attendance object',
        '[POST] /academics': 'returns academics object',
        '[POST] /verify': 'returns verification of the ',
        '[GET] /logout': 'end current session'
    }

@app.post('/login',tags=['SLCM-api'],summary='Creates a login session for app')
async def login(username:str,password:str):
    pass

@app.get('/attendance',tags=['SLCM-api'],summary='Returns attendance object')
async def attendance(auth=Depends(auth_required)):
    soup = BeautifulSoup(s.post('https://slcm.manipal.edu/Academics.aspx',timeout=10).text,'html.parser')
    attend = soup.select('#tblAttendancePercentage')[0].tbody.find_all('tr')
    segregate = [[j.contents[0] for j in i.find_all('td')[1:-1]] for i in attend]
    attendance = list()
    for i in segregate:
        sub = dict()
        sub['CODE'],sub['SUBJECT'],sub['SEM'],d,e,f = i
        sub['TOTAL'],sub['PRESENT'],sub['ABSENT']  = int(d),int(e),int(f)
        try:
            sub['PERCENTAGE'] = round(float(sub['PRESENT'])/float(sub['TOTAL'])*100,2)
        except ZeroDivisionError:
            sub['PERCENTAGE'] = 100
        attendance.append(sub)
    return attendance

@app.get('/academics',tags=['SLCM-api'],summary='Returns academic object')
async def academics(auth=Depends(auth_required)):
    soup = BeautifulSoup(s.post('https://slcm.manipal.edu/Academics.aspx',timeout=10).text,'html.parser')
    attend = soup.select('#tblAttendancePercentage')[0].tbody.find_all('tr')
    segregate = [[j.contents[0] for j in i.find_all('td')[1:-1]] for i in attend]
    subcode = list()
    sublist = list()
    for i in segregate:
        subcode.append(''.join(i[0].split(' ')))
        sublist.append(i[1])
    marks = list()
    for i,y in enumerate(subcode):
        submarks = dict()
        submarks['CODE'] = y
        submarks['SUBJECT'] = sublist[i]
        submarkslist = list()
        data = [[l.contents[0] for l in k.find_all('td')] for j in soup.find(id=subcode[0]).find_all('table') for k in j.find_all('tr')[1:-1]]
        for i in data:
            subsubmarks = dict()
            subsubmarks['NAME'],subsubmarks['MAX'],subsubmarks['OBTAINED'] = i[0],float(i[1]),float(i[2])
            submarkslist.append(subsubmarks)
        submarks['MARKS'] = submarkslist
        marks.append(submarks)
    return marks


@app.post('/verify',response_model=Verify,tags=['Authenticate'],summary='Used for verification',description='This will verify the user and return only necessary data as response. This can be used for verifying new users')
async def verify(auth=Depends(auth_required)):
    soup = BeautifulSoup(s.post('https://slcm.manipal.edu/StudentProfile.aspx',timeout=10).text,'html.parser')
    data = [i['value'] for i in soup.select('input.form-control')[:11]]
    return {'status': 200,'message':'success','body': {'reg_no':data[0],'app_no':data[1],'name':data[2],'acad_year':data[3],'branch':data[4],'date_of_join':data[5],'birthday':data[6],'sex':data[7],'phone_no':data[8],'email':data[10]}}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)