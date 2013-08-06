#     config.py -- configuration class for CAPCollector
#     version 0.9 - 6 August 2013
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
        
        self.web_path_to_data = "http://localhost/~acb/cap/data"
        
        self.path_to_data = "/var/www/incident.com/secure_html/map/data"
        
        self.expired_file_path = "/var/www/incident.com/secure_html/map/data"
        
        self.cap_ns = "urn:oasis:names:tc:emergency:cap:1.2"
        
        self.version = "CAPCollector v0.9"
    