import math
from pathlib import Path
import shutil
from tkinter import filedialog
import pyttsx3
from msilib import Table
import requests
import os
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import webbrowser
import tkinter as tk  
from tkinter import *
from easygui import *
import wget
import urllib3

def download_file(url, filename):
    http = urllib3.PoolManager()
    with http.request('GET', url, preload_content=False) as resp, open(filename, 'wb') as out_file:
        data = resp.read()
        out_file.write(data)
    print(f"Downloaded {url} and saved as {filename}")

def download_file_wget(url, filename):
    wget.download(url,filename)
    print(f"Downloaded {url} and saved as {filename}")

def get_fixes(xml_data):
    tree = ET.fromstring(xml_data)
    #rootNode = tree.getroot()
    navlog_node = tree.find('navlog')
    fix_nodes = navlog_node.findall('fix')
    return fix_nodes

def get_value(xml_string,param):
    root = ET.fromstring(xml_string)
    val = root.find(param).text
    return val


def speak(text):
    
    engine = pyttsx3.init()

    
    rate = engine.getProperty('rate')
    engine.setProperty('rate', rate - 50)
    volume = engine.getProperty('volume')
    engine.setProperty('volume', volume + 0.25)
    voices = engine.getProperty('voices')

    engine.setProperty('voice', 'HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-US_ZIRA_11.0')

    # say the input text
    engine.say(text)
    engine.runAndWait()

def downloadbriefing():
    
    coroute = flight_id_entry.get()
    print("Saving flight plan ",coroute)
    shutil.copyfile(documentsPath+"\\rSimBriefDownloader\\recent.xml",save_directory+"\\"+coroute+".xml")
    
    url=f"https://www.simbrief.com/ofp/flightplans/{coroute}_XPE_{timegenerated}.fms"
    output_fms=save_directory+"\\"+coroute+".fms"
    url2=f"https://www.simbrief.com/ofp/flightplans/xml/{coroute}_XML_{timegenerated}.xml--ZBO"
    output_fms2=save_directory+"\\b738x.xml"
    download_file(url,output_fms)
    download_file(url2,output_fms2)
#https://www.simbrief.com/ofp/flightplans/xml/KTPAKMIA_XML_1702909449.xml--ZBO
#https://www.simbrief.com/ofp/flightplans/xml/KTPAKMIA_XML_1702909449.xml--ZBO
#def set_simbrief_username():
    #global simbrief_username
    #simbrief_username = simbrief_username_entry.get()
    
import win32gui, win32con
the_program_to_hide = win32gui.GetForegroundWindow()
win32gui.ShowWindow(the_program_to_hide , win32con.SW_HIDE)

def donothing():
    pass

def _quit():  
   root.quit()  
   root.destroy()  
   exit()  

def output_select():
   global save_directory
   filepath = filedialog.askdirectory(initialdir=save_directory)
   if(filepath == ""):
       return
       
    
   save_directory=filepath
   global savedirmenu
   #savedirmenu.add_command(label="Test",command=donothing)
   savedirmenu.entryconfigure(1,label=save_directory)
   print("Set path to "+save_directory)
   speak("set path to "+save_directory)
   
def username_select():
    global username
    new_name = enterbox("Enter simbrief username", "Simbrief Username", username)
    global usernamemenu
    usernamemenu.entryconfigure(1,label=new_name)
    username=new_name
    print("Set Username to "+username)
    speak("Set username to "+username)

def read_config():
    global username
    global save_directory

    configFile=f"{documentsPath}\\rSimBriefDownloader\\config.ini"
    configPath=Path(configFile)
    if(configPath.is_file()):
        with open(configFile) as f:
            lines = f.readlines()
        user_name = lines[0].strip()
        savepath = lines[1].strip()
        if(len(user_name) >0):
            username=user_name
        if(len(savepath) >0):
            save_directory=savepath

    return username,save_directory
    
def openxml(arguments):
    global documentsPath
    filename=documentsPath+"\\rSimBriefDownloader\\recent.xml"
    webbrowser.open_new_tab(filename)



def filltable(cruisealt=0,rampfuel=0,payload=0,zfw=0,reserveFuel=0,takeoffFuel=0,costIndex=0,tocWind=0,tocTemp=0,tocDev=0,origMetar="none",destMetar="none"):
    names = ["Cruise Altitude", "Block Fuel", "Reserve Fuel","Takeoff Fuel","Payload","ZFW","Cost Index","TOC Wind","TOC Temp","TOC ISA Dev"]
    if(zfw==0):
        return
    
    rampfuel=(math.ceil(int(rampfuel)/100) * 100)
    zfw=round(int(zfw)/1000,1)
    #details.configure(background="blue")
    values = [cruisealt, rampfuel, reserveFuel,takeoffFuel,payload,zfw,costIndex,tocWind,tocTemp,tocDev]
    for i in range(len(names)):
        exLabel="";
        if(i == 1 or i == 2 or i == 3):
            exLabel=units;
        tk.Label(details, text=names[i],width="17",font=("Arial", 16, "bold"),anchor="e",padx="15").grid(row=i+1, column=0)
        password_label = tk.Label(details, text=f"{values[i]} {exLabel}",width="25",anchor="w",font=("Arial", 16, "bold"),padx="10")
        password_label.grid(row=i+1, column=1)

    oMetar_label = tk.Label(details, text=f"{origMetar}",anchor="w",font=("Arial", 10, "bold"),padx="10",wrap="250")
    dMetar_label = tk.Label(details, text=f"{destMetar}",anchor="n",font=("Arial", 10, "bold"),padx="10",wrap="250")
    oMetar_label.grid(row=len(names)+1,column=0,sticky="w")
    dMetar_label.grid(row=len(names)+1,column=1,sticky="n")


    #origMetarLabel=tk.Label(details,text=origMetar)
    #origMetarLabel.grid(column=0,columnspan=2)

