import requests
from bs4 import BeautifulSoup

LOGIN_URL = 'https://slcm.manipal.edu/'
getDetails = lambda soup: {'__EVENTVALIDATION': soup.select('#__EVENTVALIDATION')[0]['value'],'__VIEWSTATEGENERATOR': soup.select('#__VIEWSTATEGENERATOR')[0]['value'],'__VIEWSTATE': soup.select('#__VIEWSTATE')[0]['value']}
login_payload = {
    'txtUserid': '',
    'txtpassword': '',
    'btnLogin': 'Sign%20in',
}

#   Create a user.txt file containing username and password
#   in following format:
#
#   <username> <password>

f = open('user.txt','r')
u,p = f.read().strip().split(' ')
login_payload.update({'txtUserid': u,'txtpassword': p})

with requests.Session() as s:
    status = None
    try:
        soup = BeautifulSoup(s.get(LOGIN_URL).text,'html.parser')
        login_payload.update(getDetails(soup))
        r = s.post(LOGIN_URL, data=login_payload)
        if len(r.history) == 1:
            status = 200
        else:
            status = 401
    except requests.exceptions.ConnectionError:
        status = 404
    except requests.exceptions.ReadTimeout:
        status = 400
    except Exception:
        status = 418
    finally:
        if status == 200:
            print('\n + + + + + + + + Connection Successful and Logged in + + + + + + + + \n')
        elif status == 401:
            print("\n + + + + + + + + Invalid Credentials + + + + + + + + \n")
        elif status == 404:
            print("\n + + + + + + + + Connection not established + + + + + + + + \n")
        elif status == 400:
            print('\n + + + + + + + + Connection Timed out + + + + + + + + \n')
        elif status == 418:
            print("\n + + + + + + + + I am a teapot + + + + + + + + \n")
    s.close()

if status == 200:
    soup = BeautifulSoup(s.post('https://slcm.manipal.edu/StudentProfile.aspx').text,'html.parser')
    reg_no,app_no,name,a_year,branch,doj,bday,gsex,pno,eno,email = [i['value'] for i in soup.select('input.form-control')[:11]]
    print("Hi {0},\nYou are using the SLCM-API.\n".format(name))
s.close()