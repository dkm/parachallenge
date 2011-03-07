#!/usr/bin/env python

# Based on :
# This comes from http://www.ninemoreminutes.com/2009/12/google-maps-with-python-and-kml/
#

# Copyright (c) 2011 Nine More Minutes, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# - Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# - Neither the name of Nine More Minutes, Inc. nor the names of its
#   contributors may be used to endorse or promote products derived from this
#   software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import csv
import sys
import time
import urllib
import urlparse
import xml.dom.minidom

GMAPS_API_KEY = ''

class Element(xml.dom.minidom.Element):

    def writexml(self, writer, indent="", addindent="", newl=""):
        # indent = current indentation
        # addindent = indentation to add to higher levels
        # newl = newline string
        writer.write(indent+"<" + self.tagName)

        attrs = self._get_attributes()
        a_names = attrs.keys()
        a_names.sort()

        for a_name in a_names:
            writer.write(" %s=\"" % a_name)
            xml.dom.minidom._write_data(writer, attrs[a_name].value)
            writer.write("\"")
        if self.childNodes:
            newl2 = newl
            if len(self.childNodes) == 1 and \
                self.childNodes[0].nodeType == xml.dom.minidom.Node.TEXT_NODE:
                indent, addindent, newl = "", "", ""
            writer.write(">%s"%(newl))
            for node in self.childNodes:
                node.writexml(writer,indent+addindent,addindent,newl)
            writer.write("%s</%s>%s" % (indent,self.tagName,newl2))
        else:
            writer.write("/>%s"%(newl))

# Monkey patch Element class to use our subclass instead.
xml.dom.minidom.Element = Element

def create_document(title, description=''):
    """Create the overall KML document."""
    doc = xml.dom.minidom.Document()
    kml = doc.createElement('kml')
    kml.setAttribute('xmlns', 'http://www.opengis.net/kml/2.2')
    doc.appendChild(kml)
    document = doc.createElement('Document')
    kml.appendChild(document)
    docName = doc.createElement('name')
    document.appendChild(docName)
    docName_text = doc.createTextNode(title)
    docName.appendChild(docName_text)
    docDesc = doc.createElement('description')
    document.appendChild(docDesc)
    docDesc_text = doc.createTextNode(description)
    docDesc.appendChild(docDesc_text)

    style_doc = create_style('takeoff', 
                             'http://maps.google.com/mapfiles/kml/paddle/wht-stars.png')
    document.appendChild(style_doc.documentElement)

    style_doc = create_style('waypoint', 
                             'http://maps.google.com/mapfiles/kml/paddle/wht-blank.png')
    document.appendChild(style_doc.documentElement)

    style_doc = create_style('landing', 
                             'http://maps.google.com/mapfiles/kml/paddle/red-stars.png')
    document.appendChild(style_doc.documentElement)

    line_style = create_linestyle("trackstyle")
    document.appendChild(line_style.documentElement)

    return doc

def create_linestyle(style_id):
    doc = xml.dom.minidom.Document()
    
    mstyle = doc.createElement("Style")
    mstyle.setAttribute("id", style_id)
    doc.appendChild(mstyle)
    
    style = doc.createElement("LineStyle")
    mstyle.appendChild(style)

    color = doc.createElement("color")
    style.appendChild(color)
    col_text = doc.createTextNode("ff000000")
    color.appendChild(col_text)
    width = doc.createElement("width")
    style.appendChild(width)
    width_text = doc.createTextNode("5")
    width.appendChild(width_text)
    return doc

def create_style(style_id, icon_href):
    """Create a new style for different placemark icons."""
    doc = xml.dom.minidom.Document()
    style = doc.createElement('Style')
    style.setAttribute('id', style_id)
    doc.appendChild(style)
    icon_style = doc.createElement('IconStyle')
    style.appendChild(icon_style)
    icon = doc.createElement('Icon')
    icon_style.appendChild(icon)
    href = doc.createElement('href')
    icon.appendChild(href)
    href_text = doc.createTextNode(icon_href)
    href.appendChild(href_text)
    return doc

# def create_placemark(address):
#     """Generate the KML Placemark for a given address."""
#     doc = xml.dom.minidom.Document()
#     pm = doc.createElement("Placemark")
#     doc.appendChild(pm)
#     name = doc.createElement("name")
#     pm.appendChild(name)
#     name_text = doc.createTextNode('%(name)s' % address)
#     name.appendChild(name_text)
#     desc = doc.createElement("description")
#     pm.appendChild(desc)
#     desc_text = doc.createTextNode(address.get('phone', ''))
#     desc.appendChild(desc_text)
#     if address.get('county', ''):
#         style_url = doc.createElement("styleUrl")
#         pm.appendChild(style_url)
#         style_url_text = doc.createTextNode('#%(county)s' % address)
#         style_url.appendChild(style_url_text)
#     pt = doc.createElement("Point")
#     pm.appendChild(pt)
#     coords = doc.createElement("coordinates")
#     pt.appendChild(coords)
#     coords_text = doc.createTextNode('%(longitude)s,%(latitude)s,0' % address)
#     coords.appendChild(coords_text)
#     return doc


