#!/usr/bin/env python
# coding=utf-8

class Waypoint:
    def __init__(self, lat, lon, name):
        self.lat = lat
        self.lon = lon
        self.name = name

    def __str__(self):
        return "Balise:" + self.lat + "," + self.lon + self.name
        
class Cross:
    def __init__(self,name,difficulty,description,waypoints):
        self.name = name
        self.difficulty = difficulty
        self.description = description
        self.waypoints = waypoints

    def __str__(self):
        retstr =  "Name:" + self.name + "/"
        retstr += "Difficulté:" + self.difficulty + "/"
        retstr += "Description:" + self.description + "/"
        retstr += "Balises:"+ "/".join([str(x) for x in self.waypoints])
        return retstr

