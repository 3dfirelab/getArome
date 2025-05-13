import xarray as xr
import datetime 
import glob
import sys 
import pdb 


'''
load arome 
'''

def load_wind(dir_data, date_obj, forecastTime):

    day_= date_obj.strftime("%Y%m%d")
    dir_data = '{:s}/{:s}/{:02d}Z/'.format(dir_data, day_, forecastTime)

    # File path to your AROME GRIB data
    grib_files = sorted(glob.glob(dir_data+"{:s}.{:02d}Z.*H.SP1.grib2".format(day_,forecastTime)))

    ds10 = None
    for grib_file in grib_files:
        # Open only the surface data
        ds10_ = xr.open_dataset(
                                    grib_file,
                                    engine="cfgrib",
                                    decode_timedelta=True,
                                    backend_kwargs={
                                        "filter_by_keys": {"shortName":["10u","10v"]}
                                    }
                                )

        if ds10 is None:
            ds10 = ds10_
        else:
            ds10 = xr.concat([ds10,ds10_],dim="step")


    return ds10

dir_data = '/mnt/data3/SILEX/AROME/'
date_obj = datetime.datetime(2025, 4, 13)
forecastTime = 21

ds = load_wind(dir_data, date_obj, forecastTime)

sys.exit()

ds2 = xr.open_dataset(
    grib_file,
    engine="cfgrib",
    backend_kwargs={
        "filter_by_keys": {"shortName":["2t","2r"]}
    }
)    

grib_file = dir_data+"20250413.21Z.20H.SP2.grib2"

# Open only the surface data
dsp = xr.open_dataset(
    grib_file,
    engine="cfgrib",
    backend_kwargs={
        "filter_by_keys": {"shortName":["tirf"]}
    }
)    


print(dsp)
