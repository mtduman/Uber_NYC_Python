
# coding: utf-8

# In[1]:

import numpy as np
from mpl_toolkits.basemap import Basemap
import pandas as pd
import datetime as dt
from matplotlib import pyplot as plt
import urllib
from bokeh.plotting import *
from bokeh.models import HoverTool
from collections import OrderedDict
import numpy as np

def aggregate_uber_data(data_filenames):
    df = pd.read_csv(data_filenames, delimiter=';', parse_dates=[0])
    df = df.set_index(pd.DatetimeIndex(df['Date/Time']))
    df['Date'] = df['Date/Time'].apply(lambda x: dt.datetime.strftime(x,'%Y%m%d'))
    df['Hour'] = df['Date/Time'].apply(lambda x: dt.datetime.strftime(x,'%H'))
    df['DayName'] = df['Date/Time'].apply(lambda x: dt.datetime.strftime(x,'%a'))
    df['WeekEnd'] = df['DayName'].apply(lambda x: 'Yes' if x in 'Fri,Sat,Sun' else 'No')
    df['Lat2'] = df['Lat'].apply(lambda x: round(x,2))
    df['Lon2'] = df['Lon'].apply(lambda x: round(x,2))
    return(df)

def groupby_dayhour_uber_data(df):
    dfg_dh = pd.DataFrame({'Count' : df.groupby( ['Date','Hour']).size()}).reset_index()
    dfg_dh['Date'] = pd.to_datetime(dfg_dh['Date'])
    dfg_dh['MonthFirst'] = dfg_dh['Date'].apply(lambda x: dt.datetime.strftime(x,'%Y%m-%b'))
    dfg_dh['DayName'] = dfg_dh['Date'].apply(lambda x: dt.datetime.strftime(x,'%a'))
    dfg_dh['DayOfWeek'] = dfg_dh['Date'].apply(lambda x: dt.datetime.strftime(x,'%w'))
    dfg_dh['WeekEnd'] = dfg_dh['DayName'].apply(lambda x: 'Yes' if x in 'Fri,Sat,Sun' else 'No')
    dfg_dh['WeekFirst'] = [(date - dt.timedelta(days=date.dayofweek)).strftime("%Y-%m-%d") for date in dfg_dh["Date"]]
    return dfg_dh

def create_daytotal_plot(dfg_dh):
    dfq = pd.DataFrame({'CountDay' : dfg_dh.groupby( ["DayOfWeek", "DayName"] )['Count'].sum()}).reset_index()
    dfq.loc[dfq['DayOfWeek'] == '0', 'DayOfWeek'] = '7'
    dfq = dfq.set_index('DayOfWeek')
    dfq.sort_index(inplace=True)
    dfq.plot(x='DayName', y='CountDay', kind='bar', title ="Uber Daily Ride", 
             figsize=(8,4),legend=False, fontsize=7, label='Total')
    return

def create_day_hourtotal_plot(dfg_dh):
    dfh = pd.DataFrame({'CountDay' : dfg_dh.groupby( ["DayOfWeek", "DayName","Hour"] )['Count'].sum()}).reset_index()
    dfh.loc[dfh['DayOfWeek'] == '0', 'DayOfWeek'] = '7'
    dfh_pivot = pd.pivot_table(dfh, index='Hour', columns='DayOfWeek', values='CountDay', aggfunc='sum')    
    dfh_pivot.fillna(0, inplace=True)
    day_x = dfh_pivot.as_matrix(columns=dfh_pivot.columns)
    dfh_p = pd.DataFrame(day_x, index=list(dfh_pivot.index), columns=['Mon','Tue','Wen','Thu','Fri','Sat','Sun'])
    dfh_p.plot(title ="Uber Day Hourly Total Ride", 
             figsize=(10,4),legend=True, fontsize=8 )
    plt.legend(loc='upper left', fontsize = 'xx-small')
    return

def create_week_day_hourly_plot(dfg_dh):
    dfh = pd.DataFrame({'CountDay' : dfg_dh.groupby( ["DayOfWeek", "DayName","Hour"] )['Count'].sum()}).reset_index()
    dfh.loc[dfh['DayOfWeek'] == '0', 'DayOfWeek'] = '7'
    dfh_pivot = pd.pivot_table(dfh, index='Hour', columns='DayOfWeek', values='CountDay', aggfunc='sum')    
    dfh_pivot.fillna(0, inplace=True)
    day_x = dfh_pivot.as_matrix(columns=dfh_pivot.columns)
    dfh_p = pd.DataFrame(day_x, index=list(dfh_pivot.index), columns=['Mon','Tue','Wen','Thu','Fri','Sat','Sun'])
    dfh_p.plot(title ="Uber Hourly Ride", 
             figsize=(10,4),legend=True, fontsize=7 )
    return

