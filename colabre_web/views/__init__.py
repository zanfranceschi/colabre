"""
from auth import *
from home import *
from jobs import *
from my_jobs import *
from my_profile import *
from my_resume import *
from registration import *
from resumes import *
"""
"""
google_maps_api = "http://maps.googleapis.com/maps/api/geocode/json?address=%s&sensor=false" % "Rua Radiante, 13 - SP - Brasil"
import urllib2
response = urllib2.urlopen(google_maps_api)
r = response.read()
import json
j = json.loads(r)
"""