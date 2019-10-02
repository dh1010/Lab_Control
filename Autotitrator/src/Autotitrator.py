# -*- coding: utf-8 -*-
"""
Created on Thu Sep 19 09:30:24 2019

@author: eart0461
"""

import serial
import pandas as pd
import re
import time

from Modules import chemyx

def ReadOrion():
    try:
        orion.write(str.encode('*IDN?\n'))
        time.sleep(0.5)
        pH_data = str(orion.read(200))
        trim_pH = re.search('M100,(.+?),pH', pH_data)
        trim_temp = re.search('mV,(.+?),C', pH_data)
        temp = float(trim_temp.group(1))
        pH = float(trim_pH.group(1))
               
    except Exception:
        pH = 0
    return(pH, temp) 
    

def Collect(df, filename):
    try:
        time.sleep(10.0 - ((time.time() - starttime) % 10.0))
    
        vol = chemyx.getDisplacedVolume()
        vol = str(vol[1])
        vol = vol.partition("=")[2]
        vol = vol[0:-5]
                
        orion_dat = ReadOrion()
        pH = orion_dat[0]
        temp = orion_dat[1]
        
        data = pd.DataFrame({"Key": key, "Sample_mass_g": sol_mass, "Normality": norm, "Time": time.ctime(), "Temp": temp, "pH": pH, "Volume_mL": vol}, index = [0])
        df = df.append(data) 
        data.to_csv(filename, mode='a', header=False, index=False)
        print(data)
    except Exception:
        pass
#------------------------------------------------------------------------------

key = input("Experimental Key: ")
sol_mass = input("Sample mass (g): ")
norm = input("Acid normality: ")

filename = key +".csv"

chemyx =  chemyx.Connection(port = "COM5", baudrate = 9600)
chemyx.openConnection()

orion = serial.Serial('COM4', baudrate = 9600)

starttime=time.time()
df = pd.DataFrame({"Key": [], "Sample_mass_g": [], "Normality": [], "Time": [], "Temp": [], "pH": [], "Volume_mL": []})
df.to_csv(filename, mode='a', header=True, index=False)

chemyx.startPump()
pH = ReadOrion()[0]

loop1 = 1
loop2 = 1

try:
    while True:
        if pH > 4.5:
            if loop1 == 1:
                chemyx.setRate(5)   
                loop1 = loop1 + 1
            Collect(df, filename)
        
        elif pH < 4.5:
            if loop2 == 1:
                chemyx.setRate(1) 
                loop2 = loop2 + 1            
            Collect(df, filename)
        
except Exception:
    print('Stopped')
    chemyx.stopPump()
    chemyx.closeConnection()
    orion.close()
    