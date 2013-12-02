#     config.py -- configuration class for CAPCollector
#     version 0.9.2 - 1 December 2013
#     
#     Copyright (c) 2013, Carnegie Mellon University
#     All rights reserved.
# 
#     See LICENSE.txt for license terms (Modified BSD) 
#     

# SET THESE FOR LOCAL CONFIGURATION
class Config():
    
    def __init__(self):
         
        self.sender_domain = "incident.com"
        
        self.web_path_to_data = "http://localhost/cap/data"
        
        self.path_to_data = "/Users/acb/git/CAPTools/CAPCreator/data"
        
        self.expired_file_path = "/Users/acb/git/CAPTools/CAPCreator/inactive"
        
        self.creds_file_path = "/Users/acb/git/CAPTools/CAPCreator/creds"
        
        self.cap_ns = "urn:oasis:names:tc:emergency:cap:1.2"
        
        self.version = "CAPCollector v0.9"
        
        self.cap_schema = "cap1.2.xsd"
    
        self.cap_ns = "urn:oasis:names:tc:emergency:cap:1.2"
        
        self.sig_ns = "http://www.w3.org/2000/09/xmldsig#"
