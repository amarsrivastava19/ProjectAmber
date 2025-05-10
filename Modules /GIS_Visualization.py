import requests
import osmnx as ox
from math import radians, cos, sin, sqrt, atan2
from dotenv import load_dotenv
import os

load_dotenv()  
google_key = os.getenv('GOOGLE_MAPS_KEY')

def Geocoder(address, api_key):
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": api_key}
    response = requests.get(url, params=params)
    data = response.json()
    
    if data["status"] == "OK":
        location = data["results"][0]["geometry"]["location"]
        return location["lat"], location["lng"]
    else:
        return None

def GenerateGraph():
    north = 41.750
    south = 41.450
    east = -93.400
    west = -93.900

    custom_filter = ('["highway"~"motorway|trunk|primary|secondary|tertiary|residential"]')
    graph = ox.graph_from_bbox((west, south, east, north),
                               custom_filter=custom_filter)

    return graph
    


def GraphToNetwork(graph, state_abbr = 'IA', epsg = 3417):    
    nodes, edges = ox.graph_to_gdfs(graph, nodes=True, edges=True)
    edges = edges.reset_index(drop=False)  
    nodes = nodes.reset_index(drop=False)[['osmid', 'x','y']]
    nodes['State'] = state_abbr
    nodes['Node'] = nodes['State'] + nodes['osmid'].astype('str')
    edges = edges.to_crs(epsg=epsg)
    edges['length'] = edges.geometry.length
    edges = edges[['u','v','length']]
    edges['u'] = state_abbr + edges['u'].astype('str')
    edges['v'] = state_abbr + edges['v'].astype('str')
    return nodes, edges

def Haversine(lat1, lon1, lat2, lon2):
    R = 6371 
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def FindClosestNode(nodes, target_y, target_x):
    nodes['distance'] = nodes.apply(lambda row: Haversine(target_y, target_x, row['y'], row['x']), axis=1)
    closest_node = nodes.loc[nodes['distance'].idxmin()]
    return closest_node.osmid


def VisualizeGraph(dataExtract):
    
    if dataExtract['LastSeenVictimLocation'] != 'NONE':
        victimLat, victimLon = Geocoder(sample_data['LastSeenVictimLocation'], google_key)
    else:
        victimLat = None
        victimLon = None
        
    if dataExtract['LastSeenSuspectLocation'] != 'NONE':
        suspectLat, suspectLon = Geocoder(sample_data['LastSeenVictimLocation'], google_key)
    else:
        suspectLat = None
        suspectLon = None

    if 'graph' not in locals():
        graph = GenerateGraph()
    
    nodes,edges = GraphToNetwork(graph)
    
    if victimLat: 
        nodes['distanceToVictim'] = nodes.apply(lambda row: Haversine(victimLat, victimLon, row['y'], row['x']), axis=1)
        victimNodes = nodes[nodes['distanceToVictim'] < 0.75]['osmid'].tolist()
    else:
        victimNodes = []
        
    if suspectLat: 
        nodes['distanceToVictim'] = nodes.apply(lambda row: Haversine(suspectLat, suspectLon, row['y'], row['x']), axis=1)   
        suspectNodes = nodes[nodes['distanceToSuspect'] < 0.75]['osmid'].tolist()
    else:
        suspectNodes = []
        
    node_color = ['red' if node in victimNodes or node in suspectNodes else 'gray' for node in graph.nodes()]

    # Plot the graph
    fig, ax = ox.plot_graph(
        graph,
        node_color=node_color,
        node_size=node_size,
        edge_color='white',
        edge_linewidth=0.5,
        bgcolor='black',
        show=True,
        close=False,
        figsize = (25,30)
    )
    return None


if __name__ == "__main__":
    
    sample_data = {'SuspectName': 'NONE', 
                   'VehicleMake': 'Chevy', 
                   'VehicleModel': 'Tahoe', 
                   'VehicleColor': 'Dark Blue', 
                   'LicensePlate': 'JVK129', 
                   'LastSeenVictimLocation': 'Union Park in Des Moines', 
                   'LastSeenVictimTime': '4:12 PM', 
                   'LastSeenSuspectLocation': 'NONE', 
                   'LastSeenSuspectTime': 'NONE', 
                   'Heading': 'East on I-235'}
    
    VisualizeGraph(sample_data)
