########################################################################
# AirTravelCarbon.py
#
# This code seeks to assess the carbon footprint of flying commercially
#
# Notes:
# - uses geopy to calculate great circle distances. This is necessary
#   to calculate fuel consumption of assumed aircraft. 
#   https://pypi.org/project/geopy
# - uses pycountry-convert to get continents from countries. This is 
#   important to get the correct ICAO load factors.
#   https://pypi.org/project/pycountry-convert/
# - implements ICAO carbon calculator (although simplified)
#   https://www.icao.int/environmental-protection/CarbonOffset/Documents/
#   Methodology%20ICAO%20Carbon%20Calculator_v10-2017.pdf/
# - requires files plf.csv and ptff.csv, which contain the ICAO load
#   factors but consolidated for the 5 continents: Europe, North America
#   South America, Afria, Asia and Oceania. The load factors are found in
#   Appendix A of the ICAO pdf.
#   Aircraft assumptions:
#       - Short Haul:  CRJ 700          < 550  km
#       - Medium Haul: Airbus A320      < 5500 km
#       - Long Haul:   Boeing 777-300ER > 5500 km
#
#   Sanjoy Som  -January 2019
########################################################################
import os
import sys
import pycountry
import numpy as np
import pandas as pd
########################################################################
# Functions called by main program
########################################################################
def get_continent(country):
    from pycountry_convert import \
	country_name_to_country_alpha2 as cn2a2
    from pycountry_convert import \
	country_alpha2_to_continent_code as a2ctc
    from pycountry_convert import \
        convert_continent_code_to_continent_name as ctc2ctn
    #find country name in pycountry database
    for i in range(len(pycountry.countries)):
       newcountry = list(pycountry.countries)[i].name
       if country in newcountry:
          country = newcountry
    #find corresponding country alpha2 code & continent
    country_alpha2 = cn2a2(country)
    continent      = a2ctc(country_alpha2)
    continent      = ctc2ctn(continent)
    return continent 

def get_coordinates(city):
    from geopy.geocoders import Nominatim
    geolocator  = Nominatim(user_agent="AirTravelCarbon")
    location    = geolocator.geocode(city, language='en')
    if location == None:
        print 'Error: city ' + city + ' was not found.'
        sys.exit()
    coordinates = [location.latitude, location.longitude]
    country     = location.address.split()[-1]
    continent   = get_continent(country)
    return coordinates, country, continent

def get_greatcircle(city1, city2, verbose = False):
    from geopy.distance import great_circle
    distance = great_circle(city1,city2).km
    if verbose:
        print 'Distance of travel: ' + '%.0f'%distance + ' km'
    return distance

def get_aircraftdata(distance,ft,verbose=False):
    if ft == 'Short Haul':
       #Assumptions for Medium Haul:
       if verbose:
          print 'Aircraft: CRJ 700'
       #aircraft data: https://www.united.com/web/en-US/content/travel/
       #               inflight/aircraft/crj/700/default.aspx
       #Seats: 6 (First), 64 (economy). 6 First = 12 economy equival.
       #Therefore CRJ 700 has 76 economy equivalent seats (nys)
       nys = 76.
       #Fuel consumption source: 
       #https://en.wikipedia.org/wiki/Fuel_economy_in_aircraft
       #mileage = 4.4 L/100km per seat of jet fuel (0.804 kg/l),
       #calculated for 70 seats.
       tf = 4.4 * 0.804 / 100. #kg of fuel per km per passenger
       tf = tf * 70.           #kg of fuel per km
       tf = tf * distance       #kg of fuel
       tf = tf / 1000.          #tons of fuel
    if ft == 'Medium Haul':
       #Assumptions for Medium Haul:
       if verbose:
          print 'Aircraft: Airbus A320'
       #aircraft data: https://www.united.com/web/en-US/content/travel/
       #               inflight/aircraft/airbus320/default.aspx
       #Seats: 12 (First), 138 (economy). 12 First = 18 economy equival.
       #Therefore A320 has 156 economy equivalent seats (nys)
       nys = 156.
       #Fuel consumption source: 
       #https://en.wikipedia.org/wiki/Fuel_economy_in_aircraft
       #mileage = 2.61 L/100km per seat of jet fuel (0.804 kg/l),
       #calculated for 150 seats.
       tf = 2.61 * 0.804 / 100. #kg of fuel per km per passenger
       tf = tf * 150.           #kg of fuel per km
       tf = tf * distance       #kg of fuel
       tf = tf / 1000.          #tons of fuel
    elif ft == 'Long Haul':
       #Assumptions for Long Haul:
       if verbose:
          print 'Aircraft: Boeing 777-300ER'
       #aircraft data: https://www.united.com/web/en-US/content/travel/
       #               inflight/aircraft/777/300/default.aspx
       #Seats: 60 (Business), 24 (premium). 266 (economy)
       #28 Business = 140 economy equival.
       #24 Premium  = ~35 economy equival.
       #Therefore 777 has 300 + 35 + 266 = 601 economy equivalent seats (nys)
       nys = 601.
       #Fuel consumption source: 
       #https://en.wikipedia.org/wiki/Fuel_economy_in_aircraft
       #mileage = 3.11 L/100km per seat of jet fuel (0.804 kg/l),
       #calculated for 344 passengers
       tf = 3.11 * 0.804 / 100. #kg of fuel per km per passenger
       tf = tf * 344.           #kg of fuel per km
       tf = tf * distance       #kg of fuel
       tf = tf / 1000.          #tons of fuel
    if verbose:
       print 'Fuel consumption of aircraft: ' + '%.0f'%tf + ' tons'
    return tf, nys

