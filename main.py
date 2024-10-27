import datetime as dt
import os
import os.path 

#*for discord chat scrapping
import requests
import json
from datetime import datetime
from dateutil import parser
import pytz

#*for gui
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk

#*for securing authentication id
from dotenv import load_dotenv

#*for google aclendar automation
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/calendar"]

def submit():
    global channel_id, selected_timezone
    channel_id = channel_id_entry.get()
    selected_timezone = timezone_var.get()
    print(f"Channel ID: {channel_id}")
    print(f"Time Zone: {selected_timezone}")

    if channel_id and selected_timezone:
        messagebox.showinfo("Run","Click ok to Automate")
    else:
        messagebox.showwarning("Waring","Please fill up above boxes")

    def configure():
        load_dotenv()

    #*discord chat scrapping
    def msg(channedid):
            configure()
            headers = {
                'authorization' : os.getenv('authfile')
            }
            r = requests.get(
                f'https://discord.com/api/v9/channels/{channedid}/messages?',headers=headers
            )
            jsson = json.loads(r.text)

            string = ""
            for value in jsson:
                string+= value['content']
                break
            return string

    userid = channel_id
    usertimezone = selected_timezone

    idd = userid
    string = msg(idd)
    print(string)

    parsed_date = str(parser.parse(string,fuzzy=True))

    user_tz = pytz.timezone(usertimezone)
    now_in_user = datetime.now(user_tz)
    utc_offset = now_in_user.strftime('%z')
    formatted_offset = f"{utc_offset[:3]}:{utc_offset[3:]}"

    endtime_string = parsed_date.replace(" ","T")+formatted_offset
    starttime_string = datetime.now().isoformat().split('.')[0]+formatted_offset
    print("endtime_string",endtime_string)
    print("starttime_string",starttime_string)

    #*calendar automation
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("directory\\token.json")
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("directory\\credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json","w") as token:
            token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)

        event = {  
            "location": usertimezone,
            "description": "automate your life",
            "summary": "Assignment",
            "start": {
                "dateTime": starttime_string,
                "timeZone": usertimezone
            },
            "end": {
                "dateTime": endtime_string,
                "timeZone": usertimezone
            },
            "attendees": [
                {"email": "email@gmail.com"}
            ]
        }
        event = service.events().insert(calendarId="primary",body=event).execute()
        print(f"Event created {event.get('htmlLink')}")


    except HttpError as error:
        print(f"An error occurred: {error}")

root = tk.Tk()
root.title("Auto Scheduling from Discord To Google Calendar")
root.geometry("600x450")
root.configure(bg="#edefe8")

title_label = tk.Label(root, text="Auto Scheduling", font=("Helvetica", 22))
title_label.pack(pady=25)

# Load and resize images with the correct resampling method
discord_image = Image.open("discord.png").resize((60, 50), Image.Resampling.LANCZOS)
discord_photo = ImageTk.PhotoImage(discord_image)

calendar_image = Image.open("calendar.png").resize((50, 50), Image.Resampling.LANCZOS)
calendar_photo = ImageTk.PhotoImage(calendar_image)

# Header Frame to hold the logos
header_frame = tk.Frame(root, bg="#edefe8")
header_frame.pack(pady=10)

discord_label = tk.Label(header_frame, image=discord_photo, bg="#edefe8")
discord_label.pack(side="left", padx=10)

arrow_label = tk.Label(header_frame, text="→", font=("Helvetica", 18), fg="#5b5e53", bg="#edefe8")
arrow_label.pack(side="left", padx=10)

calendar_label = tk.Label(header_frame, image=calendar_photo, bg="#edefe8")
calendar_label.pack(side="left", padx=10)

# Channel ID input
channel_id_label = tk.Label(
    root, text="Channel ID:", font=("Helvetica", 12, "bold"), bg="#edefe8", fg="#5b5e53"
)
channel_id_label.pack(side="top",pady=5)
channel_id_entry = tk.Entry(
    root, width=30, font=("Helvetica", 12), bg="#3c3c3c", fg="#edefe8", relief="flat"
)
channel_id_entry.pack(pady=5)

# Time Zone dropdown menu
timezone_var = tk.StringVar()
timezone_label = tk.Label(
    root, text="Select Time Zone:", font=("Helvetica", 12, "bold"), bg="#edefe8", fg="#5b5e53"
)
timezone_label.pack(pady=5)

timezones = [
    "Asia/Dhaka", "Asia/Kolkata", "Europe/London", 
    "America/New_York", "Australia/Sydney", "Africa/Nairobi"
]

timezone_menu = ttk.Combobox(
    root, textvariable=timezone_var, values=timezones, state="readonly", width=28
)
timezone_menu.pack(pady=5)

# Submit button with hover effect
def on_enter(e):
    submit_button.config(bg="#16a085")

def on_leave(e):
    submit_button.config(bg="#1abc9c")

submit_button = tk.Button(
    root, text="Submit", font=("Helvetica", 12, "bold"), bg="#1abc9c", fg="#ffffff", relief="flat", 
    command=submit
)
submit_button.pack(pady=20)
submit_button.bind("<Enter>", on_enter)
submit_button.bind("<Leave>", on_leave)


root.mainloop()