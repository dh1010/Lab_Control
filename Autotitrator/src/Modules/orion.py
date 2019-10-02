# -*- coding: utf-8 -*-
"""
Created on Thu Sep 19 11:32:38 2019

@author: eart0461
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Sep 19 11:29:59 2019

@author: eart0461
Modules for connections with Chemyx syringe pump
"""
import time
import serial

def ReadOrion():
    try:
        dualstar.write(str.encode('*IDN?\n'))
        time.sleep(0.5)
        pH_data = str(dualstar.read(273))
        trim_pH = re.search('M100,(.+?),pH', pH_data)
        pH = float(trim_pH.group(1))
               
    except Exception:
        pH = 0
    return(pH) 
         