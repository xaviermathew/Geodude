import os
from tqdm import tqdm

tqdm.pandas()
os.environ['GDAL_ENABLE_DEPRECATED_DRIVER_GTM'] = 'YES'
