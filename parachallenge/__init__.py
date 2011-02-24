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

from Cheetah.Template import Template
import makemaps
import pyproj
import re
import ConfigParser

UTM_RE = re.compile("(?P<lat>\d+(\.\d*)?)\s*N\s*(?P<lon>\d+(\.\d*)?)\s*E\s*(?P<zone>\d+)\s*T\s*")

WGS84_GEOD = pyproj.Geod(ellps='WGS84')

FICHE_ENCODING="utf-8"

import json

class ParachallengeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Cross) or isinstance(obj, Pilot) or isinstance(obj,Waypoint) or isinstance(obj, Declaration):
            return obj.toMap()

        return json.JSONEncoder.default(self, obj)

class Pilot:
    def __init__(self, name):
        self.name = unicode(name)
        self.points = 0
        self.distance = 0

    def toMap(self):
        m = { 'name' : self.name,
              'points' : self.points,
              'distance' : self.distance}
        return m

    def __unicode__(self):
        return self.name + u" " + u"|".join([unicode(self.points), 
                                             unicode(self.distance)])
    def __str__(self):
        return self.__unicode__().encode("utf-8")

class Declaration:
    def __init__(self, pilot, date, cross, last_balise):
        self.pilot = unicode(pilot)
        self.date = unicode(date)
        self.cross = cross
        self.last_balise = int(last_balise)
        
        self.distance = 0
        self.points = 0
        prev = self.cross.takeoff

        for i,b in enumerate(self.cross.waypoints + [self.cross.landing]):
            if i > self.last_balise:
                break

            self.distance += b.distance_to(prev)
            self.points += b.points
            prev = b
        
    def toMap(self):
        # do not embed the full cross object, simply its fid.
        m = { 'pilot' : self.pilot,
              'date' : self.date,
              'cross' : self.cross.fid,
              'last_balise' : self.last_balise,
              'distance' : self.distance,
              'points': self.points}
        return m

    def __unicode__(self):
        s = u"||".join([u'Declaration',self.pilot, self.date, unicode(self.cross.fid), unicode(self.last_balise), unicode(self.distance), unicode(self.points)])
        return s
   
    def __str__(self):
        return self.__unicode__().encode("utf-8")

class Waypoint:
    def __init__(self, name, coords, points=0):
        self.coords = coords
        self.name = name
        self.points = points

    def toMap(self):
        m = { 'coords' : self.coords,
              'name' : self.name,
              'points' : self.points}
        return m

    def distance_to(self, other):
        fwd,back,dist = WGS84_GEOD.inv(self.coords[0], self.coords[1],
                                       other.coords[0], other.coords[1])
        return dist/1000.0

    def __unicode__(self):
        return unicode(self.coords[0]) + u", " + unicode(self.coords[1])+ u" | " + self.name
    
    def __str__(self):
        return self.__unicode__().encode("utf-8")

    def __getattr__(self, name):
        if name == 'lon':
            return self.coords[0]
        elif name == 'lat':
            return self.coords[1]
        
