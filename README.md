# TO Get Arome from the Meteo France API.

`download_arome.py` download the SP1 and SP2 packages data from the open source AROME forecast (see [here](https://meteo.data.gouv.fr/datasets/65bd1247a6238f16e864fa80)) using the [Meteo France API](https://donneespubliques.meteofrance.fr/?fond=produit&id_produit=131&id_rubrique=51).

You need to define in your bash environment:
```
export APPLICATION_ID_METEOFRANCE=XXX
```
The data directory where the SP1 and SP2 files are stored is defined in `run_download_arome.sh`, see:
```
export dataDir=/mnt/data3/SILEX/AROME/
```

At `2025-05-14_18h00` the output looks like:
```
$dirData
└── FORECAST
    ├── 20250414
    │   ├── 00Z
    |   ...
    |   └── 12Z
    │       ├── 20250514.12Z.00H.SP1.grib2
    │       ├── 20250514.12Z.00H.SP2.grib2
    |       ...
    │       ├── 20250514.12Z.51H.SP1.grib2
    │       └── 20250514.12Z.51H.SP2.grib2
    └── log
        ├── aromeDownload.log
        └── cron.log
```
Where every 3h we have the hourly forecast for the next 51h.
The delay to get the last forecast is about 6h.