def create_weekly_dailytotal_plot(dfg_dh):
    dfr = pd.DataFrame({'CountDay' : dfg_dh.groupby( ["WeekFirst", "DayName","Date"] )['Count'].sum()}).reset_index()
    dfr = dfr.set_index(pd.DatetimeIndex(dfr['WeekFirst']))
    dfr = dfr.set_index('WeekFirst')
#    dfr.to_csv('Uber_Daybyday_total.csv', sep=',')


    weeks = list(pd.unique(dfr.index))
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    colors = [  "#75968f", "#a5bab7", "#c9d9d3", "#e2e2e2", "#dfccce",
                "#ddb7b1", "#cc7878", "#933b41", "#550b1d"]
    day = []        
    week = []
    color = []
    count = []
    count_max = max(dfr['CountDay'])
    count_min = min(dfr['CountDay'])
    count_dif = (count_max - count_min)/7
    for row_index, row in dfr.iterrows():
        day.append(row['DayName'])
        week.append(row_index)
        count.append(row['CountDay'])
        color.append(colors[int(round((row['CountDay'] - count_min) / count_dif , 0)  )])

    source = ColumnDataSource(
        data=dict(day=day, week=week, color=color, count=count))

    output_file('UberGraph1.html')
    TOOLS = "resize,hover,save,pan,box_zoom,wheel_zoom"

    p = figure(title="Uber Weekly Day by Day Rides (2014 Apr-Sep)",
        x_range=weeks, y_range=list(reversed(days)),
        x_axis_location="above", plot_width=900, plot_height=400,
        toolbar_location="left", tools=TOOLS)

    p.rect("week", "day", 1, 1, source=source,
        color="color", line_color=None)

    p.grid.grid_line_color = None
    p.axis.axis_line_color = None
    p.axis.major_tick_line_color = None
    p.axis.major_label_text_font_size = "5pt"
    p.axis.major_label_standoff = 0
    p.xaxis.major_label_orientation = np.pi/3
    hover = p.select(dict(type=HoverTool))
    hover.tooltips = OrderedDict([
        ('row_index', '@day @week'),
        ('count', '@count'),])
    return p 

def create_wend_wday_plot(dfg_dh):
    dfW = pd.DataFrame({'Count_x' : dfg_dh.groupby( ["WeekFirst", "WeekEnd"] )['Count'].sum()}).reset_index()
    dfW.loc[dfW['WeekEnd'] == 'Yes', 'Fri_Sat_Sun'] = dfW['Count_x']
    dfW.loc[dfW['WeekEnd'] == 'No', 'Mon_Tue_Wed_Thu'] = dfW['Count_x']
    dfW_2= dfW.groupby(['WeekFirst'])['Fri_Sat_Sun','Mon_Tue_Wed_Thu'].sum()
    dfW_3 = dfW_2.applymap(abs)
    dfW_3.plot(title ="Uber Weekday/Weekend Ride", kind='bar', fontsize=7)
    return

def create_allweeks_daily_plot(dfg_dh):
    dfW = pd.DataFrame({'CountDay' : dfg_dh.groupby( ["WeekFirst", "DayOfWeek"] )['Count'].sum()}).reset_index()
    dfW.loc[dfW['DayOfWeek'] == '0', 'DayOfWeek'] = '7'
    dfW.loc[dfW['DayOfWeek'] == '1', 'Mon'] = dfW['CountDay']
    dfW.loc[dfW['DayOfWeek'] == '2', 'Tue'] = dfW['CountDay']
    dfW.loc[dfW['DayOfWeek'] == '3', 'Wed'] = dfW['CountDay']
    dfW.loc[dfW['DayOfWeek'] == '4', 'Thu'] = dfW['CountDay']
    dfW.loc[dfW['DayOfWeek'] == '5', 'Fri'] = dfW['CountDay']
    dfW.loc[dfW['DayOfWeek'] == '6', 'Sat'] = dfW['CountDay']
    dfW.loc[dfW['DayOfWeek'] == '7', 'Sun'] = dfW['CountDay']
    dfW_2= dfW.groupby(['WeekFirst'])['Mon','Tue','Wed','Thu','Fri','Sat','Sun'].sum()
    dfW_3 = dfW_2.applymap(abs)
    dfW_3.plot(title ='Uber Daily Detail Ride', kind='bar', fontsize=7)
    plt.legend(loc='upper left', fontsize = 'xx-small')
    return

