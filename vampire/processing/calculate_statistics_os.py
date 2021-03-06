
import rasterio
import rasterstats
import numpy as np
import json
import csv
import os

def calc_average(file_list, avg_file):
    """ Calculate pixel-by-pixel average of list of rasters and save result as new raster. 
    
    For each pixel, calculate the mean of values in the list of rasters. 
    
    Parameters
    ----------
    file_list : list
        List of raster filenames
    avg_file : str
        Filename of output file
    
    Returns
    -------
    None
        Returns None
    
    """
    #    print "calcAverage: ", file_list
    if file_list:
        arrayList = []
        first = True
        profile = None
        for f in file_list:
            with rasterio.open(f) as cur_r:
                if first:
                    profile = cur_r.profile.copy()
                    first = False
                cur_a = cur_r.read(1, masked=True)
                arrayList.append(cur_a)
        dst_a = np.ma.dstack(arrayList)
        dst_r = dst_a.mean(axis=2, dtype=rasterio.float32)
        dst_r = dst_r.filled(-9999)
        profile.update(dtype=rasterio.float32, nodata=-9999)
        with rasterio.open(avg_file, 'w', **profile) as dst:
            dst.write(dst_r.astype(rasterio.float32), 1)
    return None

def calc_min(file_list, min_file):
    """ Calculate pixel-by-pixel minimum of list of rasters and save result as new raster. 

    For each pixel, calculate the minimum of values in the list of rasters. 

    Parameters
    ----------
    file_list : list
        List of raster filenames
    min_file : str
        Filename of output file

    Returns
    -------
    None
        Returns None
    """
    print "calcMin (open source version): ", file_list
    if file_list:
        arrayList = []
        first = True
        profile = None
        for f in file_list:
            with rasterio.open(f) as cur_r:
                if first:
                    profile = cur_r.profile.copy()
                    first = False
                cur_a = cur_r.read(1, masked=True)
                arrayList.append(cur_a)
        dst_a = np.ma.dstack(arrayList)
        dst_r = np.ma.min(dst_a, axis=2)
        with rasterio.open(min_file, 'w', **profile) as dst:
            dst.write(dst_r.astype(profile.dtype), 1)
            print "saved minimum in: ", min_file
    return None

def calc_max(file_list, max_file):
    """ Calculate pixel-by-pixel maximum of list of rasters and save result as new raster. 
    
    For each pixel, calculate the maximum of values in the list of rasters. 
    
    Parameters
    ----------
    file_list : list
        List of raster filenames
    max_file : str
        Filename of output file
    
    Returns
    -------
    None
        Returns None
    """
    if file_list:
        arrayList = []
        first = True
        profile = None
        for f in file_list:
            with rasterio.open(f) as cur_r:
                if first:
                    profile = cur_r.profile.copy()
                    first = False
                cur_a = cur_r.read(1, masked=True)
                arrayList.append(cur_a)
        dst_a = np.ma.dstack(arrayList)
        dst_r = np.ma.max(dst_a, axis=2)
        with rasterio.open(max_file, 'w', **profile) as dst:
            dst.write(dst_r.astype(profile.dtype), 1)
#            print "saved maximum in: ", max_file
    return None

def calc_std_dev(file_list, sd_file):
    """ Calculate pixel-by-pixel standard deviation of list of rasters and save result as new raster. 
    
    For each pixel, calculate the standard deviation of values in the list of rasters. 
    
    Parameters
    ----------
    file_list : list
        List of raster filenames
    sd_file : str
        Filename of output file
    
    Returns
    -------
    None
        Returns None
    """
    #    print "calcStDev (open source version): ", file_list
    if file_list:
        arrayList = []
        first = True
        profile = None
        for f in file_list:
            with rasterio.open(f) as cur_r:
                if first:
                    profile = cur_r.profile.copy()
                    first = False
                cur_a = cur_r.read(1, masked=True)
                arrayList.append(cur_a)
        dst_a = np.ma.dstack(arrayList)
        dst_r = np.ma.std(dst_a, axis=2, ddof=1)
        profile.update(dtype=rasterio.float32)
        with rasterio.open(sd_file, 'w', **profile) as dst:
            dst.write(dst_r.astype(rasterio.float32), 1)
#            print "saved standard deviation in: ", sd_file
    return None

def calc_sum(file_list, sum_file):
    """ Calculate pixel-by-pixel sum of list of rasters and save result as new raster. 

    For each pixel, calculate the sum of values in the list of rasters. 

    Parameters
    ----------
    file_list : list
        List of raster filenames
    sum_file : str
        Filename of output file

    Returns
    -------
    None
        Returns None
    """
    print "calcSum (open source version): ", file_list
    if file_list:
        arrayList = []
        first = True
        profile = None
        for f in file_list:
            with rasterio.open(f) as cur_r:
                if first:
                    profile = cur_r.profile.copy()
                    first = False
                cur_a = cur_r.read(1, masked=True)
                arrayList.append(cur_a)
        dst_a = np.dstack(arrayList)
        dst_r = np.sum(dst_a, axis=2)
        with rasterio.open(sum_file, 'w', **profile) as dst:
            dst.write(dst_r.astype(rasterio.float32), 1)
            print "saved sum in: ", sum_file
    return None

def calc_average_of_day_night(day_file, night_file, avg_file):
    """ Calculate pixel-by-pixel average of land surface temperature day and night rasters and save result as new raster. 

    For each pixel, calculate the mean of values in the two rasters. 
    
    Parameters
    ----------
    day_file : str
        Filename of day file
    night_file : str
        Filename of night file
    avg_file : str
        Filename of output file

    Returns
    -------
    None
        Returns None

    """
    print "calcAverage: ", day_file, night_file
    with rasterio.open(day_file) as day_r:
        profile = day_r.profile.copy()
#        profile.update(dtype=rasterio.uint32)
        day_a = day_r.read(1, masked=True)
        with rasterio.open(night_file) as night_r:
            night_a = night_r.read(1, masked=True)
            dst_r = np.ma.array((day_a, night_a)).mean(axis=0, dtype=rasterio.float32)
            dst_r = dst_r.filled(-9999)
            profile.update(dtype=rasterio.float32, nodata=-9999)
            with rasterio.open(avg_file, 'w', **profile) as dst:
                dst.write(dst_r.astype(rasterio.float32), 1)
    return None

def calc_zonal_statistics(raster_file, polygon_file, zone_field, output_table):
    """ Calculate zonal statistics for a raster and vector and save result as .csv file. 

    For each polygon in the vector file, calculate set of statistics from the raster (sum, mean, max, min, count). 

    Parameters
    ----------
    raster_file : str
        Filename of raster file
    polygon_file : str
        Filename of vector file
    zone_field : str
        Name of field labelling the zones within vector file
    output_table : str
        Filename of output table (.csv)

    Returns
    -------
    None
        Returns None

    """
    stats = rasterstats.zonal_stats(polygon_file, raster_file, stats=['min', 'max', 'mean', 'count', 'sum'],
                                    geojson_out=True)
    # export to .csv
    _stats_list = []
    _header_row = []
    for i in stats[0]['properties']:
        _header_row.append(i)
    for i in stats:
        row = []
        for p in i['properties']:
            row.append(i['properties'][p])
        _stats_list.append(row)
    _output_csv = os.path.join(os.path.dirname(output_table), output_table)
    with open(_output_csv, 'wb') as cf:
        wr = csv.writer(cf)
        wr.writerow(_header_row)
        wr.writerows(_stats_list)

    return stats