def get_filepath():
    from os import path
    filepath   = os.path.dirname(os.path.abspath(__file__))+'/'
    return filepath

def get_table(filename):
    filepath   = get_filepath()
    data = pd.read_csv(filepath+filename,delimiter=',')
    df = pd.DataFrame(data)
    return df

def get_flightvalues(distance,ft,ct1,ct2, verbose = False):
    #tC   = number of tons of CO2 producing by burning 1 ton of fuel
    #tf   = total fuel used by aircraft to reach destination
    #ptff = pax-to-freight factor
    #nys  = number of economy equivalent seats
    #plf  = pax load factor
    plf = get_table('plf.csv')
    plf = plf.set_index('continent')
    plf = plf.filter(regex=ct1,axis=0).filter(regex=ct2,axis=1).iloc[0]
    ptff = get_table('ptff.csv')
    ptff = ptff.set_index('continent')
    ptff = ptff.filter(regex=ct1,axis=0).filter(regex=ct2,axis=1).iloc[0]
    tf, nys = get_aircraftdata(distance,ft,verbose)
    tC = 3.16 
    return tC, tf, ptff, nys, plf 

def get_icaocarbon(distance, ct1, ct2, verbose=False): #from p.8 of ICAO pdf
    if distance <= 550.:
       distance =  distance + 50.
       ft = 'Short Haul'
    elif (distance > 550.) and (distance < 5500.):
       distance = distance + 100.
       ft = 'Medium Haul'
    elif distance >= 5500.:
       distance = distance + 125.
       ft = 'Long Haul'
    if verbose:
       print 'Identified flight type: ' + ft
    tC, tf, ptff, nys, plf = get_flightvalues(distance,ft,ct1,ct2, verbose)
    #Now we have all the information to calculate C emmited, based on
    #ICAO equation p.6 of pdf.
    CO2_pax = tC * (tf * ptff) / (nys * plf) #tons of carbon emitted
    CO2_pax = CO2_pax *1000.                 #kg of C emitted
    return CO2_pax

def get_vars(cities):
    noc = len(cities) #number of cities
    nof = noc - 1     #number of flights

    coords    = np.zeros((noc),dtype = object)
    country   = np.zeros((noc),dtype = object) 
    continent = np.zeros((noc),dtype = object) 
    distance  = np.zeros(nof)
    carbon    =  np.zeros(nof)
    return noc, nof, coords, country, continent, distance, carbon

def get_journeycarbon(cities, verbose=False):
    noc, nof, coords, country, continent, distance, carbon = get_vars(cities)
    for i in range(noc):
        coords[i], country[i], continent[i] = get_coordinates(cities[i])

    for i in range(nof):
        if verbose:
           print cities[i] + ' ('+country[i]+')'+ ' to'
           print cities[i+1] + ' ('+country[i+1]+')'  
        distance[i] = get_greatcircle(coords[i],coords[i+1], verbose)
        carbon[i]  = get_icaocarbon(distance[i],continent[i], continent[i+1], verbose)
        if (nof > 1) and verbose:
            print 'Carbon cost of leg: ' + '%.0f'%carbon[i] +' kg'
            print '-'*40
    return carbon

def get_airtravelcarbon(city_departure, city_layover, city_arrival, verbose=False):
	cities = [city_departure, city_layover, city_arrival]
	direct = [city_departure, city_arrival]

	if (not city_layover) or (city_layover == 'none') or \
           (city_layover == 'direct') or (city_layover == 'None'):
   		cities = direct

	carbon = get_journeycarbon(cities, verbose)
	if verbose:
	    print 'Total Carbon cost of journey: ' + '%.0f'%np.sum(carbon) +' kg'
	return carbon
########################################################################
# Main program
########################################################################
if __name__ == "__main__":
        verbose = True
	city_departure = raw_input('City of Departure: ')
	city_layover   = raw_input('City of Layover: ')
	city_arrival   = raw_input('City of Arrival: ')
        print '-'*40
	carbon = get_airtravelcarbon(city_departure, city_layover, city_arrival, verbose)
