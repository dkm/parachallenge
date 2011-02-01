#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#   parachallenge
#   Copyright (C) 2010  Marc Poulhiès
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

import math

import makemaps
import pyproj
import re
import ConfigParser

UTM_RE = re.compile("(?P<lon>\d+(\.\d*)?)\s*N\s*(?P<lat>\d+(\.\d*)?)\s*E\s*(?P<zone>\d+)\s*T\s*")

WGS84_GEOD = pyproj.Geod(ellps='WGS84')

class Waypoint:
    def __init__(self, name, coords):
        self.coords = coords
        self.name = name

    def distance_to(self, other):
        fwd,back,dist = WGS84_GEOD.inv(self.coords[0], self.coords[1],
                                       other.coords[0], other.coords[1])
        return dist/1000.0

    def __unicode__(self):
        return unicode(self.coords[0]) + u", " + unicode(self.coords[1])+ u" | " + self.name
        
    def __getattr__(self, name):
        if name == 'lon':
            return self.coords[0]
        elif name == 'lat':
            return self.coords[1]
        
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

    def __unicode__(self):
        if self.distance == -1:
            self.compute_distance()

        retstr =  u"Name:" + self.name + u"/"
        retstr += u"Difficulte:" + self.difficulty + u"/"
        retstr += u"Distance:" + unicode(self.distance) + u"/"
        retstr += u"Description:" + self.description + u"/"
        retstr += u"Deco:" + unicode(self.takeoff)
        retstr += u"Balises:"+ "/".join([unicode(x) for x in self.waypoints])
        retstr += u"Aterro:" + unicode(self.landing)
        return retstr

    def compute_distance(self):
        prev_wpt = self.takeoff
        d = 0
        prev_p = self.takeoff

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
        r += '='*(len(self.name)) + '\n'

        r += '-' + ' ' + 'Difficulty: ' + self.difficulty + '\n'
        r += '-' + ' ' + 'Distance: ' + "%.2f" % self.distance + ' km\n\n'
        r += 'Description\n'
        r += "-"*(len('Description\n')-1) + '\n'
        r += self.description + '\n\n'

        r += 'Trajet\n'
        r += "-"*(len('Trajet\n')-1) + '\n'
        r += '- Decolage : ' + unicode(self.takeoff) + '\n'
        
        i = 1
        p = self.takeoff
        for w in self.waypoints:
            r += ' - B%d:' % i + " " + unicode(w) +'(%.2f km)\n' % p.distance_to(w)
            i += 1
            p = w
        r += "\n"

        r += '- Atterissage : ' + unicode(self.landing) + '(%.2f km)\n' % self.landing.distance_to(p)
        r += "\n"

        return r.encode('utf-8')

def unpackUTM(utmstring):
    m = UTM_RE.match(utmstring)
    if m:
        return getLatLonFromUTM(m.group('lon'), m.group('lat'), m.group('zone'))
    else:
        print "Can't match UTM in '%s'" %utmstring
        return None

def getLatLonFromUTM(easting, northing, zone):
    utm = pyproj.Proj(proj='utm', zone=zone)
    
    lon,lat = utm(float(easting), float(northing), inverse=True)
    
    return (lon,lat)

def loadFromIni(filename, debug=False):
    config = ConfigParser.ConfigParser()
    config.read(filename)

    titre = config.get('general', 'titre').decode("iso-8859-15")
    descr = config.get('general', 'description').decode("iso-8859-15")
    ##diff = config.get('general', 'difficulté').decode("iso-8859-15")
    diff = u""
    for name,val in config.items('general'):
        if name.decode("iso-8859-15").startswith(u'difficult'):
            diff = val.decode("iso-8859-15")
            break

    if debug and not diff:
        print "WARNING: No difficulty"
    
    deco_str = config.get('trajet', 'deco').decode("iso-8859-15")
    atterro_str = config.get('trajet', 'atterro').decode("iso-8859-15")
    
    deco_utm_str, deco_name = [x.strip() for x in deco_str.split('|')]
    atterro_utm_str, atterro_name = [x.strip() for x in atterro_str.split('|')]

    deco = Waypoint(deco_name, unpackUTM(deco_utm_str))
    atterro = Waypoint(atterro_name, unpackUTM(atterro_utm_str))

    waypoints = []
    for name,val in config.items('trajet'):
        name = name.decode("iso-8859-15")
        val = val.decode("iso-8859-15")
        m = re.match("b(?P<idx>\d+)", name)
        if m:
            b_utm_str, b_name = [x.strip() for x in val.split('|')]
            waypoints.append(Waypoint("B%s %s" %(m.group('idx'), b_name), 
                                      unpackUTM(b_utm_str)))

    c = Cross(titre, diff, descr, deco, atterro, waypoints)
    return c