def create_linestring(points):
    #     <LineString>
    #   <tessellate>1</tessellate>
    #   <coordinates>
    #     -122.378009,37.830128,0 -122.377885,37.830379,0
    #   </coordinates>
    # </LineString>
    doc = xml.dom.minidom.Document()
    pm = doc.createElement("Placemark")
    doc.appendChild(pm)

    style_url = doc.createElement("styleUrl")
    pm.appendChild(style_url)

    style_url_text = doc.createTextNode('#trackstyle')
    style_url.appendChild(style_url_text)
    pm.appendChild(style_url)

    ls = doc.createElement("LineString")
    pm.appendChild(ls)
    
    tess = doc.createElement("tesselate")
    ls.appendChild(tess)
    text = doc.createTextNode("1")
    tess.appendChild(text)

    coords = doc.createElement("coordinates")
    ls.appendChild(coords)
    text = " ".join(['%s,%s,0' %(x.lon, x.lat) for x in points])
    coords_text = doc.createTextNode(text)
    coords.appendChild(coords_text)

    return doc

def create_placemark(waypoint, t="waypoint", dist=None):
    """Generate the KML Placemark for a waypoint."""
    doc = xml.dom.minidom.Document()
    pm = doc.createElement("Placemark")
    doc.appendChild(pm)
    name = doc.createElement("name")
    pm.appendChild(name)

    if dist:
        fulltext = '%s (%d points) %0.2f km' % (waypoint.name, waypoint.points, dist)
    else:
        fulltext = '%s (%d points)' % (waypoint.name, waypoint.points)

    if t in ['landing', 'takeoff']:
        fulltext = '[%s] %s' %(t.upper(), fulltext)

    name_text = doc.createTextNode(fulltext)
    name.appendChild(name_text)
    style_url = doc.createElement("styleUrl")
    pm.appendChild(style_url)

    style_url_text = doc.createTextNode('#%s' % t)
    style_url.appendChild(style_url_text)


    # desc = doc.createElement("description")
    # pm.appendChild(desc)
    # desc_text = doc.createTextNode(address.get('phone', ''))
    # desc.appendChild(desc_text)
    # if address.get('county', ''):
    #     style_url = doc.createElement("styleUrl")
    #     pm.appendChild(style_url)
    #     style_url_text = doc.createTextNode('#%(county)s' % address)
    #     style_url.appendChild(style_url_text)
    pt = doc.createElement("Point")
    pm.appendChild(pt)
    coords = doc.createElement("coordinates")
    pt.appendChild(coords)

    coords_text = doc.createTextNode('%s,%s,0' % (waypoint.lon, waypoint.lat))
    coords.appendChild(coords_text)
    return doc

# def geocode(address):
#     """Geocode the given address, updating the standardized address, latitude,
#     and longitude."""
#     qs = dict(q=address['address_string'], key=GMAPS_API_KEY, sensor='true',
#               output='csv')
#     qs = urllib.urlencode(qs)
#     url = urlparse.urlunsplit(('http', 'maps.google.com', '/maps/geo', qs, ''))
#     f = urllib.urlopen(url)
#     result = list(csv.DictReader(f, ('status', 'accurary', 'latitude', 'longitude')))[0]
#     if int(result['status']) != 200:
#         raise RuntimeError, 'could not geocode address %s (%s)' % \
#                             (address, result['status'])
#     address['latitude'] = result['latitude']
#     address['longitude'] = result['longitude']
#     time.sleep(1.0)

# def read_addresses(filename):
#     """Retrieve addresses from the given CSV filename."""
#     required_fields = set(['name', 'address', 'city', 'zip'])
#     reader = csv.DictReader(file(filename, 'rU'))
#     for row in reader:
#         if not all(row.get(f, '').strip() for f in required_fields):
#             continue
#         yield row

# if __name__ == '__main__':
#     kml_doc = create_document('RDU Bojangle\'s',
#                               'Sweet Tea, Chicken and Biscuits')
#     document = kml_doc.documentElement.getElementsByTagName('Document')[0]
#     style_doc = create_style('Wake', \
#         'http://maps.google.com/mapfiles/kml/paddle/red-blank.png')
#     document.appendChild(style_doc.documentElement)
#     style_doc = create_style('Durham', \
#         'http://maps.google.com/mapfiles/kml/paddle/blu-blank.png')
#     document.appendChild(style_doc.documentElement)
#     style_doc = create_style('Orange', \
#         'http://maps.google.com/mapfiles/kml/paddle/wht-blank.png')
#     document.appendChild(style_doc.documentElement)
#     for address in read_addresses(sys.argv[1]):
#         address['address_string'] = \
#             '%(address)s, %(city)s, %(state)s %(zip)s' % address
#         try:
#             geocode(address)
#         except RuntimeError, e:
#             print >> sys.stderr, e
#             print >> sys.stderr, "warning: %s skipped" % address['address_string']
#             continue
#         placemark = create_placemark(address)
#         document.appendChild(placemark.documentElement)
#     print kml_doc.toprettyxml(indent="  ", encoding='UTF-8')
