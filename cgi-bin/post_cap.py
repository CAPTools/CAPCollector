#! /usr/bin/python
#     post_cap.py -- python CGI for posting CAP XML (as POST) to CAPCollector
#     version 0.9.2 - 1 December 2013
#     
#     Copyright (c) 2013, Carnegie Mellon University
#     All rights reserved.
# 
#     See LICENSE.txt for license terms (Modified BSD) 
#     
#    REQUIRED PYTHON PACKAGES IN ENVIRONMENT:  pytz, ISO8601, lxml, pam, xml.dom.minidom
#     (pam module is from the web2py framework: https://code.google.com/p/web2py/source/browse/gluon/contrib/pam.py)
 
import cgi
from config import Config
import sys
import uuid
from lxml import etree
import pam
import xml.dom.minidom
import re

import sys

from cap_support import Signer, Filer, Forwarder


# load configuration variables
config_obj = Config();
sender_domain = config_obj.sender_domain
path_to_data = config_obj.path_to_data 
web_path_to_data = config_obj.web_path_to_data
expired_file_path = config_obj.expired_file_path
cap_ns = config_obj.cap_ns
version = config_obj.version
    
# Extract the XML from the HTTP POST
form = cgi.FieldStorage()
uid = form.getvalue('uid')
password = form.getvalue('password')
xml_string = form.getvalue('xml').replace('>\n',">")

# authenticate submission
authentic = pam.authenticate(uid,password)

# if it authenticates, validate it against the CAP schema
if (authentic):
    try:
        # clean up the XML format a bit
        xml_string = re.sub("> +<", "><", xml_string)
        xml_string = xml.dom.minidom.parseString(xml_string).toprettyxml()
        # now parse into etree and validate
        xml_tree = etree.fromstring( xml_string )
        with open(config_obj.cap_schema,"r") as schema_file:
            schema_string = schema_file.read()    
        xml_schema = etree.XMLSchema( etree.fromstring( schema_string ) )
        valid = xml_schema.validate( xml_tree )
        log = xml_schema.error_log
        error = str( log.last_error )
    except:
        valid = False
        log = ""
        error = "Validation Error"  
# otherwise skip validation
else:
    valid = False
    error = "Authentication Failure"

# and either way, assign a the message a UUID and report the result to the client
msg_id = str( uuid.uuid4() ) 
print "Content-type: text/plain;charset=utf-8"
print 
print '{ "authenticated": ' + str( authentic ).lower() + ',"valid": ' + str( valid ).lower() + ',"error": "' + error + '", "uuid": "' + msg_id + '" }'  
    # force lowercase above to conform with JSON usage for boolean
 
# and now... if valid and authenticated
if (valid and authentic): 
    
    # assign <identifier> and <sender> values
    find_identifier = etree.XPath( "//p:identifier", namespaces={ 'p': cap_ns } )
    identifier = find_identifier( xml_tree )[0]
    identifier.text = msg_id
    find_sender = etree.XPath( "//p:sender", namespaces={ 'p': cap_ns } )
    sender = find_sender( xml_tree )[0]
    sender.text = uid + "@" + sender_domain
      
    # sign the XML tree
    signer = Signer(config_obj, uid);
    xml_tree = signer.signCAP( xml_tree )
    
    # re-serialize as string
    signed_xml_string = etree.tostring( xml_tree, pretty_print=False )
       
    # store CAP XML string
    filer = Filer(config_obj)
    filer.fileCAP( msg_id, signed_xml_string )
    
    # regenerate the ATOM index
    filer.reindex()
    
    # and forward as appropriate
    Forwarder.forwardCAP( path_to_data, msg_id )
    
