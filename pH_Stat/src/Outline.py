# -*- coding: utf-8 -*-
"""
Created on Sat Sep 14 10:17:11 2019

@author: eart0461
"""

###############################################################################
### Load modules
###############################################################################
import pandas as pd
import time
import serial
import re

from Modules import chemyx

def ReadOrion():
    try:
        orion.flushInput()
        orion.flushOutput()
        orion.write(str.encode('*IDN?\r'))
        time.sleep(0.1)
        pH_data = str(orion.read(170))
        trim_pH = re.search('M100,(.+?),pH', pH_data)
        trim_temp = re.search('mV,(.+?),C', pH_data)
        temp = float(trim_temp.group(1))
        pH = float(trim_pH.group(1))
        print(pH_data)
        return [pH, temp]  
           
    except Exception:
        pass
    

def Collect(df, filename):
    try:    
        vol = chemyx.getDisplacedVolume()
        vol = str(vol[1])
        vol = vol.partition("=")[2]
        vol = vol[0:-5]
                
        orion_dat = ReadOrion()
        pH = orion_dat[0]
        temp = orion_dat[1]
        
        data = pd.DataFrame({"Key": key,
                          "Time": time.ctime(),
                          "Elapsed": elapsed_time,
                          "pH": pH,
                          "Temp": temp,
                          "setpoint_pH": setpoint_pH,
                          "Volume_mL": vol,
                          "Rate_mL_h": rate,
                          "NaHCO3": NaHCO3, 
                          "Na2CO3": Na2CO3, 
                          "CaCl2": CaCl2, 
                          "CaCO3": CaCO3, 
                          "sol_mass": sol_mass, 
                          "desig": desig}, index = [0])
        df = df.append(data) 
        
        data.to_csv(filename, mode='a', header=False, index=False)
        print(data[["Elapsed", "pH", "setpoint_pH", "Volume_mL", "Rate_mL_h"]])
        return [elapsed_time, pH, setpoint_pH, vol, rate]
        
    except Exception as e:
        print("Collect error of type: ", e)
        pass


def set_lims(num):
    num = float(num)
    min = 0
    max = 7
    if num > max:
        num = max
    elif num < min:
        num = min
    return(num)  
    
###############################################################################
### Initialise program
###############################################################################
key = input("Experimental Key: ")
NaHCO3 = input("NaHCO3 mass (g): ")
Na2CO3 = input("Na2CO3 Titrant mass (g): ")
CaCl2 = input("CaCl2 Titrant mass (g): ")
CaCO3 = input("CaCO3 Seed mass (g): ")
sol_mass = input("Solution mass (g): ")
desig = input("Experimental Designation: ")
filename = key +".csv"

expt_data = pd.DataFrame({"Key": key,
                          "Time": time.ctime(),
                          "Elapsed": [],
                          "pH": [],
                          "Temp": [],
                          "setpoint_pH": [],
                          "Volume_mL": [],
                          "Rate_mL_h": [],
                          "NaHCO3": NaHCO3, 
                          "Na2CO3": Na2CO3, 
                          "CaCl2": CaCl2, 
                          "CaCO3": CaCO3, 
                          "sol_mass": sol_mass, 
                          "desig": desig})

expt_data.to_csv(filename, mode='a', header=True, index=False)

chemyx =  chemyx.Connection(port = "COM5", baudrate = 9600)
chemyx.openConnection()

orion = serial.Serial('COM4', baudrate = 9600) 

###############################################################################
### Program loop
###############################################################################
starttime=time.time()
chemyx.startPump()
pumpon = True
rate = 0.25
chemyx.setRate(0.25)

setpoint_pH = 8.211 # ReadOrion()[0]
pH = setpoint_pH

try:
    while True: 
        elapsed_time = time.time() - starttime
               
        data = Collect(expt_data, filename)
        pH = data[1]
        vol = data[3]
        diff = setpoint_pH - pH
        adiff = abs(diff)
        
        if adiff > 0.02:
            if rate > 0.2:
                rate = set_lims(rate + (diff * 4))
                chemyx.setRate(rate)
                                 
                
            elif rate <= 0.2:
                if pumpon == True:
                    chemyx.pausePump()
                    pumpon = False
                    time.sleep(0.5)
                    
                
                elif pumpon == False:
                    if diff > 0.2:
                        chemyx.startPump()
                        rate = 0.25
                        chemyx.setRate(rate)
                        pumpon = True
                        time.sleep(0.5)
        

        time.sleep(30.0 - (elapsed_time % 30.0))
        
except Exception as e:
    print("Error of type: ", e)
    chemyx.stopPump()
    chemyx.closeConnection()
    orion.close()
    print("Closed")
    
