#!/usr/bin/env python
# coding=utf-8

import math

import makemaps

def distance_on_unit_sphere(lat1, long1, lat2, long2):
    """
    taken from http://www.johndcook.com/python_longitude_latitude.html
    """

    # Convert latitude and longitude to 
    # spherical coordinates in radians.
    degrees_to_radians = math.pi/180.0
        
    # phi = 90 - latitude
    phi1 = (90.0 - lat1)*degrees_to_radians
    phi2 = (90.0 - lat2)*degrees_to_radians
        
    # theta = longitude
    theta1 = long1*degrees_to_radians
    theta2 = long2*degrees_to_radians
        
    # Compute spherical distance from spherical coordinates.
        
    # For two locations in spherical coordinates 
    # (1, theta, phi) and (1, theta, phi)
    # cosine( arc length ) = 
    #    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
    # distance = rho * arc length
    
    cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + 
           math.cos(phi1)*math.cos(phi2))
    arc = math.acos( cos )

    # Remember to multiply arc by the radius of the earth 
    # in your favorite set of units to get length.
    return arc * 6373


class Waypoint:
    def __init__(self, lat, lon, name):
        self.lat = lat
        self.lon = lon
        self.name = name

    def distance_to(self, other):
        return distance_on_unit_sphere(self.lat, self.lon, other.lat, other.lon)

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
        self.distance = -1

    def __str__(self):
        if self.distance == -1:
            self.compute_distance()

        retstr =  "Name:" + self.name + "/"
        retstr += "Difficulté:" + self.difficulty + "/"
        retstr += "Distance:" + str(self.distance) + "/"
        retstr += "Description:" + self.description + "/"
        retstr += "Deco:" + str(self.takeoff)
        retstr += "Balises:"+ "/".join([str(x) for x in self.waypoints])
        retstr += "Atterro:" + str(self.landing)
        return retstr

    def compute_distance(self):
        prev_wpt = self.takeoff
        d = 0

        for p in self.waypoints:
            d += prev_wpt.distance_to(p) 
            prev_p = p
        d += prev_p.distance_to(self.landing)
        self.distance = d
    
    def toKML(self):
        kml_doc = makemaps.create_document(self.name,
                                           self.description)
        document = kml_doc.documentElement.getElementsByTagName('Document')[0]
        style_doc = makemaps.create_style('Wake',
             'http://maps.google.com/mapfiles/kml/paddle/red-blank.png')
        document.appendChild(style_doc.documentElement)
        style_doc = makemaps.create_style('Durham',
           'http://maps.google.com/mapfiles/kml/paddle/blu-blank.png')
        document.appendChild(style_doc.documentElement)
        style_doc = makemaps.create_style('Orange',
           'http://maps.google.com/mapfiles/kml/paddle/wht-blank.png')
        document.appendChild(style_doc.documentElement)
        placemark = makemaps.create_placemark(self.takeoff)
        document.appendChild(placemark.documentElement)
        
        for w in self.waypoints:
            placemark = makemaps.create_placemark(w)
            document.appendChild(placemark.documentElement)

        placemark = makemaps.create_placemark(self.landing)
        document.appendChild(placemark.documentElement)

        return kml_doc.toprettyxml(indent="  ", encoding='UTF-8')

    def toRST(self):
        if self.distance == -1:
            self.compute_distance()

        r = ""
        r += self.name + "\n"
        r += '='*(len(self.name)-1) + '\n'

        r += '-' + ' ' + 'Difficulty: ' + self.difficulty + '\n'
        r += '-' + ' ' + 'Distance: ' + "%.2f" % self.distance + ' km\n\n'
        r += 'Description\n'
        r += "-"*(len('Description\n')-1) + '\n'
        r += self.description + '\n\n'

        r += 'Trajet\n'
        r += "-"*(len('Trajet\n')-1) + '\n'
        r += '- Decolage : ' + str(self.takeoff) + '\n'
        
        i = 1
        p = self.takeoff
        for w in self.waypoints:
            r += ' - B%d:' % i + " " + str(w) +'(%.2f km)\n' % p.distance_to(w)
            i += 1
            p = w
        
        r += '- Atterissage : ' + str(self.landing) + '(%.2f km)\n' % self.landing.distance_to(p)

        return r
