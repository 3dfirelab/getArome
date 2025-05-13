import json
import sys
import os 
import requests
import time
import pdb 
from datetime import datetime, timedelta
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from pathlib import Path
import glob

# Example of a Python implementation for a continuous authentication client.
# It's necessary to :
# - update APPLICATION_ID
# - update request_url at the end of the script

# unique application id : you can find this in the curl's command to generate jwt token 
APPLICATION_ID = os.environ['APPLICATION_ID_METEOFRANCE']

# url to obtain acces token
TOKEN_URL = "https://portail-api.meteofrance.fr/token"



#############################
class Client(object):

    def __init__(self):
        self.session = requests.Session()


    def request(self, method, url, **kwargs):
        # First request will always need to obtain a token first
        if 'Authorization' not in self.session.headers:
            self.obtain_token()



        # Optimistically attempt to dispatch reqest
        response = self.session.request(method, url, **kwargs)
        if self.token_has_expired(response):
            # We got an 'Access token expired' response => refresh token
            self.obtain_token()
            # Re-dispatch the request that previously failed
            response = self.session.request(method, url, **kwargs)

        return response



    def token_has_expired(self, response):
        status = response.status_code
        content_type = response.headers['Content-Type']
        if status == 401 and 'application/json' in content_type:
            repJson = response.text
            if 'Invalid JWT token' in repJson['description']:
                return True

        return False



    def obtain_token(self):
        # Obtain new token
        data = {'grant_type': 'client_credentials'}
        headers = {'Authorization': 'Basic ' + APPLICATION_ID}
        access_token_response = requests.post(TOKEN_URL, data=data, verify=False, allow_redirects=False, headers=headers)
        token = access_token_response.json()['access_token']
        # Update session with fresh token
        self.session.headers.update({'Authorization': 'Bearer %s' % token})


#############################
def get_two_level_dirs(base_path):
    base = Path(base_path)
    out = sorted([
        p for p in base.rglob("*")
        if p.is_dir()
        and len(p.relative_to(base).parts) == 2
        and not (len(p.relative_to(base).parts) == 1 and p.name == "log")
    ])
    return out

#############################
if __name__ == '__main__':
#############################
    
    dirData = sys.argv[1] #'/mnt/data3/SILEX/AROME/FORECAST/'

    client = Client()
    # Issue a series of API requests an example.  
    # For use this test, you must first subscribe to the arome api with your application
    client.session.headers.update({'Accept': 'application/json'})

    dirData = '{:s}/FORECAST/'.format(dirData)
    #get next forcast to download
    existingdir_sorted = get_two_level_dirs(dirData)
    forecastTime = None
    if len(existingdir_sorted)> 0: 
        last_forecastTime = datetime.strptime('T'.join(str(existingdir_sorted[-1]).split('/')[-2:]), '%Y%m%dT%HZ')
        dirout_ = '{:s}/{:s}/'.format(dirData,last_forecastTime.strftime('%Y%m%d/%HZ'))
        if len(glob.glob(dirout_+'*.grib2')) == 104:
            forecastTime = last_forecastTime + timedelta(hours=3)
        else: 
            forecastTime = last_forecastTime 

        if (datetime.now()-forecastTime).days: 
            forecastTime = None

    if forecastTime is None : 
        #if first call
        closest_past_3h = datetime.now().replace(minute=0, second=0, microsecond=0)
        hours_since_midnight = closest_past_3h.hour
        closest_3h_hour = (hours_since_midnight // 3) * 3
        forecastTime = closest_past_3h.replace(hour=closest_3h_hour) - timedelta(hours=6)  
    print('forecast = ',forecastTime)
   

    forecastTime_str = forecastTime.strftime('%Y-%m-%dT%H{:s}%M{:s}%SZ').format('%3A','%3A')
    url_check_availibility = 'https://public-api.meteofrance.fr/previnum/DPPaquetAROME/v1/models/AROME/grids/0.01/packages/SP1?referencetime={:s}'.format(forecastTime_str)

    response = client.request('GET', url_check_availibility, verify=True)
    if (response.status_code != 200):
        print(response.content)
    elif os.path.isfile(dirData+'lock.txt'):
        print('already running')
    else: 
        print('downloading...')
        with open(dirData+'lock.txt', "w") as file:
            pass  # This just opens and closes the file without writing anything

        dirout = '{:s}/{:s}/'.format(dirData,forecastTime.strftime('%Y%m%d/%HZ'))
        os.makedirs(dirout,exist_ok=True)

        json_str = response.content.decode('utf-8')
        # Parse the JSON string into a Python dict
        data = json.loads(json_str)
        
        for data_ in data['links'][1:]:
       
            timestep = int(data_['title'].split('H du r')[0].split('ance')[1].strip())
            
            for package in ['SP1','SP2']:
                
                fileout = '{:s}{:s}.{:02d}H.{:s}.grib2'.format(dirout,forecastTime.strftime('%Y%m%d.%HZ'),timestep,package)
                if os.path.isfile(fileout): continue

                url_paquet = 'https://public-api.meteofrance.fr/previnum/DPPaquetAROME/v1/models/AROME/grids/0.01/packages/{:s}/productARO?referencetime={:s}&time={:02d}H&format=grib2'.format(package,forecastTime_str,timestep)

                try: 
                    response = client.request('GET', url_paquet, verify=True)
                except: 
                    sys.exit(3)
                if response.status_code == 200: 
                    print('{:s}.{:02d}H.{:s}.grib2'.format(forecastTime.strftime('%Y%m%dT.%HZ'),timestep,package))
                    with open('{:s}{:s}.{:02d}H.{:s}.grib2'.format(
                        dirout,forecastTime.strftime('%Y%m%d.%HZ'),timestep,package), 'wb') as f:
                        f.write(response.content)

        os.remove(dirData+'lock.txt')
        print('done')

        
        if len(glob.glob(dirout+'*.grib2')) == 104: # all files are there. send 2 at exit to start fwi calculation
            with open(dirData+'../FWI/timeToCompute.txt', "w") as file:
                file.write(forecastTime.strftime('%Y%m%dT.%H%MZ'))
            sys.exit(0)
        else:
            sys.exit(1)


    sys.exit(2)
