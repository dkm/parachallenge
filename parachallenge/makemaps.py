#!/usr/bin/env python
#
# This comes from http://www.ninemoreminutes.com/2009/12/google-maps-with-python-and-kml/
#

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

def create_placemark(address):
    """Generate the KML Placemark for a given address."""
    doc = xml.dom.minidom.Document()
    pm = doc.createElement("Placemark")
    doc.appendChild(pm)
    name = doc.createElement("name")
    pm.appendChild(name)
    name_text = doc.createTextNode('%(name)s' % address)
    name.appendChild(name_text)
    desc = doc.createElement("description")
    pm.appendChild(desc)
    desc_text = doc.createTextNode(address.get('phone', ''))
    desc.appendChild(desc_text)
    if address.get('county', ''):
        style_url = doc.createElement("styleUrl")
        pm.appendChild(style_url)
        style_url_text = doc.createTextNode('#%(county)s' % address)
        style_url.appendChild(style_url_text)
    pt = doc.createElement("Point")
    pm.appendChild(pt)
    coords = doc.createElement("coordinates")
    pt.appendChild(coords)
    coords_text = doc.createTextNode('%(longitude)s,%(latitude)s,0' % address)
    coords.appendChild(coords_text)
    return doc

def create_placemark(waypoint):
    """Generate the KML Placemark for a waypoint."""
    doc = xml.dom.minidom.Document()
    pm = doc.createElement("Placemark")
    doc.appendChild(pm)
    name = doc.createElement("name")
    pm.appendChild(name)
    name_text = doc.createTextNode('%s' % waypoint.name)
    name.appendChild(name_text)
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
