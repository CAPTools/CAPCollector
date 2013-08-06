#     post_cap.py -- python CGI for posting CAP XML (as POST) to CAPCollector
#     version 0.9 - 6 August 2013
#     
#     Copyright (c) 2013, Carnegie Mellon University
#     All rights reserved.
# 
#     See LICENSE.txt for license terms (Modified BSD) 
#     
 
import cgi
from cap_support import Authenticator, Signer, Filer, Forwarder
from lxml import etree
import sys
import uuid

sender_domain = "incident.com"
path_to_data = "/var/www/incident.com/secure_html/map/data"
web_path_to_data = "https://www.incident.com/map/data"
expired_file_path = "/var/www/incident.com/secure_html/map/data"
cap_ns = "urn:oasis:names:tc:emergency:cap:1.2"
    
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
    xml_tree = etree.fromstring( xml_string )
    # and validate against the XML Schema
    with open("cap1.2.xsd","r") as schema_file:
        schema_string = schema_file.read()    
    xml_schema = etree.XMLSchema( etree.fromstring( schema_string ) )
    valid = xml_schema.validate( xml_tree )
    log = xml_schema.error_log
    error = str( log.last_error )
    
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
    filer = Filer(path_to_data, web_path_to_data, expired_file_path)
    filer.fileCAP( msg_id, signed_xml_string )
    
    # regenerate the ATOM index
    filer.reindex()
    
    # and forward as appropriate
    Forwarder.forwardCAP( path_to_data, msg_id )
    
