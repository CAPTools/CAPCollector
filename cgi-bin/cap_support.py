#     cap_support.py -- python support objects for CAPCollector (post_cap.py)
#     version 0.9.2 - 29 November 2013
#     
#     Copyright (c) 2013, Carnegie Mellon University
#     All rights reserved.
# 
#    See LICENSE.txt for license terms (Modified BSD) 
#
#     REQUIRES PYTHON MODULES pytz, iso8601, lxml, pam, xmldsig
#     (pam module is from the web2py framework: https://code.google.com/p/web2py/source/browse/gluon/contrib/pam.py)
#     (xmldsig has some installation peculiarities and dependencies, see https://github.com/AntagonistHQ/xmldsig)
#     (xmldsig requires libxml2, libsxlt and libxmlsec)

from datetime import datetime, timedelta
import pytz
import iso8601
from lxml import etree
import uuid
import os
import dateutil.parser
import pam

cap_ns = "urn:oasis:names:tc:emergency:cap:1.2"

class Authenticator():
    
    @staticmethod
    def isAuthentic(uid, password ):
        return pam.authenticate(uid,password)
 
    
class Signer():
    
    @staticmethod
    def signCAP(uid, xml_string):
        return xml_string  # stub for now

    
class Filer():
    
    def __init__(self, config):
        self.path = config.path_to_data
        self.web_path = config.web_path_to_data
        self.expired_file_path = config.expired_file_path
        self.version = config.version
    
    def fileCAP(self, id, xml):
        f = self.path + "/" + id + ".xml"
        with open( f,"w" ) as cap_file:
            cap_file.write(xml+"\n")
        
    def reindex(self):  # rebuild ATOM index (may also be called periodically, e.g. from cron)
        
        af = self.path + '/index.atom'
        # build ATOM header
        timestamp = datetime.utcnow().isoformat().split(".")[0] + "+00:00"
        atom = '<?xml version = "1.0" encoding = "UTF-8"?>\n'
        atom = atom + '<feed xmlns="http://www.w3.org/2005/Atom" xmlns:cap="urn:oasis:names:tc:emergency:cap:1.2">\n'
        atom = atom + '<title>Current Alerts</title>\n'
        atom = atom + '<link href="' + self.web_path + '/index.atom" rel="self" />\n'
        atom = atom + '<id>' + self.web_path+ '</id>\n'
        atom = atom + '<updated>' + timestamp + '</updated>\n'
        atom = atom + '<generator>' + self.version + '</generator>\n'
 
        # get a directory list
        filelist = os.listdir(self.path)
        
        # for each unexpired message, get the necessary values and add <entry> to ATOM string
        for filename in filelist:
            
            if (filename != 'index.atom'):
                f = self.path + "/" + filename
                with open(f, "r") as cap_file:
                    xml_string = cap_file.read()
                    
                # skip (and relocate) this message if it's expired
                xml_tree = etree.fromstring( xml_string )
                expires_string = self.get_first_text( self.get_cap_element("expires", xml_tree) )
                expires_date = iso8601.parse_date(expires_string)
                if datetime.now(pytz.utc) > expires_date:
                    os.rename(f, self.expired_file_path + "/" + filename)  # move expired msg to expired directory        
                    continue  # and go on to the next message
                
                # else extract the other needed values from the CAP XML
                sender = self.get_first_text( self.get_cap_element("sender", xml_tree) )
                senderName = self.get_first_text( self.get_cap_element("senderName", xml_tree) )
                name =  sender
                if senderName != "":
                    name =  name + ": " + senderName
                id = self.get_first_text( self.get_cap_element("identifier", xml_tree) ) 
                urgency = self.get_first_text( self.get_cap_element("urgency", xml_tree) ) 
                severity = self.get_first_text( self.get_cap_element("severity", xml_tree) ) 
                certainty = self.get_first_text( self.get_cap_element("certainty", xml_tree) ) 
                category = self.get_first_text( self.get_cap_element("category", xml_tree) ) 
                responseType = self.get_first_text( self.get_cap_element("responseType", xml_tree) ) 
                title = self.get_first_text( self.get_cap_element("headline", xml_tree) )
                if title == "":
                    title = "Alert Message"  # force a default
                link = self.web_path + '/' + filename
                updated = self.get_first_text( self.get_cap_element("sent", xml_tree) )
                areaDesc = self.get_first_text( self.get_cap_element("areaDesc", xml_tree) )
                polys = self.get_all_text( self.get_cap_element("polygon", xml_tree) )
                circles = self.get_all_text( self.get_cap_element("circle", xml_tree) )
                
                 # and add the entry for this alert
                atom = atom + '<entry>\n'
                atom = atom + '  <author>\n'
                atom = atom + '    <name>' + name + '</name>\n'
                atom = atom + '  </author>\n'
                atom = atom + '  <title>' + title + '</title>\n'
                atom = atom + '  <updated>' + updated + '</updated>\n'
                atom = atom + '  <link href="' + link + '" rel="alternate" />\n'
                atom = atom + '  <id>uuid:' + id + '</id>\n'
                atom = atom + '  <cap:urgency>' + urgency + '</cap:urgency>\n'
                atom = atom + '  <cap:severity>' + severity + '</cap:severity>\n'
                atom = atom + '  <cap:certainty>' + certainty + '</cap:certainty>\n'
                atom = atom + '  <cap:category>' + category + '</cap:category>\n'
                atom = atom + '  <cap:responseType>' + responseType + '</cap:responseType>\n'
                atom = atom + '  <cap:expires>' + expires_string + '</cap:expires>\n'
                atom = atom + '  <cap:areaDesc>' + areaDesc + '</cap:areaDesc>\n'
                for poly in polys:
                    atom = atom + '  <cap:polygon>' + poly + '</cap:polygon>\n'
                for circle in circles:
                    atom = atom + '  <cap:circle>' + circle + '</cap:circle>\n'
                atom = atom + '</entry>\n'
                      
        # now complete the ATOM string
        atom = atom + '</feed>\n'
        
        # and write the updated ATOM index to file
        with open( self.path + '/index.atom',"w" ) as atom_file:
            atom_file.write( atom )
            
    # return the first text item from an XML element, trapping any None values
    def get_first_text(self, xml_element):
        if xml_element and len(xml_element):
            return str( xml_element[0].text )
        return ""
    
    # return an array of text items from multiple elements
    def get_all_text(self, xml_element):
        string_array = []
        if xml_element and len(xml_element):
            for item in xml_element:
                string_array.append( str(item.text) )
        return string_array
        
    # use lxml.XPath to extract elements from CAP XML tree
    def get_cap_element(self, element_name, xml_tree ):
        element = "//p:" + element_name
        finder = etree.XPath( element, namespaces={ 'p': cap_ns } )
        return finder( xml_tree )
        
        
class Forwarder():
    
    @staticmethod
    def forwardCAP(path, id):
        pass
        # forward as appropriate
   
        
# for testing only, force a manual reindex of messages
if __name__ == '__main__':
    from config import Config
    config = Config()
    filer = Filer( config )
    filer.reindex()
    