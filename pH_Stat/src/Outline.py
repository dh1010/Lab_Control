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
        orion.write(str.encode('*IDN?\r'))
        orion.flushInput()
        time.sleep(0.1)
        pH_data = str(orion.read(170))
        orion.flushOutput()
        trim_pH = re.search('M100,(.+?),pH', pH_data)
        trim_temp = re.search('mV,(.+?),C', pH_data)
        temp = float(trim_temp.group(1))
        pH = float(trim_pH.group(1))
        print(pH_data)
        return [pH, temp, pH_data]  
           
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
        raw_dat = orion_dat[2]
        
        data = pd.DataFrame({"Key": key,
                          "Date": time.ctime(),
                          "Time_s": elapsed_time,
                          "pH": pH,
                          "Temp_C": temp,
                          "Setpoint_pH": setpoint_pH,
                          "Volume_mL": vol,
                          "Rate_mL_h": rate,
                          "Mass_of_NaHCO3_g": NaHCO3, 
                          "Mass_of_Na2CO3_in_titrant_g": Na2CO3, 
                          "Mass_of_CaCl2_in_titrant_g": CaCl2, 
                          "Mass_of_Seed_g": CaCO3, 
                          "sol_mass": sol_mass, 
                          "Designation": desig,
                          "Raw_data":raw_dat}, index = [0])
        df = df.append(data) 
        
        data.to_csv(filename, mode='a', header=False, index=False)
        print(data[["Time_s", "pH", "Setpoint_pH", "Volume_mL", "Rate_mL_h"]])
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
filename = "Stat_" + key +".csv"

expt_data = pd.DataFrame({"Key": key,
                          "Date": time.ctime(),
                          "Time_s": [],
                          "pH": [],
                          "Temp_C": [],
                          "Setpoint_pH": [],
                          "Volume_mL": [],
                          "Rate_mL_h": [],
                          "Mass_of_NaHCO3_g": NaHCO3, 
                          "Mass_of_Na2CO3_in_titrant_g": Na2CO3, 
                          "Mass_of_CaCl2_in_titrant_g": CaCl2, 
                          "Mass_of_Seed_g": CaCO3, 
                          "sol_mass": sol_mass, 
                          "Designation": desig,
                          "Raw_data":[]})

expt_data.to_csv(filename, mode='a', header=True, index=False)

chemyx =  chemyx.Connection(port = "COM5", baudrate = 9600)
chemyx.openConnection()

orion = serial.Serial('COM4', baudrate = 9600) 

###############################################################################
### Program loop
###############################################################################
starttime=time.time()
#chemyx.startPump()
pumpon = False
#rate = 0.25
#chemyx.setRate(0.25)

setpoint_pH = ReadOrion()[0]
pH = 8.125

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
                    if adiff > 0.2:
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
    
