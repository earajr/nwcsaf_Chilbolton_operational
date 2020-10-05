from netCDF4 import Dataset
import numpy as np
from scipy.ndimage import gaussian_filter 
import os
import sys
from skimage import measure

#define input file

input_fil = sys.argv[1]

# define output directory

output_dir = "/data/FASTA/CRR_geojson"

# Read in lat and lon values from full disk lat lon file

lat_lon = Dataset("/data/CEH_NFLICS/SEVIRI_lat_lon_fulldisk.nc", "r")

lat = lat_lon.variables['lat']
lon = lat_lon.variables['lon']

# Read in CRR intensity values from latest CRR file.

CRR_fil = Dataset(input_fil, "r")

start_time = CRR_fil.time_coverage_start
file_name = CRR_fil.id[:-3]

CRR = CRR_fil.variables['crr_intensity'][:,:]
CRR = np.where(CRR>5000.0, 0, CRR)
CRR = gaussian_filter(CRR, sigma=5)

levels = ["CRR_02_1", "CRR_1_2", "CRR_2_3", "CRR_3_5", "CRR_5_7", "CRR_7_10", "CRR_10_15", "CRR_15_20", "CRR_20_30", "CRR_30_50", "CRR_50_plus"]
thresholds = [0.2, 1.0, 2.0, 3.0, 5.0, 7.0, 10.0, 15.0, 20.0, 30.0, 50.0]

level_masks = {}
level_contours = {}
level_cells = {}

for i in range(0, len(levels)):
   temp_CRR = (CRR>=thresholds[i])
   level_masks[levels[i]] = temp_CRR.astype(np.int32)
   level_contours[levels[i]] = measure.find_contours(level_masks[levels[i]], 0.5)
   level_cells[levels[i]] = []
   for j in range(0, len(level_contours[levels[i]])):
      maxxindex = np.max(level_contours[levels[i]][j][:,0])
      minxindex = np.min(level_contours[levels[i]][j][:,0])
      maxyindex = np.max(level_contours[levels[i]][j][:,1])
      minyindex = np.min(level_contours[levels[i]][j][:,1])
      if ( i > 0 ):
         for k in range(0, len(level_cells[levels[i-1]])):
            if (maxxindex <= level_cells[levels[i-1]][k]["max_xindex"] and minxindex >= level_cells[levels[i-1]][k]["min_xindex"] and maxyindex <= level_cells[levels[i-1]][k]["max_yindex"] and minyindex >= level_cells[levels[i-1]][k]["min_yindex"]):
               thiscell = {"cell_id":j, "min_xindex": minxindex, "max_xindex": maxxindex, "min_yindex": minyindex, "max_yindex": maxyindex, "parent_cell":level_cells[levels[i-1]][k]["cell_id"]}
               continue
      else:
         thiscell = {"cell_id":j, "min_xindex": minxindex, "max_xindex": maxxindex, "min_yindex": minyindex, "max_yindex": maxyindex, "parent_cell":""}
      level_cells[levels[i]].append(thiscell.copy())

