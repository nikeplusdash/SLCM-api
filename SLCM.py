import requests
from bs4 import BeautifulSoup
import pytesseract
from PIL import Image

LOGIN_URL = 'https://slcm.manipal.edu/'
getDetails = lambda soup: {'txtCaptcha': pytesseract.image_to_string(Image.open(s.get(LOGIN_URL + soup.select('#imgCaptcha')[0]['src'], stream=True).raw)).strip(),'__EVENTVALIDATION': soup.select('#__EVENTVALIDATION')[0]['value'],'__VIEWSTATEGENERATOR': soup.select('#__VIEWSTATEGENERATOR')[0]['value'],'__VIEWSTATE': soup.select('#__VIEWSTATE')[0]['value']}
login_payload = {
    'txtUserid': '',
    'txtpassword': '',
    'btnLogin': 'Sign%20in',
    'txtCaptcha': ''
}
TIMEOUT = 30

#   Create a user.txt file containing username and password
#   in following format:
#
#   <username> <password>

f = open('user.txt','r')
u,p = f.read().strip().split(' ')
login_payload.update({'txtUserid': u,'txtpassword': p})
pytesseract.pytesseract.tesseract_cmd = r'D:\\Program Files\\Tesseract-OCR\\tesseract.exe'
s =  requests.Session()
status = None
try:
    # Logging In
    soup = BeautifulSoup(s.get(LOGIN_URL,timeout=TIMEOUT).text,'html.parser')
    login_payload.update(getDetails(soup))
    r = s.post(LOGIN_URL, data=login_payload)
    if len(r.history) == 1:
        status = 200
    else:
        status = 401

    if status == 200:
        # Basic Details
        soup = BeautifulSoup(s.post('https://slcm.manipal.edu/StudentProfile.aspx',timeout=TIMEOUT).text,'html.parser')
        reg_no,app_no,name,a_year,branch,doj,bday,gsex,pno,eno,email = [i['value'] for i in soup.select('input.form-control')[:11]]
        print("Hi {0},\nYou are using the SLCM-API.\n".format(name))

        # Attendance Details
        soup = BeautifulSoup(s.post('https://slcm.manipal.edu/Academics.aspx',timeout=TIMEOUT).text,'html.parser')
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
        subcode = list()
        sublist = list()
        for i in attendance:
            subcode.append(''.join(i['CODE'].split(' ')))
            sublist.append(i['SUBJECT'])
            print('Your attendance in {} is {}%'.format(i['SUBJECT'],i['PERCENTAGE']))

        # Marks Details
        marks = list()
        for i,y in enumerate(subcode):
            submarks = dict()
            submarks['CODE'] = y
            submarks['SUBJECT'] = sublist[i]
            submarkslist = list()
            data = [[l.contents[0] for l in k.find_all('td')] for j in soup.find(id=y).find_all('table') for k in j.find_all('tr')[1:-1]]
            for i in data:
                subsubmarks = dict()
                subsubmarks['NAME'],subsubmarks['MAX'],subsubmarks['OBTAINED'] = i[0],float(i[1]),float(i[2])
                submarkslist.append(subsubmarks)
            submarks['MARKS'] = submarkslist
            marks.append(submarks)
        for i in marks:
            print('{}: {}'.format(i['CODE'],i['SUBJECT']))
            for j in i['MARKS']:
                print('\t{}: {}/{}'.format(j['NAME'],j['OBTAINED'],j['MAX']))
except requests.exceptions.ConnectionError:
    status = 404
except requests.exceptions.ReadTimeout:
    status = 400
except Exception as e:
    status = 418
finally:
    if status == 200:
        print('\n + + + + + + + + Connection Successful + + + + + + + + \n')
    elif status == 401:
        print("\n + + + + + + + + Invalid Credentials + + + + + + + + \n")
    elif status == 404:
        print("\n + + + + + + + + Connection not established + + + + + + + + \n")
    elif status == 400:
        print('\n + + + + + + + + Connection Timed out + + + + + + + + \n')
    elif status == 418:
        print("\n + + + + + + + + Exception occured + + + + + + + + \n")
s.close()