#Import streamlit pandas and geo pandas

import streamlit as st
import pandas as pd
import geopandas as gpd

#Import folium and related plugins
import folium
from folium import Marker
from folium.plugins import MarketCluster

#Geopy's Nomination
from geopy.geocoders import Nominatim

#Scipy's Spatial
from scipy import spatial

import requests
from io import StringIO
from io import BytesIO

import json


@st.cache #This decorator is used to imporove the performance of streamlit when dealing with large datasets.

###This function read a csv file which contains a list of concentrations by latitude and longitude

def load_data():
    """This function loads a csv file and returns a pandas dataframe"""
    original_url = "https://drive.google.com/file/d/1keCA9T8f_wIxjtdgjzQY9kzYX9bppCqs/view?usp=sharing"
    file_id = original_url.split("/")[-2]
    dwn_url = 'https://drive.google.com/uc?export=download&id=' + file_id
    url = requests.get(dwn_url).text
    path = StringIO(url)
    df = pd.read_csv(path)
    return df

###This function loads a geoJSON file with oakland city boundary

def load_oakl_data():
    """This function returns a url to geoJSON file."""
    original_url_oakl = "https://drive.google.com/file/d/1I008pOw0Qz0ARNVC8eBqhEt325DDU_yq/view?usp=sharing"
    file_id_oakl = original_url_oakl.split("/")[-2]
    dwn_url_oakl = 'https://drive.google.com/uc?export=download&id=' + file_id_oakl   
    url_oakl = requests.get(dwn_url_oakl).content
    return url_oakl


def convert_address(address):
    """This function converts an address or a point of interest to latitide and longitude coordinates."""
    geolocator = Nominatim(user_agent="my_app") #using open street map API
    Geo_Coordinate = geolocator.geocode(address)
    lat = Geo_Coordinate.latitude
    lon = Geo_Coordinate.longitude
    #Convert the lat long into a list and store is as points
    point = [lat, lon]
    return point

def display_map(point, df, oakl_geojson):
    m = folium.Map(point, tiles = 'OpenStreetMap', zoom_start=11)
    
    # Add polygon boundary to folium map
    folium.GeoJson(oakl_geojson, style_function = lambda x: {'color':'blue', 'weight':2.5, 'fillOpacity':0}, name="Oakland").add_to(m)
    
    #Add marker for Location
    folium.Marker(location=point, 
                  popup = """
                                <i>BC Concentration: </i> <br> <b>{}</b> ug/m3 <br><hr>
                                <i>NO<sub>2</sub> Concentration:</i><b><br>{}</b> ppb <br>""".format(
                                    round(df.loc[spatial.KDTree(df[['Latitude', 'Longitude']]).query(point)[1]]['BC_Predicted_XGB'],2),
                                    round(df.loc[spatial.KDTree(df[['Latitude', 'Longitude']]).query(point)[1]]['NO2_Predicted_XGB'],2)),
                                icon= folium.Icon()).add_to(m)
    
    return st.markdown(m._repr_html_(), unsafe_allow_html = True)


def main():
    #Load csv data
    df_data = load_data()
    
    #Load geoJSON file using json.loads
    oakl_json = load_oakl_data()
    oakl_json = oakl_json.decode("utf-8")
    oakl_geojson = json.loads(oakl_json)
    
    
    #For the page display, create header and subheader, and get an input address from the user 
    st.header("Predicting Air Quality  in East Bay Area")
    st.text("")
    st.subheader("This website reports annual average concentrations of Black Carbon and Nitrogen Dioxide in Oakland and San Leandri.")
    st.text("")
    address = st.text_input("Enter an address or point of interest below.", "900 Fallon St, Oakland, CA 94607")
    
    #Use the convert_address function to convert address to coordiantes
    coordinates = convert_address(address)
     
     
     #Call the display_map function by passing coordinates, datafram eand geoJSON file
    st.text("")
    display_map(coordinates, df_data, oakl_geojson)
     
    st.text("")
    st.text("Created by - QQ")
     
    if __name__ == "__main__":
        main()
         