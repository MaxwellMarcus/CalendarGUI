from tkinter import *
from apiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from datetime import date
from datetime import time
from datetime import datetime
from datetime import timedelta
import pickle
import requests

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
    flow = InstalledAppFlow.from_client_secrets_file('client_secret.json',scopes=scopes)
    credentials = flow.run_console()

    pickle.dump(credentials, open('token.pkl','wb'))

    service = build('calendar','v3',credentials=credentials)

calendar = service.calendarList().list().execute()
calendar_id = calendar['items'][1]['id']

today_beginning = datetime.combine(datetime.now().date(), time())

tommorow_beginning = today_beginning + timedelta(1,0) + timedelta(hours=6)
tommorow_end = tommorow_beginning + timedelta(1,0) - timedelta(0,1)

tommorow_beginning = tommorow_beginning.isoformat() + 'Z'
tommorow_end = tommorow_end.isoformat() + 'Z'

two_days_beginning = today_beginning + timedelta(2,0) + timedelta(hours=6)
two_days_end = two_days_beginning + timedelta(2,0) - timedelta(0,1)

two_days_beginning = two_days_beginning.isoformat() + 'Z'
two_days_end = two_days_end.isoformat() + 'Z'

now = datetime.utcnow()

today_end = today_beginning + timedelta(1, 0) - timedelta(0, 1) + timedelta(hours=6)

today_beginning = now.isoformat() + 'Z'
today_end = today_end.isoformat() + 'Z'

weather_api_address = 'http://api.openweathermap.org/data/2.5/weather?appid=4b713022f58629805d9de8f92f2de92d&lat=38.579178&lon=-90.391050&units=Imperial'

cloud = PhotoImage(file='cloud.gif')
cloud = cloud.subsample(5,5)

timeToGetAgain = get_int_from_time(get_time_from_datetime(datetime.now().isoformat()))-3

root.bind('w',scroll_up)
root.bind('s',scroll_down)

