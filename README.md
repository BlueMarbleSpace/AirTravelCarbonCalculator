# AirTravelCarbonCalculator
Blue Marble Space is committed to a sustainable future. See our [Code of Ethics](https://www.bluemarblespace.org/ethics.html).

This code calculates carbon emissions of flying commercially.

# Notes on construction:
- Dependency TL;DR: pandas, numpy, pycountry, geopy, pycountry-convert.
- Uses geopy to calculate great circle distances. This is necessary to calculate fuel consumption of assumed aircraft.
  https://pypi.org/project/geopy
- Uses pycountry-convert to get continents from countries. This is important to get the correct ICAO load factors.
  https://pypi.org/project/pycountry-convert/
- Implements ICAO carbon calculator (although simplified):
  https://www.icao.int/environmental-protection/CarbonOffset/Documents/Methodology%20ICAO%20Carbon%20Calculator_v10-2017.pdf
- Requires files plf.csv and ptff.csv (included), which contain the ICAO load factors but consolidated for the 5 continents: Europe, 
  North  America, South America, Afria, Asia and Oceania. The load factors are found in Appendix A of the ICAO pdf.
- Fuel economy of aircrafts from: https://en.wikipedia.org/wiki/Fuel_economy_in_aircraft
- Assumes traveler is flying economy class.
- Implements a single layover (layover can left blank for direct flights).
  
 # Aircraft assumptions:
 - Short Haul:  United Airlines CRJ 700          < 550  km
   https://www.united.com/web/en-US/content/travel/inflight/aircraft/crj/700/default.aspx
 - Medium Haul: United Airlines Airbus A320      >=500 km, < 5500 kmh
   https://www.united.com/web/en-US/content/travel/inflight/aircraft/airbus320/default.aspx
 - Long Haul:   United Airlines Boeing 777-300ER >= 5500 km
   https://www.united.com/web/en-US/content/travel/inflight/aircraft/777/300/default.aspx

  # Notes on implementation:
 - Can be used as standalone code (verbose) or imported into another (non-verbose) with, for example: 
   '''
   import AirTravelCarbonCalculator as ATC
   kg_carbon = ATC.get_airtravelcarbon(city_of_departure, city_of_layover, city_of_destination)
   '''
   