def refreshbriefing():
    global loadedflight
    global units    
    global timegenerated

    xml_url = f"https://www.simbrief.com/api/xml.fetcher.php?username={username}"
    xml_response = requests.get(xml_url)
    #print(f"The XML file for flight  has been downloaded to {save_directory}")
    timegenerated = get_value(xml_response.content,"./params/time_generated")
    origin = get_value(xml_response.content,"./origin/icao_code")
    destination = get_value(xml_response.content,"./destination/icao_code")
    loadedflight = origin + destination
    loadedflight_label.config(text=loadedflight, fg='green')
    flight_id_entry.delete(0, tk.END)
    flight_id_entry.insert(0, origin+destination)
    print(f"Time generated {timegenerated} from {origin}{destination}")
    xml_path = os.path.join(documentsPath+"\\rSimbriefDownloader", f"recent.xml")
    #xml_path = os.path.join(save_directory, f"{origin}{destination}.xml")
    with open(xml_path, "wb") as xml_file:
        xml_file.write(xml_response.content)
    #speak("Downloaded simbrief xml")

    units=get_value(xml_response.content,"./params/units")

    cruiseAltitude=get_value(xml_response.content,"./general/initial_altitude")
    rampFuel=get_value(xml_response.content,"./fuel/plan_ramp")
    payload=get_value(xml_response.content,"./weights/payload")
    zfw=get_value(xml_response.content,"./weights/est_zfw")
    reserveFuel=get_value(xml_response.content,"./fuel/reserve")
    takeoffFuel=get_value(xml_response.content,"./fuel/plan_takeoff")
    costIndex=get_value(xml_response.content,"./general/costindex")
    origMetar=get_value(xml_response.content,"./weather/orig_metar")
    destMetar=get_value(xml_response.content,"./weather/dest_metar")

    #cruiseLabel2.config(text=cruiseAltitude)
    
    
    fixes=get_fixes(xml_response.content)
    tocwind="000/000"
    toctemp="0"
    tocdev="0"
    #print ("Fixes found ",fixes)
    for node in fixes:
        #print("winddir",node.find("wind_dir").text)
        ident=node.find("ident").text
        wind_dir=node.find("wind_dir").text
        wind_spd=node.find("wind_spd").text
        if(ident == "TOC"):
            tocwind=f"{wind_dir}/{wind_spd}"
            toctemp=node.find("oat").text
            tocdev=node.find("oat_isa_dev").text
            

    
    details.pack(fill=X, expand=0)
    filltable(cruiseAltitude,rampFuel,payload,zfw,reserveFuel,takeoffFuel,costIndex,tocwind,toctemp,tocdev,origMetar,destMetar)
    



documentsPath=os.environ.get("USERPROFILE")+"\\documents"

if not os.path.exists(documentsPath+"\\rSimBriefDownloader"):
    os.makedirs(documentsPath+"\\rSimBriefDownloader")

username = "rgralinski"
save_directory = documentsPath+"\\rSimBriefDownloader"
loadedflight = "None loaded"
units="kgs"
timegenerated=0

read_config()

root = tk.Tk()


mainmenu = Menu(root)

m1 = Menu(mainmenu, tearoff=0)
m1.add_command(label="Quit", command=_quit)
m1.add_separator()



m2 = Menu(mainmenu, tearoff=0)
m2.add_separator()
#m2.add_command(label="Simbrief Username", command=username_select)

usernamemenu=Menu(mainmenu,tearoff=0)
usernamemenu.add_separator()
usernamemenu.add_command(label=username,command=username_select)
usernamemenu.add_separator()

m2.add_cascade(label="Simbrief Username",menu=usernamemenu)



savedirmenu=Menu(mainmenu,tearoff=0)
savedirmenu.add_separator()
savedirmenu.add_command(label=save_directory,command=output_select)
savedirmenu.add_separator()

m2.add_cascade(label="Output Folder",menu=savedirmenu)

mainmenu.add_cascade(label="File", menu=m1)
mainmenu.add_cascade(label="Settings", menu=m2)
root.config(menu=mainmenu)



root.title("Ryans Simbrief Downloader")
root.attributes("-topmost", True)  # This line makes the window stay on top
root.geometry("600x700")

title_label = tk.Label(root, text="Ryans Simbrief Downloader", font=("Arial", 16, "bold"), pady=10)
title_label.pack()

loaded_label = tk.Label(root, text="Loaded Flight:", font=("Arial", 12))
loaded_label.pack()

loadedflight_label = tk.Label(root, text=loadedflight, font=("Arial", 12), fg='red')
loadedflight_label.pack()
loadedflight_label.bind("<Button>",openxml)

refresh_button = tk.Button(root, text="Refresh", font=("Arial", 12), width=20, command=refreshbriefing)
refresh_button.pack()

flight_id_label = tk.Label(root, text="COROUTE:", font=("Arial", 12))
flight_id_label.pack()

flight_id_entry = tk.Entry(root, font=("Arial", 12), width=20)
flight_id_entry.pack(pady=10)
flight_id_entry.insert(0, "")

submit_button = tk.Button(root, text="Save to output folder", font=("Arial", 12), command=downloadbriefing)
submit_button.pack()



details=Frame(root)

filltable()

root.mainloop()





