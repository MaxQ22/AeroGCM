# Aero GCM - Flight Route Mapper

Aero GCM is a Python-based application built using the Kivy framework. This program allows users to plot great circle routes on a world map between specified airports using ICAO/IATA codes. It provides customizable options for displaying city names, country boundaries, and airport identifiers, making it a versatile tool for visualizing global flight paths.

## Table of Contents

- [Features](#features)
- [Program Usage](#program-usage)
- [Requirements](#requirements)
- [Running the Repository](#running-the-repository)
- [Building the Repository](#Building-the-Repository)
- [License](#license)


## Features

- **Plot Great Circle Routes**: Visualize the shortest routes between airports.
- **Distance Rings**: Add distance rings around specific airports.
- **Customization Options**: Toggle labels for airports, country boundaries, and major city names.
- **Resizable World Map**: The map automatically zooms to display all plotted routes.

## Program Usage
Aero GCM (Aero Great Circle Mapper) is used to plot the great circle routes between airports on a world map. To plot a great circle on the map, the IATA or ICAO airport codes can be used.To plot a great circle, the airport combiantion is typed into the airport code window. To plot the great circle route between Los Angeles International airport and San Francisco International airport on the map, use the pair command:
```bash
LAX-SFO
``` 
![LAX-SFO](/screenshots/LAX-SFO.png)

The airport pair is inserted in the text box on the top right, and then the button below it must be pressed, to plot the result to the map. On the left side, there are several options, which can be switched on or off, for example to plot country borders to the map or to hide the airport labels.

Using ICAO codes, the following command leads to the same result, with the exception, that ICAO codes instead of IATA codes are displayed on the map:
```bash
KLAX-KSFO
``` 
To plot multiple routes on one map, they can be combined with commas, for example:
```bash
KLAX-KSFO, KLAX-KEWR
``` 
![KLAX-KSFO, KLAX-KEWR](/screenshots/KLAX-KSFO,KLAX-KEWR.png)

Flights with stopovers can also be plottet, by just concatonating them. For example flying from Los Angeles via Atlanta to Newark Liberty Internationl airport:
```bash
KLAX-KATL-KEWR
``` 
![KLAX-KATL-KEWR](/screenshots/KLAX-KATL-KEWR.png)

It is also possible to combine multiple routes starting from the same origin, by combining the destinations with a '/'. For example several routes from Atlanta can be plottet like this:
```bash
KATL-KLAX/KEWR/KSFO/KHOU
``` 
![KATL-KLAX/KEWR/KSFO/KHOU](/screenshots/KATL-KLAX_KEWR_KSFO_KHOU.png)

The same can be done for plotting multiple routes from the same start point, to the same end point, using several stopovers. For example flying from Los Angeles to Newark via Atlanta or Chicago:
```bash
KLAX-KATL/KORD-KEWR
``` 
![KLAX-KATL/KORD-KEWR](/screenshots/KLAX-KATL_KORD-KEWR.png)

As another feature, it is also possible to plot distance rings around airports. This can be done using kilometers or nautical miles as units. The syntax for doing this is for example:
```bash
1000km@FRA
``` 
or 
```bash
1000nm@KEWR
``` 
Distance rings can also be combined with the great circle routes. The following example shows a combination of distance rings in km and nautical miles, with a great circle route, using mixed ICAO and IATA codes:
```bash
1000nm@KEWR, 1000km@FRA, FRA-KEWR
``` 
![FRA-KEWR](/screenshots/FRA-KLAX.png)
  
## Requirements

To run Aero GCM, you will need the following libraries:

- [Kivy](https://kivy.org/#home)
- [Matplotlib](https://matplotlib.org/)
- [Basemap](https://matplotlib.org/basemap/)
- [airportsdata](https://pypi.org/project/airportsdata/)
- [Geopy](https://geopy.readthedocs.io/)

## Running the Repository

1. Clone this repository or download the source code.
3. Go to the main folder of the repository
2. To install the required Python packages via Conda, use the provided environment.yml file:
```bash
conda env create -f environment.yml
``` 
After that, to activate the environment, do:
```bash
conda activate aerogcm
``` 
to run the AeroGCM program, use the command
```bash
python ./src/AeroGCM.py
``` 
## Building the Repository
This repository can be build into an executable, using the PyInstaller tool. If the conda environment is created from the .yml file, pyinstaller will be automatically installed. To build and pack the repository into an executable file, run the following command:
```bash
pyinstaller AeroGCM.spec
``` 
On Windows, Linux and MACOs platforms, this will generate a stand alone executable of this repository in the folder /dist.
## License
The code within this repository is released under the terms of the GPL-3.0 license.


   
