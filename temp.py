import requests
from bs4 import BeautifulSoup

LOGIN_URL = 'https://slcm.manipal.edu/'
getDetails = lambda soup: {'__EVENTVALIDATION': soup.select('#__EVENTVALIDATION')[0]['value'],'__VIEWSTATEGENERATOR': soup.select('#__VIEWSTATEGENERATOR')[0]['value'],'__VIEWSTATE': soup.select('#__VIEWSTATE')[0]['value']}
login_payload = {
    'txtUserid': '',
    'txtpassword': '',
    'btnLogin': 'Sign%20in',
}
TIMEOUT = 30


s =  requests.Session()
status = None
soup = BeautifulSoup(s.get(LOGIN_URL,timeout=TIMEOUT).text,'html.parser')
login_payload.update(getDetails(soup))
r = s.post(LOGIN_URL, data=login_payload)
if len(r.history) == 1:
    soup = BeautifulSoup(s.post('https://slcm.manipal.edu/StudentProfile.aspx',timeout=TIMEOUT).text,'html.parser')
    reg_no,app_no,name,a_year,branch,doj,bday,gsex,pno,eno,email = [i['value'] for i in soup.select('input.form-control')[:11]]
    print("Hi {0},\nYou are using the SLCM-API.\n".format(name))    
    soup = BeautifulSoup(s.post('https://slcm.manipal.edu/GradeSheet.aspx',timeout=TIMEOUT).text,'html.parser')
    with open("index.html",'w') as f:
        f.write(str(soup))
else:
    status = 401