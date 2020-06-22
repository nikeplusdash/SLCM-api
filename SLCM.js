// const rp = require('request-promise');
const fs = require('fs') 
const fetch = require("node-fetch");
const $ = require('cheerio');
const { cookie } = require('request-promise');

const LOGIN_URL = 'https://slcm.manipal.edu/'
let login_payload = {
    'txtUserid': '',
    'txtpassword': '',
    'btnLogin': 'Sign%20in',
    '__EVENTVALIDATION': '',
    '__VIEWSTATEGENERATOR': '',
    '__VIEWSTATE': '',
    '__ASYNCPOST': 'true'
}

async function urlEncoded(data) {
    var str = []
    for(var i in data) {
        if(data.hasOwnProperty(i))
        str.push(encodeURIComponent(i) + "=" + encodeURIComponent(data[i]))                  
    }
    return str.join('&')
}

async function POST(url,data) {
    const response = fetch(url,{
        'method': 'POST',
        'header': {
            'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'
        },
        'body': data,
        'Connection': 'keep-alive',
        'Cookie': cookie
    })
    return response
}

async function GET(url) {
    const response = fetch(url,{
        'method': 'GET',
        'header': {
            'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'
        },
        'Connection': 'keep-alive',
        'Cookie': cookie
    })
    return response
}

// rp(LOGIN_URL)
GET(LOGIN_URL)
    .then(data=>data.body._readableState.buffer.head.data.toString('utf-8'))
    .then((html)=>{
        let data = fs.readFileSync('user.txt','utf-8').split(' ')
        login_payload.txtUserid = data[0]
        login_payload.txtpassword = data[1]
        login_payload.__EVENTVALIDATION = $('#__EVENTVALIDATION',html)['0'].attribs.value
        login_payload.__VIEWSTATEGENERATOR = $('#__VIEWSTATEGENERATOR',html)['0'].attribs.value
        login_payload.__VIEWSTATE = $('#__VIEWSTATE',html)['0'].attribs.value
    })
    .then(()=>{
        urlEncoded(login_payload)
            .then(data=>POST(LOGIN_URL,data))
            .then((data)=>{
                console.log(data.body._readableState.buffer.head.data.toString('utf-8'))
            })
            .catch((err)=>{
                console.log(err)
            })
    })
    .catch((err)=>{
        console.log(err)
    })
// POST(LOGIN_URL,(urlEncoded(login_payload).then(data=>data)))
//     .then(data=>data.body._readableState.buffer.head.data.toString('utf-8'))
//     .then(data=>console.log(data))