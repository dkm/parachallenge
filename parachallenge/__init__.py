#!/usr/bin/env python
# coding=utf-8

class Waypoint:
    def __init__(self, lat, lon, name):
        self.lat = lat
        self.lon = lon
        self.name = name

    def __str__(self):
        return str(self.lat) + ", " + str(self.lon)+ " | " + self.name
        
class Cross:
    def __init__(self, name, difficulty, description, 
                 takeoff, landing, waypoints):
        self.name = name
        self.difficulty = difficulty
        self.description = description
        self.waypoints = waypoints
        self.takeoff = takeoff
        self.landing = landing

    def __str__(self):
        retstr =  "Name:" + self.name + "/"
        retstr += "Difficulté:" + self.difficulty + "/"
        retstr += "Description:" + self.description + "/"
        retstr += "Deco:" + str(self.takeoff)
        retstr += "Balises:"+ "/".join([str(x) for x in self.waypoints])
        retstr += "Atterro:" + str(self.landing)
        return retstr