while True:
    if timeToGetAgain+1 < get_int_from_time(get_time_from_datetime(datetime.now().isoformat())):
        events = service.events().list(calendarId=calendar_id,timeMin=today_beginning,timeMax=today_end).execute()
        timeToGetAgain = get_int_from_time(get_time_from_datetime(datetime.now().isoformat()))

        tommorow_events = service.events().list(calendarId=calendar_id,timeMin=tommorow_beginning,timeMax=tommorow_end,singleEvents=True,orderBy='startTime').execute() #Remember that single events is on. Make sure it doesn't cause any problems down the line
        two_days_events = service.events().list(calendarId=calendar_id,timeMin=two_days_beginning,timeMax=two_days_end,singleEvents=True,orderBy='startTime').execute() #Remember that single events is on. Make sure it doesn't cause any problems down the line

        weather_data = requests.get(weather_api_address).json()

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

        y1 = start_val*multiplier+300-time_offset-scroll+2
        y2 = end_val*multiplier+300-time_offset-scroll-2

        canvas.create_rectangle(50,y1,root.winfo_screenwidth()/2-50,y2,fill='grey10',outline='red')#'grey35')
        if y1 < 300 and y2 > 350:
            canvas.create_text(root.winfo_screenwidth()/4,315,anchor=CENTER,text=i['summary'],font=('TkTextFont',20),fill='grey50')
            canvas.create_text(root.winfo_screenwidth()/4,340,anchor=CENTER,text=get_hours_and_minutes(start)+'-'+get_hours_and_minutes(end),font=('TkTextFont',10),fill='grey45')
        else:
            canvas.create_text(root.winfo_screenwidth()/4,y1+15,anchor=CENTER,text=i['summary'],font=('TkTextFont',20),fill='grey50')
            canvas.create_text(root.winfo_screenwidth()/4,y1+40,anchor=CENTER,text=get_hours_and_minutes(start)+'-'+get_hours_and_minutes(end),font=('TkTextFont',10),fill='grey45')
    if len(events['items']) == 0:
        canvas.create_text(root.winfo_screenwidth()/4,root.winfo_screenheight()/3,anchor=CENTER,text='No Events Today',font=('TkTextFont',30),fill='grey15')

    y = 300
    for i in tommorow_events['items']:
        start = get_time_from_datetime(i['start']['dateTime'])
        end = get_time_from_datetime(i['end']['dateTime'])

        start_val = get_int_from_time(start)
        end_val = get_int_from_time(end)

        canvas.create_rectangle(root.winfo_screenwidth()/2+50,y+2,root.winfo_screenwidth()/4*3-50,y+98,fill='grey10',outline='red')
        canvas.create_text(root.winfo_screenwidth()/2+root.winfo_screenwidth()/8,y+15,anchor=CENTER,text=i['summary'],font=('TkTextFont',20),fill='grey50')
        canvas.create_text(root.winfo_screenwidth()/2+root.winfo_screenwidth()/8,y+40,anchor=CENTER,text=get_hours_and_minutes(start)+'-'+get_hours_and_minutes(end),font=('TkTextFont',10),fill='grey45')

        y += 100

    if len(tommorow_events['items']) == 0:
        canvas.create_text(root.winfo_screenwidth()/2+root.winfo_screenwidth()/8,root.winfo_screenheight()/3,anchor=CENTER,text='No Events Tommorow',font=('TkTextFont',30),fill='grey15')

    y = 300
    for i in two_days_events['items']:
        start = get_time_from_datetime(i['start']['dateTime'])
        end = get_time_from_datetime(i['end']['dateTime'])

        start_val = get_int_from_time(start)
        end_val = get_int_from_time(end)

        canvas.create_rectangle(root.winfo_screenwidth()/4*3+50,y+2,root.winfo_screenwidth()-50,y+98,fill='grey10',outline='red')
        canvas.create_text(root.winfo_screenwidth()/2+root.winfo_screenwidth()/8*3,y+15,anchor=CENTER,text=i['summary'],font=('TkTextFont',20),fill='grey50')
        canvas.create_text(root.winfo_screenwidth()/2+root.winfo_screenwidth()/8*3,y+40,anchor=CENTER,text=get_hours_and_minutes(start)+'-'+get_hours_and_minutes(end),font=('TkTextFont',10),fill='grey45')

        y += 100

    if len(two_days_events['items']) == 0:
        canvas.create_text(root.winfo_screenwidth()/2+root.winfo_screenwidth()/8*3,root.winfo_screenheight()/3,anchor=CENTER,text='No Events Two Days From Now',font=('TkTextFont',30),fill='grey15',width=350,justify=CENTER)

    canvas.create_rectangle(0,0,root.winfo_screenwidth(),301,fill='black')

    canvas.create_line(0,300,root.winfo_screenwidth(),300,fill='red')
    canvas.create_line(root.winfo_screenwidth()/2,300,root.winfo_screenwidth()/2,root.winfo_screenheight(),fill='red')
    canvas.create_line(root.winfo_screenwidth()/4*3,300,root.winfo_screenwidth()/4*3,root.winfo_screenheight(),fill='red')

    canvas.create_text(root.winfo_screenwidth()/3,100,anchor=CENTER,text=get_hours_and_minutes(get_time_from_datetime(datetime.now().isoformat())),font=('TkTextFont',50),fill='grey55')
    canvas.create_text(root.winfo_screenwidth()/3,175,anchor=CENTER,text=datetime.today().strftime('%m-%d-%Y'),font=('TkTextFont',35),fill='grey45')

    canvas.create_text(root.winfo_screenwidth()/3*2-100,130,anchor=CENTER,text=str(int(weather_data['main']['temp']))+'°',font=('TKTextFont',50),fill='grey50')
    #canvas.create_image(root.winfo_screenwidth()/3*2+10,130,anchor=CENTER,image=cloud)


    root.update()
