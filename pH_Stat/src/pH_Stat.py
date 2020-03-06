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

# The modules folder contain a file called chemyx which contains some important comands
from Modules import chemyx

# This defines the ReadOdion function, it tries to collect data from the pH meter and returns the pH, temp, and the pH_dataframe
def ReadOrion():
    try:
        # Send the *IDN?\r comand to the pH meter
        orion.write(str.encode('*IDN?\r'))
        # Remove the input string from the buffer (this prevents it being transmitted to the output)
        orion.flushInput()
        # Wait 0.1s
        time.sleep(0.1)
        # Read 170 bytes of data from the pH meter
        pH_data = str(orion.read(170))
        # Clear the output (to prevent this being carried into the next loop
        orion.flushOutput()
        # This section looks in the pH_data string to extract the pH and temp reading based on their position relative to other characters
        trim_pH = re.search('M100,(.+?),pH', pH_data)
        trim_temp = re.search('mV,(.+?),C', pH_data)
        temp = float(trim_temp.group(1))
        pH = float(trim_pH.group(1))
        # Print the pH _data string to the console
        print(pH_data)
        # return pH, temp, and pH_data to the program
        return [pH, temp, pH_data]  
           
    except Exception:
        # If the above loop fails the skip the loop and try again
        pass
    
# This defines the Collect function, it tries to collect data from the syringe pump then calls the ReadOrion function and prints the ph and volume data to csv
def Collect(df, filename):
    try:    
        # Collect volume displaced from the syringe pump
        vol = chemyx.getDisplacedVolume()
        # Take the volume pumped from the raw data
        vol = str(vol[1])
        vol = vol.partition("=")[2]
        vol = vol[0:-5]
        
        # Call the ReadOrion function, pH is the first element, temp the second and raw_data the third
        orion_dat = ReadOrion()
        pH = orion_dat[0]
        temp = orion_dat[1]
        raw_dat = orion_dat[2]
        
        # Add data gathered into the existing dataframe
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
        
        # Write the dataframe to the csv file
        data.to_csv(filename, mode='a', header=False, index=False)
        # print data to the console
        print(data[["Time_s", "pH", "Setpoint_pH", "Volume_mL", "Rate_mL_h"]])
        # Return the elapsed time, pH, setpoint pH, volume, and pump rate
        return [elapsed_time, pH, setpoint_pH, vol, rate]
        
    except Exception as e:
        # This tells you there was an error in the Collect function and the type of error will be printed
        print("Collect error of type: ", e)
        pass

# This function sets upper and lower limits for the pump (this stops the pump from running too fast and running empty)
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
# Ask for the following inputs (remove any not nesscary but also remove from the expt_data
key = input("Experimental Key: ")
NaHCO3 = input("NaHCO3 mass (g): ")
Na2CO3 = input("Na2CO3 Titrant mass (g): ")
CaCl2 = input("CaCl2 Titrant mass (g): ")
CaCO3 = input("CaCO3 Seed mass (g): ")
sol_mass = input("Solution mass (g): ")
desig = input("Experimental Designation: ")
filename = "Stat_" + key +".csv"

# This prints data gathered from the inputs into the output data
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

# Establish connection with the syring pump
chemyx =  chemyx.Connection(port = "COM5", baudrate = 9600)
chemyx.openConnection()

# Establish connection with orion pH meter
orion = serial.Serial('COM4', baudrate = 9600) 

###############################################################################
### Program loop
###############################################################################
starttime=time.time()
# Start pumping
chemyx.startPump()
# Variable pumpon is True (this is used to control the looping)
pumpon = True
rate = 0.25
# Set the pump rate to 0.25
chemyx.setRate(0.25)

# The pH stat will aim to keep the pH at the first reading collected
setpoint_pH = ReadOrion()[0]
pH = ReadOrion()[0] 

# This is the loop that collects data every 30 seconds
try:
    while True: 
        elapsed_time = time.time() - starttime
        
        # Get the pH and find the difference between the pH and the target pH (the absolute value is taken so its always positive)
        data = Collect(expt_data, filename)
        pH = data[1]
        vol = data[3]
        diff = setpoint_pH - pH
        adiff = abs(diff)
        
        # If the absolute difference is greater than 0.02 the rate is adjusted
        if adiff > 0.02:
            if rate > 0.2:
                rate = set_lims(rate + (diff * 4))
                chemyx.setRate(rate)
                                 
           # If the rate drops below 0.2 there are issues with the pump volume read so the pump is paused      
            elif rate <= 0.2:
                if pumpon == True:
                    chemyx.pausePump()
                    pumpon = False
                    time.sleep(0.5)
                    
             # If the pump is paused then this code is ran which will restart the pump if the absolute difference is greater than 0.2   
                elif pumpon == False:
                    if adiff > 0.2:
                        chemyx.startPump()
                        rate = 0.25
                        chemyx.setRate(rate)
                        pumpon = True
                        time.sleep(0.5)
                        
            # Wait for 30 seconds to limit the amount of data that is collected
        time.sleep(30.0 - (elapsed_time % 30.0))
        
except Exception as e:
    print("Error of type: ", e)
    chemyx.stopPump()
    chemyx.closeConnection()
    orion.close()
    print("Closed")
    
