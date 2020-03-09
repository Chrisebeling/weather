import pandas as pd
import datetime as dt
import numpy as np
import progressbar
import os
import sys
import pkg_resources

# ROOT_PATH = r'C:\Users\kirst\Documents\Chris\Programming\Projects\weather'
try:
    from weather.functions.config import get_path
    DATA_PATH = get_path()
    
except:
    print('Could not define DATA_PATH, please specify manually.')
    DATA_PATH=None

try:
    CITIES_PATH = pkg_resources.resource_filename(
                __name__,
                os.path.join(os.pardir, 'resources', 'world_cities.csv')
            )
except:
    print('Could not define CITIES_PATH, please specify manually.')
    CITIES_PATH=None

def get_stations(df, latlong=None, err=0.1, lat=None, long=None, fixed_err=False, min_count=3):
    '''Returns ID of stations matching the given latitude and longitude.
    Error widens until min count of stations is reached.
    
    Keyword Arguments
    df - The df of station data
    latlong - A tuple or list of the desired latitude and longitude (Default None)
    err - The margin of error for both lat and long to search within (Default 0.1)
    lat, long - If latlong not specified as pair, latlong can be given individually. Only one required. (Default None)
    fixed_err - If true, will not widen search (Default False)
    min_count - The minimum number of stations to stop search (Default 3)
    '''
    # if latlong given, take defin lat and longs, else check at least one lat or long is given
    if latlong:
        assert type(latlong) == list or type(latlong) == tuple, 'latlong must be list or tuple'
        assert len(latlong) == 2, 'latlong must contain 2 items. Contains {}'.format(len(latlong))
        lat = latlong[0]
        long = latlong[1]
    else:
        assert not (lat == None and long == None), 'One of lat, long or latlong must be given.'
        
    assert lat == None or type(lat) == float, 'lat must be float, not {}'.format(type(lat))
    assert long == None or type(long) == float, 'lat must be float, not {}'.format(type(long))
    
    # define default filters as all
    lat_select, long_select = True, True
    
    # increase error tolerance each iteration
    for new_err in (np.arange(1,31) * err):
        # If each is defined, reduce lat and/or long filter to lines meeting criteria
        if lat:
            lat_select = (df['LATITUDE'] >= lat - new_err) & (df['LATITUDE'] <= lat + new_err)
        if long:
            long_select = (df['LONGITUDE'] >= long - new_err) & (df['LONGITUDE'] <= long + new_err)
        
        # combine the lat and long filters, return stations meeting filter
        select = lat_select & long_select
        subset = df[select]
        
        # return results if enough stations found, continue iteration otherwise
        if len(subset) >= min_count or fixed_err:
            print('Stations found: {}, Average lat err: {:.2f}, Average long err: {:.2f}'.format(len(subset),
                                                                                                 subset['LATITUDE'].mean() - lat,
                                                                                                subset['LONGITUDE'].mean() - long))
            return list(subset['ID'])
    
    # if max iterations reached, return the stations found
    print('Stations found: {}, Average lat err: {:.2f}, Average long err: {:.2f}'.format(len(subset),
                                                                                         subset['LATITUDE'].mean() - lat,
                                                                                        subset['LONGITUDE'].mean() - long))
    return list(subset['ID'])

def decode_line(line_str, decoding=None, data_step=8, data_length=5):
    '''Each line of the data contains one month worth of data for one element (i.e. TMAX, TMIN, PRCP)
    Takes the line and returns a df with three columns: ELEMENT, VALUE, DATE
    '''
    if decoding == None:
        decoding = {'ID':(0,11),
                   'YEAR':(11,15),
                   'MONTH':(15,17),
                   'ELEMENT':(17,21),
                   'STR_DATA':(21,269)}
    
    # check that length of string matches decoding dict
    exp_len = max([decoding[key][1] for key in decoding.keys()]) + 1
    assert exp_len == len(line_str), 'Str must be {} chars long, not {}'.format(exp_len, len(line_str))
    
    # unpack str into keys
    line_data = {}
    for key in decoding.keys():
        slicer = decoding[key]
        line_data[key] = line_str[slicer[0]:slicer[1]]

    # further separate the data str into the values for each day
    # value -9999 represents empty day, ie 31st of a month with 30 days
    month_data = [int(line_data['STR_DATA'][data_step*n:data_step*(n+1) - (data_step-data_length)]) for n in range(int(len(line_data['STR_DATA']) / data_step))]
    month_data = [x for x in month_data if x != -9999]
    line_data['DATA'] = month_data
    # create dates, year and month given in string, day inferredas data is in ascending order 
    line_data['DATE'] = [dt.date(int(line_data['YEAR']), int(line_data['MONTH']), day+1) for day in np.arange(len(line_data['DATA']))]

    line_df = pd.DataFrame({'ELEMENT':[line_data['ELEMENT']] * len(line_data['DATA']),
                             'VALUE':line_data['DATA'],
                            'DATE':line_data['DATE']})
    
    return line_df

