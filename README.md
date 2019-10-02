# Lab_Control
Software tools written in Python to read and write data to serial port devices enabling custom laboratory control set-ups.

## Getting Started

This repository contains two python programs for lab control.

Autotitrator.py is an autotitrator program that is designed for carrying out alkalinity titrations on seawater samples. The associated R data analysis file Titr.Calc.rmd uses the gran method (https://water.usgs.gov/owq/FieldManual/Chapter6/section6.6/html/section6.6.4.htm) to determine alkalinity for each sample.

pH_Stat.py is a chemostat program that adjusts the rate of a syringe pump to maintain a constant pH within a reactor vessel. The associated R data analysis file Rate_Cale.rmd is designed to use the volume of titrants added to calculate the rate of precipitation within the vessel. This requires a surface area (initially set to 0.205 m2/g).

### Prerequisites

The python programs require the following modules:

```
pip install pandas
pip install pyserial
```
The R data analysis files require the following packages:
```
install.packages("tidyverse")
install.packages("here")
install.packages("cowplot")
install.packages('Cairo')
```
## Built With

* [Anaconda3](https://www.anaconda.com/distribution/#download-section) - Anaconda for Windows Python version 3.7
* [RStudio](https://rstudio.com/products/rstudio/download/#download) - RStudio for Windows R version 3.6.1
* Chemyx Fusion 100 syringe pump
* Thermo Orion Dual star pH meter

## Authors

* **David Hodkin**

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Chemyx example code was used as a basis for the syringe pump communication (https://www.chemyx.com/support/knowledge-base/programming-and-computer-control/)