def create_monthly_plot(dfg_dh):
    dfM = pd.DataFrame({'Ride_Total' : dfg_dh.groupby( ["MonthFirst"] )['Count'].sum()})
    dfM_2 = dfM.applymap(abs)
    dfM_2.plot(title ='Uber Ride', kind='bar', legend=False, fontsize=7)
    return

def create_daily_plot(dfg_dh):
    dfd = pd.DataFrame({'Ride_Total' : dfg_dh.groupby( ["Date"] )['Count'].sum()})
    dfd.plot(title ="Uber Daily Total Ride")
    return

def create_wend_wday_all_location_dataframe(df):
    dfp = pd.DataFrame({'CountLoc' : df.groupby( ['WeekEnd','Lat','Lon']).size()}).reset_index()
    dfp.sort_values(['WeekEnd', 'CountLoc'], ascending=[1, 0], inplace=True )
#    dfp.to_csv('Uber_WeekEndDay_All_loc.csv', sep=',')
    return dfp

def show_wend_wday_all_location(dfW):
    WendLon_x = []
    WendLat_y = []
    WdayLon_x = []
    WdayLat_y = []
    for row_index, row in dfW.iterrows():
        if row['WeekEnd'] == 'Yes' :
            WendLon_x.append(row['Lon'])   
            WendLat_y.append(row['Lat'])
        else:
            WdayLon_x.append(row['Lon'])   
            WdayLat_y.append(row['Lat'])

    fig = plt.figure(figsize=(8,6))
    themap = Basemap(projection='mill', lat_0=40.7, lon_0=-74,
              llcrnrlon = -75,              # lower-left corner longitude
              llcrnrlat = 40,               # lower-left corner latitude
              urcrnrlon = -72,               # upper-right corner longitude
              urcrnrlat = 41.5,               # upper-right corner latitude
              resolution = 'h',
              area_thresh = 5)
              
    themap.drawmapboundary(fill_color='white')
    themap.drawcoastlines(color='black', linewidth=.3)
    themap.drawcountries(color='black', linewidth=.3)
    themap.drawstates(color='black', linewidth=.3)    
    lons = [-73.7822222222, -74.175]
    lats = [40.6441666667, 40.6897222222]
    xp,yp = themap(lons, lats)
    themap.plot(xp, yp, 'yo', markersize=12)
    labels = ['JFK Airport,NY', 'Newark Airport,NJ']
    for label, xpt, ypt in zip(labels, xp, yp):
        plt.text(xpt, ypt, label)

    plt.title('Weekday Ride All Location') 
    x, y = themap(WdayLon_x, WdayLat_y)
    themap.plot(x, y,'o',color='r')

    fig = plt.figure(figsize=(8,6))
    themap = Basemap(projection='mill', lat_0=40.7, lon_0=-74,
              llcrnrlon = -75,              # lower-left corner longitude
              llcrnrlat = 40,               # lower-left corner latitude
              urcrnrlon = -72,               # upper-right corner longitude
              urcrnrlat = 41.5,               # upper-right corner latitude
              resolution = 'h',
              area_thresh = 5)
              
    themap.drawmapboundary(fill_color='white')
    themap.drawcoastlines(color='black', linewidth=.3)
    themap.drawcountries(color='black', linewidth=.3)
    themap.drawstates(color='black', linewidth=.3)    
    xp,yp = themap(lons, lats)
    themap.plot(xp, yp, 'yo', markersize=12)
    labels = ['JFK Airport,NY', 'Newark Airport,NJ']
    for label, xpt, ypt in zip(labels, xp, yp):
        plt.text(xpt, ypt, label)
    
    plt.title('Weekend Ride All Location') 
    x, y = themap(WendLon_x, WendLat_y)
    themap.plot(x, y,'o',color='r')
    return

