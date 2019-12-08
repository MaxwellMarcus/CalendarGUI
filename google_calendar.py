from tkinter import *
from apiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from datetime import date
from datetime import time
from datetime import datetime
from datetime import timedelta
import pickle

root = Tk()
canvas = Canvas(root,width=root.winfo_screenwidth(),height=root.winfo_screenheight())
canvas.pack()
canvas.config(bg='black')

scroll = 0

def scroll_down(event):
    global scroll

    scroll += 10

def scroll_up(event):
    global scroll

    if scroll > 0:
        scroll -= 10

def get_time_from_datetime(dt):
    final = ''
    started = False
    for i in dt:
        if i == '-':
            started = False
        if started:
            final += i
        if i == 'T':
            started = True
    return final

def get_int_from_time(t):
    hours = ''
    in_hours = True
    minutes = ''
    in_minutes = False
    for i in t:
        if i == ':':
            in_minutes = True
            if not in_hours:
                in_minutes = False
            in_hours = False
        if in_hours:
            hours += i
        if in_minutes and not i == ':':
            minutes += i

    hours = int(hours)
    minutes = int(minutes)

    return hours*60+minutes

def get_hours_and_minutes(t):
    hours = ''
    in_hours = True
    minutes = ''
    in_minutes = False
    for i in t:
        if i == ':':
            in_minutes = True
            if not in_hours:
                in_minutes = False
            in_hours = False
        if in_hours:
            hours += i
        if in_minutes and not i == ':':
            minutes += i

    if int(hours) > 12:
        hours = str(int(hours)-12)
        minutes += ' PM'
    else:
        minutes += ' AM'

    time = hours+':'+minutes
    return time



scopes = ['https://www.googleapis.com/auth/calendar']

try:
    credentials = pickle.load(open('token.pkl','rb'))
    service = build('calendar','v3',credentials=credentials)
except:
    flow = InstalledAppFlow.from_client_secrets_file('C:/users/Max Marcus/Downloads/client_secret.json',scopes=scopes)
    credentials = flow.run_console()

    pickle.dump(credentials, open('token.pkl','wb'))

    service = build('calendar','v3',credentials=credentials)

calendar = service.calendarList().list().execute()
calendar_id = calendar['items'][1]['id']

today_beginning = datetime.utcnow()
today_end = today_beginning + timedelta(1, 0) - timedelta(0, 1)
today_beginning = today_beginning.isoformat() + 'Z'
today_end = today_end.isoformat() + 'Z'

timeToGetAgain = get_int_from_time(get_time_from_datetime(datetime.now().isoformat()))-3

root.bind('w',scroll_up)
root.bind('s',scroll_down)

while True:
    if timeToGetAgain+1 < get_int_from_time(get_time_from_datetime(datetime.now().isoformat())):
        events = service.events().list(calendarId=calendar_id,timeMin=today_beginning,timeMax=today_end).execute()
        timeToGetAgain = get_int_from_time(get_time_from_datetime(datetime.now().isoformat()))

    canvas.delete(ALL)

    y = 200
    for i in events['items']:
        start = get_time_from_datetime(i['start']['dateTime'])
        end = get_time_from_datetime(i['end']['dateTime'])

        start_val = get_int_from_time(start)
        end_val = get_int_from_time(end)

        multiplier = root.winfo_screenheight()-300
        multiplier /= 300

        time_offset = get_int_from_time(get_time_from_datetime(datetime.now().isoformat()))*multiplier

        y1 = start_val*multiplier+300-time_offset-scroll
        y2 = end_val*multiplier+300-time_offset-scroll

        canvas.create_rectangle(50,y1,root.winfo_screenwidth()-50,y2,fill='grey10',outline='red')#'grey35')
        canvas.create_text(root.winfo_screenwidth()/2,y1+15,anchor=CENTER,text=i['summary'],font=('TkTextFont',20),fill='grey50')
        canvas.create_text(root.winfo_screenwidth()/2,y1+40,anchor=CENTER,text=get_hours_and_minutes(start)+'-'+get_hours_and_minutes(end),font=('TkTextFont',10),fill='grey45')

    canvas.create_rectangle(0,0,root.winfo_screenwidth(),301,fill='black')
    canvas.create_text(root.winfo_screenwidth()/2,100,anchor=CENTER,text=get_hours_and_minutes(get_time_from_datetime(datetime.now().isoformat())),font=('TkTextFont',50),fill='grey55')

    root.update()