def get_locdata(station_ids, data_path=DATA_PATH, location=None, full_data=False):
    '''Given location and station ids, return weather data.
    If full_data flag True, will return a df containing data from every station.
    If full_data flag False, will return a df with max aggregation for TMAX, min for TMIN and mean for all other elements.
    
    Keyword arguments:
    station_ids - Can be dict or list. If list, it is a list of the station ids desired. If dict, is a dict of lists, with locations as keys.
    data_path - The path where the weather data files are located.
    location - If station_ids is a dict, the location key to use (Default None)
    full_data - If True, return all aggregation dfs (default False)
    '''
    loc_data = {}
    station_list = []
    
    # define the stations ids to get data for
    if type(station_ids) == list:
        s_ids = station_ids
    elif type(station_ids) == dict:
        assert location != None, 'station_ids is dict, location must be given.'
        s_ids = station_ids[location]
    else:
        raise('stations_ids must be list or dict, not {}'.format(type(station_ids)))
    
    sys.stdout.flush()
    for station_id in progressbar.progressbar(s_ids):
        filename = os.path.join(data_path, 'ghcnd_all', station_id+'.dly')
        
        try:
            with open(filename, 'r') as f:
                lines = f.readlines()
        except IOError as e:
            if e.errno == 2:
                print('Skipping file. Could not find: {}'.format(filename),	end='\n')
                continue
            else:
                raise
        
        # iterate through lines, converting from string to df
        for line in lines:
            line_df = decode_line(line)
            line_df.loc[:,'STATION_ID'] = station_id
            station_list.append(line_df)

    loc_df = pd.concat(station_list)
    
    # aggregate data across all stations
    value_gb = loc_df.groupby(['ELEMENT','DATE']).VALUE
    desired_funcs = ['max','min','mean']
    for func in desired_funcs:
        loc_data[func] = loc_df.groupby(['ELEMENT','DATE']).VALUE.agg(func).unstack(0)
    
    # create single df of all weather data for the location
    mean_columns = [header for header in set(loc_df.loc[:,'ELEMENT']) if header not in ['TMAX', 'TMIN']]
    main_df = loc_data['mean'].loc[:,mean_columns].copy()
    main_df = main_df.merge(loc_data['max'].loc[:,'TMAX'], how='outer', left_index=True, right_index=True)
    main_df = main_df.merge(loc_data['min'].loc[:,'TMIN'], how='outer', left_index=True, right_index=True)
    loc_data['main'] = main_df
    
    if full_data:
        return loc_df
    else:
        return main_df

def get_weatherdata(desired_cities, short_label=True, return_full=False, _min_count=3, data_path=DATA_PATH, cities_path=CITIES_PATH, additional={}, return_stations=False):
    '''Master function returns df of weather data for cities given. 
    For cities given, takes location data from cities csv in data path.
    Additional locations can be specified, given in the form of longlat tuple.
    
    Keyword arguments:
    desired_cities - A list of cities. Give in the form "city,country". 
                    Will perform a string match so city only or country can be given. 
                    Will return multiple results if matched.
    short_label - If true, dict keys will only return the city name (default True)
    return_full - If true, will return the df containing data from all matching stations.
                    If false, will return a df with max of TMAX, min of TMIN, average of other elements for each date (default False)
    _min_count - The min count of stations required (default 3)
    data_path - The directory of the required files. Default specified in py file as global (default DATA_PATH)
    additional - A dict of additional locations to return data for.
                Keys are location name, Items are tuples of long and lat. (default empty dict)
    '''
    desired_cities = [x.upper() for x in desired_cities]
    # import csvs containing high level info required to access data
    stations = pd.read_csv(os.path.join(data_path, 'ghcnd-stations.csv'), header=0)
    cities = pd.read_csv(cities_path)
    
    # create tuple of (lat,long), create location in form city,country
    cities.loc[:,'latlong'] = cities.apply(lambda row: (row['lat'], row['lng']), axis=1)
    cities.loc[:,'location'] = cities.apply(lambda row: ','.join([row['city_ascii'], row['country']]).upper(), axis=1)
    
    # find all locations matching desired cities
    sub_df = cities[cities.location.str.contains('|'.join(desired_cities))].set_index('location',drop=True)[['latlong']]
    if len(sub_df) != len(desired_cities):
        print('Returning {} locations: {}'.format(len(sub_df), list(sub_df.index)))
    
    # iterate through locations
    # first find station ids matching latlong, then process data file and store in dict
    weather_data, stations_found = {}, {}
    for idx, row in sub_df.iterrows():
        label = idx.split(',')[0] if short_label else idx
        print(label)
        desired_stations = get_stations(stations, row[0], 0.1, min_count=_min_count)
        loc_data = get_locdata(desired_stations, data_path, return_full)

        weather_data[label] = loc_data
        stations_found[label] = desired_stations
    
    # the same as above, but iterate through additional dict
    # if not additional given, will not iterate through anything
    for location in additional.keys():
        print(location)
        desired_stations = get_stations(stations, additional[location], 0.1, min_count=_min_count)
        loc_data = get_locdata(desired_stations, data_path, return_full)
        
        weather_data[label] = loc_data
        stations_found[label] = desired_stations

    if return_stations:
        return weather_data, stations_found
    else:
        return weather_data