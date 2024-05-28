import streamlit as st
import folium
from collections import namedtuple
import numpy as np
import math
import pandas as pd
from streamlit_folium import st_folium
from streamlit_folium import folium_static
def getArrows(locations, color='blue', size=6, n_arrows=3):
    
    '''
    Get a list of placed and rotated arrows or markers to be plotted
    
    Parameters
    locations : list of lists of latitude longitude that represent the begining and end of Line. 
                    this function Return list of arrows or the markers
    '''
    
    Point = namedtuple('Point', field_names=['lat', 'lon'])
    
    # creating point from Point named tuple
    point1 = Point(locations[0][0], locations[0][1])
    point2 = Point(locations[1][0], locations[1][1])
    
    # calculate the rotation required for the marker.  
    #Reducing 90 to account for the orientation of marker
    # Get the degree of rotation
    angle = get_angle(point1, point2) - 90
    
    # get the evenly space list of latitudes and longitudes for the required arrows

    arrow_latitude = np.linspace(point1.lat, point2.lat, n_arrows + 2)[1:n_arrows+1]
    arrow_longitude = np.linspace(point1.lon, point2.lon, n_arrows + 2)[1:n_arrows+1]
    
    final_arrows = []
    
    #creating each "arrow" and appending them to our arrows list
    for points in zip(arrow_latitude, arrow_longitude):
        final_arrows.append(folium.RegularPolygonMarker(location=points, 
                      fill_color=color, number_of_sides=3, 
                      radius=size, rotation=angle))
    return final_arrows

def get_angle(p1, p2):
    
    '''
    This function Returns angle value in degree from the location p1 to location p2
    
    Parameters it accepts : 
    p1 : namedtuple with lat lon
    p2 : namedtuple with lat lon
    
    This function Return the vlaue of degree in the data type float
    
    Pleae also refers to for better understanding : https://gist.github.com/jeromer/2005586
    '''
    
    longitude_diff = np.radians(p2.lon - p1.lon)
    
    latitude1 = np.radians(p1.lat)
    latitude2 = np.radians(p2.lat)
    
    x_vector = np.sin(longitude_diff) * np.cos(latitude2)
    y_vector = (np.cos(latitude1) * np.sin(latitude2) 
        - (np.sin(latitude1) * np.cos(latitude2) 
        * np.cos(longitude_diff)))
    angle = np.degrees(np.arctan2(x_vector, y_vector))
    
    # Checking and adjustring angle value on the scale of 360
    if angle < 0:
        return angle + 360
    return angle

df = pd.read_csv("D:\Rahul Sir\CenterFirst And last distance analysis\Map_Data.csv")
st.title('Center Distance Analysis')
State=list(df['State'].unique())
#District = list(df['District'].unique())
with st.sidebar:
    st.subheader("Configure the Map")
    # widget to choose which continent to display
    ##State = st.selectbox(label = "Choose a State", options = State)
    selected_state = st.selectbox("Select State", df['State'].unique())
    filtered_State = df[df['State'] == selected_state]
    # widget to choose which metric to display
    District = st.selectbox(label = "Choose a District", options = filtered_State['District'].unique().tolist())
    #selected_district=st.selectbox("Select State", df['District'].unique())
    filtered_district=df[df['District'] == District]
    branchid = st.selectbox(label = "Choose a Branch", options = filtered_district['branchid'].unique().tolist())
    filtered_branchid=df[df['branchid'] == branchid]
    centerid = st.selectbox(label = "Choose a center", options = filtered_branchid['centerid'].unique().tolist())
    
    
query = f"State=='{selected_state}' & District=='{District}' & branchid=='{branchid}' & centerid=={centerid} "
location=df.query(query)
Clientlist = df.query(query)[["Client_Lat","Client_Long"]].values.tolist()
FirstCenter=df.query(query)[["FirstCenterMeeting_Lat","FirstCenterMeeting_Long"]].values.tolist()
LastCenter=df.query(query)[["LastCenterMeeting_Lat","LastCenterMeeting_Long"]].values.tolist()
     

    ##Clientlist = df[["Client_Lat","Client_Long"]].values.tolist()
    ##FirstCenter=df[["FirstCenterMeeting_Lat","FirstCenterMeeting_Long"]].values.tolist()
    ##LastCenter=df[["LastCenterMeeting_Lat","LastCenterMeeting_Long"]].values.tolist()
labels = df["Targetid"].values.tolist()
#m = folium.Map(location=[21.44880645, 77.22538133], zoom_start=8)
m=folium.Map(location=[location[["Client_Lat"]].mean(),location[["Client_Long"]].mean()],zoom_start=10)
   
for point in range(len(Clientlist)):
    #icon=folium.Icon(color='darkblue', icon_color='white', icon='male', angle=0
    #folium.Circle(location=Clientlist[point],color='green',weight=5, popup=labels[point]).add_to(m)
    
    folium.Marker(location=Clientlist[point],icon=folium.Icon(color='darkblue', icon_color='white', icon='male',
                  angle=1,prefix='fa'),
                  tooltip='Distance From Old Center:'+df['Client TO First Center Meeting Distance'][point]+" KM" +"</br>" + 
                  ' Distance From Recent Center '+df['Client To Last Center Meeting Distance'][point]+" KM").add_to(m)  
    folium.Marker(location=FirstCenter[point],icon=folium.Icon(color='Red', icon_color='white')).add_to(m)
    folium.Marker(location=LastCenter[point],icon=folium.Icon(color='green', icon_color='yellow')).add_to(m)
    #folium.Circle(location=FirstCenter[point],color='red', popup=labels[point]).add_to(m)  
    ##folium.Circle(location=LastCenter[point],color='yellow', popup=labels[point]).add_to(m) 
    folium.plugins.PolyLineOffset(locations=[Clientlist[point], FirstCenter[point]],weight=1, color='red').add_to(m)
    folium.plugins.PolyLineOffset(locations=[Clientlist[point], LastCenter[point]],weight=2, color='green').add_to(m)   
    arrows = getArrows(locations=[Clientlist[point], FirstCenter[point]])
    for arrow in arrows:
        arrow.add_to(m)
    arrows1 = getArrows(locations=[Clientlist[point], LastCenter[point]])
    for arrow in arrows1:
        arrow.add_to(m)
    
table= pd.pivot_table(location,values='Targetid', index='Last Center To Client Distance Bucket',
       columns='First Center To Client Distance Bucket',margins=True,margins_name="Total",fill_value=0,aggfunc='count')
st.write = ("Selectetd Center" + str(centerid) + "Have")
st.dataframe(table, use_container_width=True)
    #m 
        
      

    #folium.LayerControl().add_to(m)
    ##st_data = st_folium(m, width=725)
folium_static(m)