def create_wend_wday_pop_location_dataframe(df,drop_perc=0.001):
    dfp = pd.DataFrame({'CountLoc' : df.groupby( ['WeekEnd','Lat2','Lon2']).size()}).reset_index()
    dfp['WTotal'] = dfp.groupby(['WeekEnd'])['CountLoc'].transform('sum')
    dfp['WPercent'] = dfp['CountLoc'] / dfp['WTotal']
    dfp = dfp.drop(dfp[dfp.WPercent < drop_perc].index)

    dfp['WX_Total'] = dfp.groupby(['WeekEnd'])['CountLoc'].transform('sum')
    dfp['WX_Percent'] = dfp['WX_Total'] / dfp['WTotal']                           # I am checking what percent of data left by WeekEnd-Yes-No group after I drop drop_perc 
    dfp.sort_values(['WeekEnd', 'CountLoc'], ascending=[1, 0], inplace=True )
#    dfp.to_csv('Uber_WeekEndDay_popular_loc.csv', sep=',')
#    p_min = round(100 * min(dfp['WX_Percent']))
#    p_max = round(100 * max(dfp['WX_Percent']))
#    print("Weekday-Weekend Selected location Percentage Min % :", p_min)     # I got %91 and %92
#    print("Weekday-Weekend Selected location Percentage Max % :", p_max)
    return dfp

def show_wend_wday_pop_location(dfW):
    WendLon_x = []
    WendLat_y = []
    WdayLon_x = []
    WdayLat_y = []
    for row_index, row in dfW.iterrows():
        if row['WeekEnd'] == 'Yes' :
            WendLon_x.append(row['Lon2'])   
            WendLat_y.append(row['Lat2'])
        else:
            WdayLon_x.append(row['Lon2'])   
            WdayLat_y.append(row['Lat2'])

    fig = plt.figure(figsize=(8,6))
    themap = Basemap(projection='mill', lat_0=40.7, lon_0=-74,
              llcrnrlon = -74.3,              # lower-left corner longitude
              llcrnrlat = 40.55,               # lower-left corner latitude
              urcrnrlon = -73.6,               # upper-right corner longitude
              urcrnrlat = 40.9,               # upper-right corner latitude
              resolution = 'h',
              area_thresh = 5)
              
    themap.drawmapboundary(fill_color='white')
    themap.drawcoastlines(color='black', linewidth=.3)
    themap.drawcountries(color='black', linewidth=.3)
    themap.drawstates(color='black', linewidth=.3)    
    lons = [-73.7822222222, -74.175]
    lats = [40.6441666667, 40.6897222222]
    xp,yp = themap(lons, lats)
    themap.plot(xp, yp, 'yo', markersize=12)
    labels = ['JFK Airport,NY', 'Newark Airport,NJ']
    for label, xpt, ypt in zip(labels, xp, yp):
        plt.text(xpt, ypt, label)

    plt.title('Weekday Ride Popular Location') 
    x, y = themap(WdayLon_x, WdayLat_y)
    themap.plot(x, y,'o',color='r')

    fig = plt.figure(figsize=(8,6))
    themap = Basemap(projection='mill', lat_0=40.7, lon_0=-74,
              llcrnrlon = -74.3,              # lower-left corner longitude
              llcrnrlat = 40.55,               # lower-left corner latitude
              urcrnrlon = -73.6,               # upper-right corner longitude
              urcrnrlat = 40.9,               # upper-right corner latitude
              resolution = 'h',
              area_thresh = 5)
              
    themap.drawmapboundary(fill_color='white')
    themap.drawcoastlines(color='black', linewidth=.3)
    themap.drawcountries(color='black', linewidth=.3)
    themap.drawstates(color='black', linewidth=.3)    
    xp,yp = themap(lons, lats)
    themap.plot(xp, yp, 'yo', markersize=12)
    labels = ['JFK Airport,NY', 'Newark Airport,NJ']
    for label, xpt, ypt in zip(labels, xp, yp):
        plt.text(xpt, ypt, label)
    
    plt.title('Weekend Ride Popular Location') 
    x, y = themap(WendLon_x, WendLat_y)
    themap.plot(x, y,'o',color='r')
    return

