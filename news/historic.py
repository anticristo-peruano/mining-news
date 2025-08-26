import pandas as pd
import os
import io
import requests
import zipfile
from datetime import date, timedelta
from tqdm import tqdm

from .config import LINK, COLUMNS

class gdelt_archive:
    def __init__(self,year,export_path,code=None):
        self.y = year
        self.export = os.path.join(export_path,f'{year}.csv')
        self.code = code
        os.makedirs(export_path,exist_ok=True)

        for filenames in tqdm(list(self.parse_date())):
            self.fetch_zipped_csv(LINK + filenames)
        if self.code:
            self.select_country()
    
    def parse_date(self):
        '''Rules:
            - <= 2005       YYYY.zip
            - 2006-2012     YYYYMM.zip
            - 2013          YYYYMM.zip para ene-mar; luego diarios
            - >= 2014       YYYYMMDD.export.CSV.zip
        '''
        if self.y <= 2005:
            yield f'{self.y}.zip'

        elif self.y < 2013:
            for m in range(1, 13):
                yield f'{self.y}{m:02d}.zip'

        elif self.y > 2013:
            d = date(self.y, 1, 1)
            while d < date(self.y + 1, 1, 1):
                yield f'{d.strftime("%Y%m%d")}.export.CSV.zip'
                d += timedelta(days=1)

        else: # For the weird cut in 2013
            for m in range(1, 4):
                yield f'{self.y}{m:02d}.zip'

            d = date(self.y, 4, 1)
            while d < date(self.y + 1, 1, 1):
                yield f'{d.strftime("%Y%m%d")}.export.CSV.zip'
                d += timedelta(days=1)

    def fetch_zipped_csv(self,url:str):
        resp = requests.get(url,stream=True)
        if resp.ok:
            zip = zipfile.ZipFile(io.BytesIO(resp.content))

            with zip.open(zip.namelist()[0]) as f:
                pd.read_csv(
                    f, 
                    sep = '\t', 
                    header = None
                ).to_csv(
                    self.export,
                    mode = 'a', 
                    header = not os.path.exists(self.export),
                    columns = COLUMNS,
                    index=False
                )

    def select_country(self):
        df = pd.read_csv(self.export)
        df = df[(df['ACTOR1COUNTRYCODE']==self.code) | (df['ACTOR2COUNTRYCODE']==self.code)]
        
        if df.shape[0] != 0:
            df.to_csv(self.export,index=False)
        else:
            print('Wrong code. No selection performed (df.shape[0] = 0).')