with open(output_dir+'/'+file_name+'.geojson', 'a') as CRR_file:
   CRR_file.write('{\n')
   CRR_file.write('                        "type": "FeatureCollection",\n')
   CRR_file.write('                        "dimensions": { "time":{"value":"'+start_time+'", "units": "ISO8601" }, "elevation": {"value": "0", "units": "meter"}},\n')
   CRR_file.write('                            "features": [')

   features = ''

   for i in range(0, len(levels)):
      if (i < len(levels)-1):
         for j in range(0, len(level_contours[levels[i]])):
            out_of_bounds = 0
            feature = '{ "type": "Feature",\n            "properties": {"ObjectType": "CRR-retrieval", "RainRate": "'+levels[i]+'"},\n          "geometry": {\n              "type": "Polygon",\n              "coordinates": [['
            coords = ''
            for k in range(0, len(level_contours[levels[i]][j])):
               if (level_contours[levels[i]][j][k][0] % 1 != 0 and level_contours[levels[i]][j][k][1] % 1 != 0):
                  index_1 = level_contours[levels[i]][j][k][0]
                  index_2 = level_contours[levels[i]][j][k][1]

                  lat_1 = lat[int(index_1-0.5),int(index_2-0.5)]
                  lat_2 = lat[int(index_1+0.5),int(index_2+0.5)]

                  lon_1 = lon[int(index_1-0.5),int(index_2-0.5)]
                  lon_2 = lon[int(index_1+0.5),int(index_2+0.5)]
           
                  temp_lat = (lat_1 + lat_2)/2.0
                  temp_lon = (lon_1 + lon_2)/2.0
               elif (level_contours[levels[i]][j][k][0] % 1 != 0 and level_contours[levels[i]][j][k][1] % 1 == 0):
                  index_1 = level_contours[levels[i]][j][k][0]
                  index_2 = level_contours[levels[i]][j][k][1]

                  lat_1 = lat[int(index_1-0.5),int(index_2)]
                  lat_2 = lat[int(index_1+0.5),int(index_2)]

                  lon_1 = lon[int(index_1-0.5),int(index_2)]
                  lon_2 = lon[int(index_1+0.5),int(index_2)]

                  temp_lat = (lat_1 + lat_2)/2.0
                  temp_lon = (lon_1 + lon_2)/2.0
               elif (level_contours[levels[i]][j][k][0] % 1 == 0 and level_contours[levels[i]][j][k][1] % 1 != 0):
                  index_1 = level_contours[levels[i]][j][k][0]
                  index_2 = level_contours[levels[i]][j][k][1]

                  lat_1 = lat[int(index_1),int(index_2-0.5)]
                  lat_2 = lat[int(index_1),int(index_2+0.5)]

                  lon_1 = lon[int(index_1),int(index_2-0.5)]
                  lon_2 = lon[int(index_1),int(index_2+0.5)]

                  temp_lat = (lat_1 + lat_2)/2.0
                  temp_lon = (lon_1 + lon_2)/2.0
               else:
                  index_1 = level_contours[levels[i]][j][k][0]
                  index_2 = level_contours[levels[i]][j][k][1]

                  lat_1 = lat[int(index_1),int(index_2)]
                  lat_2 = lat[int(index_1),int(index_2)]

                  lon_1 = lon[int(index_1),int(index_2)]
                  lon_2 = lon[int(index_1),int(index_2)]

                  temp_lat = (lat_1 + lat_2)/2.0
                  temp_lon = (lon_1 + lon_2)/2.0

               if (np.isnan(temp_lat) or np.isnan(temp_lon)):
                  out_of_bounds = 1
                  break
               else:
                  coord = '[%f,%f],' % (temp_lon, temp_lat)
                  coords += coord
            coords = coords[:-1]
            coords += ']'
            feature += coords
            if (out_of_bounds == 0):
               for k in range(0, len(level_cells[levels[i+1]])):
                  if (level_cells[levels[i+1]][k]["parent_cell"] == j):
                     coords = '\n                             ,['
                     for l in range(0, len(level_contours[levels[i+1]][k])):
                        if (level_contours[levels[i+1]][k][l][0] % 1 != 0 and level_contours[levels[i+1]][k][l][1] % 1 != 0):
                           index_1 = level_contours[levels[i+1]][k][l][0]
                           index_2 = level_contours[levels[i+1]][k][l][1]
  
                           lat_1 = lat[int(index_1-0.5),int(index_2-0.5)]
                           lat_2 = lat[int(index_1+0.5),int(index_2+0.5)]

                           lon_1 = lon[int(index_1-0.5),int(index_2-0.5)]
                           lon_2 = lon[int(index_1+0.5),int(index_2+0.5)]

                           temp_lat = (lat_1 + lat_2)/2.0
                           temp_lon = (lon_1 + lon_2)/2.0
                        elif (level_contours[levels[i+1]][k][l][0] % 1 != 0 and level_contours[levels[i+1]][k][l][1] % 1 == 0):
                           index_1 = level_contours[levels[i+1]][k][l][0]
                           index_2 = level_contours[levels[i+1]][k][l][1]
  
                           lat_1 = lat[int(index_1-0.5),int(index_2)]
                           lat_2 = lat[int(index_1+0.5),int(index_2)]
 
                           lon_1 = lon[int(index_1-0.5),int(index_2)]
                           lon_2 = lon[int(index_1+0.5),int(index_2)]

                           temp_lat = (lat_1 + lat_2)/2.0
                           temp_lon = (lon_1 + lon_2)/2.0
                        elif (level_contours[levels[i+1]][k][l][0] % 1 == 0 and level_contours[levels[i+1]][k][l][1] % 1 != 0):
                           index_1 = level_contours[levels[i+1]][k][l][0]
                           index_2 = level_contours[levels[i+1]][k][l][1]
 
                           lat_1 = lat[int(index_1),int(index_2-0.5)]
                           lat_2 = lat[int(index_1),int(index_2+0.5)]

                           lon_1 = lon[int(index_1),int(index_2-0.5)]
                           lon_2 = lon[int(index_1),int(index_2+0.5)]

                           temp_lat = (lat_1 + lat_2)/2.0
                           temp_lon = (lon_1 + lon_2)/2.0
                        else:
 
                           index_1 = level_contours[levels[i+1]][k][l][0]
                           index_2 = level_contours[levels[i+1]][k][l][1]

                           lat_1 = lat[int(index_1),int(index_2)]
                           lat_2 = lat[int(index_1),int(index_2)]
 
                           lon_1 = lon[int(index_1),int(index_2)]
                           lon_2 = lon[int(index_1),int(index_2)]

                           temp_lat = (lat_1 + lat_2)/2.0
                           temp_lon = (lon_1 + lon_2)/2.0

                        if (np.isnan(temp_lat) or np.isnan(temp_lon)):
                           coords = ''
                           break
                        else:
                           coord = '[%f,%f],' % (temp_lon, temp_lat)
                           coords += coord
                     coords = coords[:-1]
                     coords += ']'
                     feature += coords
            feature += ']\n                  }\n                },'
            if (out_of_bounds == 0):
               features += feature
            else:
               feature = ''
               features += feature
      else:
         for j in range(0, len(level_contours[levels[i]])):
            print(levels[i])
            out_of_bounds = 0
            feature = '{ "type": "Feature",\n            "properties": {"ObjectType": "CRR-retrieval", "RainRate": "'+levels[i]+'"},\n          "geometry": {\n              "type": "Polygon",\n              "coordinates": [['
            coords = ''
            for k in range(0, len(level_contours[levels[i]][j])):
               if (level_contours[levels[i]][j][k][0] % 1 != 0 and level_contours[levels[i]][j][k][1] % 1 != 0):
                  index_1 = level_contours[levels[i]][j][k][0]
                  index_2 = level_contours[levels[i]][j][k][1]

                  lat_1 = lat[int(index_1-0.5),int(index_2-0.5)]
                  lat_2 = lat[int(index_1+0.5),int(index_2+0.5)]

                  lon_1 = lon[int(index_1-0.5),int(index_2-0.5)]
                  lon_2 = lon[int(index_1+0.5),int(index_2+0.5)]

                  temp_lat = (lat_1 + lat_2)/2.0
                  temp_lon = (lon_1 + lon_2)/2.0
               elif (level_contours[levels[i]][j][k][0] % 1 != 0 and level_contours[levels[i]][j][k][1] % 1 == 0):
                  index_1 = level_contours[levels[i]][j][k][0]
                  index_2 = level_contours[levels[i]][j][k][1]

                  lat_1 = lat[int(index_1-0.5),int(index_2)]
                  lat_2 = lat[int(index_1+0.5),int(index_2)]

                  lon_1 = lon[int(index_1-0.5),int(index_2)]
                  lon_2 = lon[int(index_1+0.5),int(index_2)]

                  temp_lat = (lat_1 + lat_2)/2.0
                  temp_lon = (lon_1 + lon_2)/2.0
               elif (level_contours[levels[i]][j][k][0] % 1 == 0 and level_contours[levels[i]][j][k][1] % 1 != 0):
                  index_1 = level_contours[levels[i]][j][k][0]
                  index_2 = level_contours[levels[i]][j][k][1]

                  lat_1 = lat[int(index_1),int(index_2-0.5)]
                  lat_2 = lat[int(index_1),int(index_2+0.5)]

                  lon_1 = lon[int(index_1),int(index_2-0.5)]
                  lon_2 = lon[int(index_1),int(index_2+0.5)]

                  temp_lat = (lat_1 + lat_2)/2.0
                  temp_lon = (lon_1 + lon_2)/2.0
               else:
                  index_1 = level_contours[levels[i]][j][k][0]
                  index_2 = level_contours[levels[i]][j][k][1]

                  lat_1 = lat[int(index_1),int(index_2)]
                  lat_2 = lat[int(index_1),int(index_2)]

                  lon_1 = lon[int(index_1),int(index_2)]
                  lon_2 = lon[int(index_1),int(index_2)]

                  temp_lat = (lat_1 + lat_2)/2.0
                  temp_lon = (lon_1 + lon_2)/2.0

               if (np.isnan(temp_lat) or np.isnan(temp_lon)):
                  out_of_bounds = 1
                  break
               else:
                  coord = '[%f,%f],' % (temp_lon, temp_lat)
                  coords += coord
            coords = coords[:-1]
            coords += ']'
            feature += coords
            feature += ']\n                  }\n                },'
            if (out_of_bounds == 0):
               features += feature
            else:
               feature = ''
               features += feature
   features = features[:-1]
   features += ' ] }'
   CRR_file.write(features)