def create_wend_wday_pop_location_graph(dfW):
    WendLon_x = []
    WendLat_y = []
    WdayLon_x = []
    WdayLat_y = []
    for row_index, row in dfW.iterrows():
        if row['WeekEnd'] == 'Yes' :
            WendLon_x.append(row['Lon2'])   
            WendLat_y.append(row['Lat2'])
        else:
            WdayLon_x.append(row['Lon2'])   
            WdayLat_y.append(row['Lat2'])

    fig = plt.figure(figsize=(8,6))
    themap = Basemap(projection='mill', lat_0=40.7, lon_0=-74,
              llcrnrlon = -74.3,              # lower-left corner longitude
              llcrnrlat = 40.55,               # lower-left corner latitude
              urcrnrlon = -73.6,               # upper-right corner longitude
              urcrnrlat = 40.9,               # upper-right corner latitude
              resolution = 'f',
              area_thresh = 5)
    themap.drawmapboundary(fill_color='white')
    themap.fillcontinents(color='#F5DEB3',lake_color='#85A6D9') 
    themap.drawcoastlines(color='black', linewidth=.4)
    themap.drawcountries(color='#6D5F47', linewidth=.4)
    themap.drawstates(color='black', linewidth=.4)    
    themap.drawmeridians(np.arange(0, 360, 20),                                               
                labels=[0,0,0,1],                                                    
                color='black',                                                       
                dashes=[1,0],                                                        
                labelstyle='+/-',                                                    
                linewidth=0.2)         
    themap.drawparallels(np.arange(-90, 90, 10),                                              
                labels=[1,0,0,0],                                                    
                color='black',                                                       
                dashes=[1,0],                                                        
                labelstyle='+/-',                                                    
                linewidth=0.2) 
    nx, ny = 10, 3
    WdayLon_bins = np.linspace(min(WdayLon_x), max(WdayLon_x), nx+1)
    WdayLat_bins = np.linspace(min(WdayLat_y), max(WdayLat_y), ny+1)

    density, _, _ = np.histogram2d(WdayLat_y, WdayLon_x, [WdayLat_bins, WdayLon_bins])
    WdayLon_bins_2d, WdayLat_bins_2d = np.meshgrid(WdayLon_bins, WdayLat_bins)
    xs, ys = themap(WdayLon_bins_2d, WdayLat_bins_2d)
    plt.pcolormesh(xs, ys, density)
    plt.colorbar(orientation='horizontal')
    plt.scatter(*themap(WdayLon_x, WdayLat_y))
    plt.title('Weekday Ride Location') 

    fig = plt.figure(figsize=(8,6))
    themap = Basemap(projection='mill', lat_0=40.7, lon_0=-74,
              llcrnrlon = -74.3,              # lower-left corner longitude
              llcrnrlat = 40.55,               # lower-left corner latitude
              urcrnrlon = -73.6,               # upper-right corner longitude
              urcrnrlat = 40.9,               # upper-right corner latitude
              resolution = 'f',
              area_thresh = 5)
    themap.drawmapboundary(fill_color='white')
    themap.fillcontinents(color='#F5DEB3',lake_color='#85A6D9') 
    themap.drawcoastlines(color='black', linewidth=.4)
    themap.drawcountries(color='#6D5F47', linewidth=.4)
    themap.drawstates(color='black', linewidth=.4)    
    themap.drawmeridians(np.arange(0, 360, 20),                                               
                labels=[0,0,0,1],                                                    
                color='black',                                                       
                dashes=[1,0],                                                        
                labelstyle='+/-',                                                    
                linewidth=0.2)         
    themap.drawparallels(np.arange(-90, 90, 10),                                              
                labels=[1,0,0,0],                                                    
                color='black',                                                       
                dashes=[1,0],                                                        
                labelstyle='+/-',                                                    
                linewidth=0.2) 
    nx, ny = 10, 3
    WendLon_bins = np.linspace(min(WendLon_x), max(WendLon_x), nx+1)
    WendLat_bins = np.linspace(min(WendLat_y), max(WendLat_y), ny+1)
    density, _, _ = np.histogram2d(WendLat_y, WendLon_x, [WendLat_bins, WendLon_bins])
    WendLon_bins_2d, WendLat_bins_2d = np.meshgrid(WendLon_bins, WendLat_bins)
    xs, ys = themap(WendLon_bins_2d, WendLat_bins_2d)
    plt.pcolormesh(xs, ys, density)
    plt.colorbar(orientation='horizontal')
    plt.scatter(*themap(WendLon_x, WendLat_y))
    plt.title('Weekend Ride Location') 
    return