class Cross:
    def __init__(self, name, difficulty, description, 
                 takeoff, landing, waypoints, fid):
        self.name = name
        self.difficulty = difficulty
        self.description = description
        self.waypoints = waypoints
        self.takeoff = takeoff
        self.landing = landing
        self.distance = -1
        self.points = 0
        self.fid = int(fid)

    def toMap(self):
        m = { 'name': self.name,
              'difficulty' : self.difficulty,
              'description' : self.description,
              'waypoints': self.waypoints,
              'takeoff' : self.takeoff,
              'landing' : self.landing,
              'distance' : self.distance,
              'points' : self.points,
              'fid' : self.fid}
        return m

    def __unicode__(self):
        if self.distance == -1:
            self.compute_distance()

        retstr =  u"Name:" + self.name + u"/"
        retstr =  u"FId:" + self.fid + u"/"
        retstr += u"Difficulte:" + self.difficulty + u"/"
        retstr += u"Distance:" + unicode(self.distance) + u"/"
        retstr += u"Points:" + unicode(self.points) + u"/"
        retstr += u"Description:" + self.description + u"/"
        retstr += u"Deco:" + unicode(self.takeoff)
        retstr += u"Balises:"+ "/".join([unicode(x) for x in self.waypoints])
        retstr += u"Aterro:" + unicode(self.landing)
        return retstr

    def __str__(self):
        return self.__unicode__().encode("utf-8")

    def compute_distance(self):
        prev_wpt = self.takeoff
        d = 0
        points = 0
        prev_p = self.takeoff

        for p in self.waypoints:
            d += prev_wpt.distance_to(p)
            points += p.points
            prev_p = p
        d += prev_p.distance_to(self.landing)
        points += self.landing.points
        self.distance = d
        self.points = points
    
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

        placemark = makemaps.create_placemark(self.takeoff, "takeoff")
        document.appendChild(placemark.documentElement)
        prev = self.takeoff

        for w in self.waypoints:
            dist = prev.distance_to(w)
            placemark = makemaps.create_placemark(w, dist=dist)
            document.appendChild(placemark.documentElement)

        placemark = makemaps.create_placemark(self.landing, "landing")
        document.appendChild(placemark.documentElement)

        ls = makemaps.create_linestring([self.takeoff] + self.waypoints + [self.landing])
        document.appendChild(ls.documentElement)

        return kml_doc.toprettyxml(indent="  ", encoding='UTF-8')

    def toRST(self):
        if self.distance == -1:
            self.compute_distance()

        r = ""
        r += self.name + "\n"
        r += '='*(len(self.name)) + '\n'

        r += '-' + ' ' + 'Difficulty: ' + self.difficulty + '\n'
        r += '-' + ' ' + 'Distance: ' + "%.2f" % self.distance + ' km\n'
        r += '-' + ' ' + 'Points: ' + "%d" % self.points + '\n\n'
        r += 'Description\n'
        r += "-"*(len('Description\n')-1) + '\n'
        r += self.description + '\n\n'

        r += 'Trajet\n'
        r += "-"*(len('Trajet\n')-1) + '\n'
        r += '- Decolage : ' + unicode(self.takeoff) + '\n\n'
        
        i = 1
        p = self.takeoff
        for w in self.waypoints:
            r += ' - B%d:' % i + " " + unicode(w) +'(%.2f km / %d pts)\n' % (p.distance_to(w), p.points)
            i += 1
            p = w

        if len(self.waypoints)>0:
            r += "\n"

        r += '- Atterissage : ' + unicode(self.landing) + '(%.2f km)\n' % self.landing.distance_to(p)
        r += "\n"

        return r.encode('utf-8')


    def toHTML(self, kmlfile, pdffile, sitebase):
        t = Template(file='templates/fiche.cheetah')
        t.cross = self
        t.kmlfile = kmlfile
        t.pdffile = pdffile
        t.sitebase = sitebase
        return t


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

def loadDeclarationFromIni(filename, cross):
    config = ConfigParser.ConfigParser()
    config.read(filename)

    pilot_name = config.get('declaration', 'pilot').decode(FICHE_ENCODING)
    decl_date = config.get('declaration', 'date').decode(FICHE_ENCODING)
    decl_cross_id = int(config.get('declaration', 'cross').decode(FICHE_ENCODING))
    decl_last_wpt = config.get('declaration', 'last_balise').decode(FICHE_ENCODING)

    return Declaration(pilot_name, decl_date, cross[decl_cross_id], decl_last_wpt)

def loadFichesFromIni(filename, debug=False):
    config = ConfigParser.ConfigParser()
    config.read(filename)

    titre = config.get('general', 'titre').decode(FICHE_ENCODING)
    fid = config.get('general', 'id').decode(FICHE_ENCODING)
    descr = config.get('general', 'description').decode(FICHE_ENCODING)
    ##diff = config.get('general', 'difficulté').decode(FICHE_ENCODING)
    diff = u""
    for name,val in config.items('general'):
        if name.decode(FICHE_ENCODING).startswith(u'difficult'):
            diff = val.decode(FICHE_ENCODING)
            break

    if debug and not diff:
        print "WARNING: No difficulty"
    
    deco_str = config.get('trajet', 'deco').decode(FICHE_ENCODING)
    atterro_str = config.get('trajet', 'atterro').decode(FICHE_ENCODING)
    
    vals = [x.strip() for x in deco_str.split('|')]
    if len(vals) == 3:
        deco_utm_str, deco_name, deco_points = vals
    else:
        deco_utm_str, deco_name, deco_points = vals + [0]

    vals = [x.strip() for x in atterro_str.split('|')]
    if len(vals) == 3:
        atterro_utm_str, atterro_name, atterro_points = vals
    else:
        atterro_utm_str, atterro_name, atterro_points = vals + [0]

    deco = Waypoint(deco_name, unpackUTM(deco_utm_str), int(deco_points))
    atterro = Waypoint(atterro_name, unpackUTM(atterro_utm_str), int(atterro_points))

    waypoints = []
    for name,val in config.items('trajet'):
        name = name.decode(FICHE_ENCODING)
        val = val.decode(FICHE_ENCODING)
        m = re.match("b(?P<idx>\d+)", name)
        if m:
            vals = [x.strip() for x in val.split('|')]
            if len(vals) == 3:
                b_utm_str, b_name, b_points = vals
            else:
                b_utm_str, b_name, b_points = vals + [0]

            waypoints.append(Waypoint("B%s %s" %(m.group('idx'), b_name), 
                                      unpackUTM(b_utm_str), int(b_points)))

    c = Cross(titre, diff, descr, deco, atterro, waypoints, fid=fid)
    return c
