#     post_cap.py -- python CGI for posting CAP XML (as POST) to CAPCollector
#     version 0.9 - 6 August 2013
#     
#     Copyright (c) 2013, Carnegie Mellon University
#     All rights reserved.
# 
#     See LICENSE.txt for license terms (Modified BSD) 
#     
#    REQUIRED PYTHON PACKAGES IN ENVIRONMENT:  pytz, ISO8601, lxml
 
import cgi
from config import Config
from cap_support import Authenticator, Signer, Filer, Forwarder
from lxml import etree
import sys
import uuid

# load configuration variables
config = Config();
sender_domain = config.sender_domain
path_to_data = config.path_to_data 
web_path_to_data = config.web_path_to_data
expired_file_path = config.expired_file_path
cap_ns = config.cap_ns
version = config.version
    
# Extract the XML from the HTTP POST
form = cgi.FieldStorage()
uid = form.getvalue('uid')
password = form.getvalue('password')
xml_string = form.getvalue('xml')

# authenticate submission
authentic = Authenticator.isAuthentic( uid,password )

# if it authenticates, validate as well
if (authentic):
    # parse CAP
    try:
        xml_tree = etree.fromstring( xml_string )
        # and validate against the XML Schema
        with open("cap1.2.xsd","r") as schema_file:
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

# and either way, assign a the message a UUID and report the result
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
  
    # re-serialize
    releasable_xml_string = etree.tostring( xml_tree, pretty_print=True )
    
    # sign the XML
    signed_xml_string = Signer.signCAP( uid, releasable_xml_string )
    
    # store CAP XML
    filer = Filer(path_to_data, web_path_to_data, expired_file_path, version)
    filer.fileCAP( msg_id, signed_xml_string )
    
    # regenerate the ATOM index
    filer.reindex()
    
    # and forward as appropriate
    Forwarder.forwardCAP( path_to_data, msg_id )
    