def create_wend_wday_pop_destination_graph(dfW):
    WendLon_x = []
    WendLat_y = []
    WdayLon_x = []
    WdayLat_y = []
    for row_index, row in dfW.iterrows():
        if row['WeekEnd'] == 'Yes' :
            WendLon_x.append(row['Lon2'])   
            WendLat_y.append(row['Lat2'])
        else:
            WdayLon_x.append(row['Lon2'])   
            WdayLat_y.append(row['Lat2'])
    
    fig = plt.figure(figsize=(8,6))
    plt.title('Uber Weekday Popular Destination')
    m = Basemap(projection='mill',  lat_0=40.7, lon_0=-74,
              llcrnrlon = -74.3,              # lower-left corner longitude
              llcrnrlat = 40.55,               # lower-left corner latitude
              urcrnrlon = -73.6,               # upper-right corner longitude
              urcrnrlat = 40.9,               # upper-right corner latitude
              resolution = 'h',
              area_thresh = 0.1)
    m.drawmapboundary()
    m.drawstates(color='b')
    m.drawcoastlines()
    m.drawcountries(linewidth=2)
    lons = [-73.7822222222, -74.175]
    lats = [40.6441666667, 40.6897222222]
    xp,yp = m(lons, lats)
    m.plot(xp, yp, 'bo', markersize=12)
    labels = ['JFK Airport,NY', 'Newark Airport,NJ']
    for label, xpt, ypt in zip(labels, xp, yp):
        plt.text(xpt, ypt, label)
    
    tot=len(WdayLon_x)
    for i, val in enumerate(WdayLon_x):
        if i < tot:
            temp_x = WdayLon_x[i]
            temp_y = WdayLat_y[i]
            k = i + 1
            while k < tot:
                m.drawgreatcircle(temp_x, temp_y, 
                    WdayLon_x[k], WdayLat_y[k], 
                    linewidth=0.3, color='r')
                k = k + 1
    
                
    fig = plt.figure(figsize=(8,6))
    plt.title('Uber Weekend Popular Destination')
    m = Basemap(projection='mill',  lat_0=40.7, lon_0=-74,
              llcrnrlon = -74.3,              # lower-left corner longitude
              llcrnrlat = 40.55,               # lower-left corner latitude
              urcrnrlon = -73.6,               # upper-right corner longitude
              urcrnrlat = 40.9,               # upper-right corner latitude
              resolution = 'h',
              area_thresh = 0.1)
    m.drawmapboundary()
    m.drawstates(color='b')
    m.drawcoastlines()
    m.drawcountries(linewidth=2)
    xp,yp = m(lons, lats)
    m.plot(xp, yp, 'bo', markersize=12)
    labels = ['JFK Airport,NY', 'Newark Airport,NJ']
    for label, xpt, ypt in zip(labels, xp, yp):
        plt.text(xpt, ypt, label)

    tot=len(WendLon_x)
    for i, val in enumerate(WendLon_x):
        if i < tot:
            temp_x = WendLon_x[i]
            temp_y = WendLat_y[i]
            k = i + 1
            while k < tot:
                m.drawgreatcircle(temp_x, temp_y, 
                    WendLon_x[k], WendLat_y[k], 
                    linewidth=0.3, color='r')
                k = k + 1
    return


    
def run():
#    fnames = "uber-trip-nyc-14.csv"
#    fnames = "uber-trip-nyc-14-4.csv"
    fnames = "uber-trip-nyc-14x.csv"            #Real UBER file 309.4 MB

    df = aggregate_uber_data(fnames)
    dfg_dh = groupby_dayhour_uber_data(df)
    create_daytotal_plot(dfg_dh)
    create_day_hourtotal_plot(dfg_dh)
    p = create_weekly_dailytotal_plot(dfg_dh)
    create_wend_wday_plot(dfg_dh)
    create_allweeks_daily_plot(dfg_dh)
    create_monthly_plot(dfg_dh)
    create_daily_plot(dfg_dh)

    df_all = create_wend_wday_all_location_dataframe(df)
    show_wend_wday_all_location(df_all)

    df_pop = create_wend_wday_pop_location_dataframe(df,0.001)       #drop_perc=0.001 After goupby Lat2,Lon2 Drop the percentage less than 0.001 Lat2,Lon2 
    show_wend_wday_pop_location(df_pop)
    create_wend_wday_pop_location_graph(df_pop)
    create_wend_wday_pop_destination_graph(df_pop) 

    print('End:',dt.datetime.now())
    show(p) 
    plt.show() 
    return
    
if __name__ == "__main__":
    print('Start:', dt.datetime.now())
    run()



# In[ ]:



