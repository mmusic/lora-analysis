# %%
from math import radians, degrees, cos, sqrt
import pandas as pd
import numpy as np
import json
from ParticleFilter import PF, PERIOD

def distance(p1, p2):
    return sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

def get_gi():
    with open(f'survey/lora-polygon_source-geojson-1656994682.txt', 'r') as gi_file:
        gi = gi_file.read().split('\n\n')
    polygons = eval(gi[0].replace('\n','')[7:])
    polygon_id = np.array(list(polygons.keys()))
    polygons = np.array(tuple(((v[0],v[1]) for p in polygons.values() for v in p))).reshape(len(polygons),4,2).transpose(2,1,0)
    beacon_str = gi[1].replace('\n','')[21:-3].split("),'")
    bx = np.empty(len(beacon_str))
    by = np.empty(len(beacon_str))
    for i, b in enumerate(beacon_str):
        idx = b.index('x=')
        bx[i] = float(b[idx+2:b.index(', ',idx)])
        idx = b.index('y=')
        by[i] = float(b[idx+2:b.index(', ',idx)])
        #idx = b.index('z=')
        #bz[i] = int(b[idx+2:b.index(', ',idx)])
    beacon_loc = pd.DataFrame(columns=['bID',0,1])
    beacon_loc['bID'] = np.array(list(map(lambda b:b[:15], beacon_str)))
    beacon_loc[0] = bx; beacon_loc[1] = by
    beacon_loc = beacon_loc.set_index('bID')
    center = (polygons.max(axis=(1,2))+polygons.min(axis=(1,2)))/2
    def geo2meter(coordinate):
        x = radians(coordinate[0] - center[0]) * 6371000 * cos(radians(center[1]))
        y = radians(coordinate[1] - center[1]) * 6371000
        return (x,y)
    def meter2geo(coordinate):
        lon = center[0] + degrees(coordinate[0] / (6371000 * cos(radians(center[1]))))
        lat = center[1] + degrees(coordinate[1] / 6371000)
        return (lon, lat)
    polygons[0] = np.radians(polygons[0]-center[0]) * 6371000 * cos(radians(center[1]))
    polygons[1] = np.radians(polygons[1]-center[1]) * 6371000
    beacon_loc[0] = np.radians(beacon_loc[0]-center[0]) * 6371000 * cos(radians(center[1]))
    beacon_loc[1] = np.radians(beacon_loc[1]-center[1]) * 6371000
    return polygons, polygon_id, beacon_loc, geo2meter, meter2geo

gt = {
'diamond_200m': {'date': ['2022/07/06 10:58:00', '2022/07/06 11:08:00'], 'coor': [114.20073744876093, 22.3412944950869]},
'dayoujie_500m': {'date': ['2022/07/06 11:24:00', '2022/07/06 11:34:00'], 'coor': [114.19885639530463, 22.338186087878373]},
'fuhaodongfang_1500m': {'date': ['2022/07/06 17:10:00', '2022/07/06 17:20:00'], 'coor': [114.1925017465669, 22.328988088616413]},
'songhuangtai_2000m': {'date': ['2022/07/06 18:16:00', '2022/07/06 18:26:00'], 'coor': [114.19031932195354, 22.325466338854763]},
}

import datetime
def date2ts(date):
    return datetime.datetime.timestamp(datetime.datetime.strptime(date, "%Y/%m/%d %H:%M:%S"))

polygons, polygon_id, beacon_loc, geo2meter, meter2geo = get_gi()

data_beacon = pd.read_csv('survey/pixel/2022-07-06_lora.csv', usecols=[1,2,3])
data_beacon.columns = ('bID', 'rssi', 'ts')
data_beacon['bID'] = data_beacon.bID.str[2:]
data_beacon = data_beacon[data_beacon.bID.isin(beacon_loc.index)]
for s in gt:

    time_range = (date2ts(gt[s]['date'][0]), date2ts(gt[s]['date'][1]))
    gt_pos = geo2meter(gt[s]['coor'])

    focus = data_beacon[(data_beacon.ts >= time_range[0]) & (data_beacon.ts < time_range[1])].reset_index()
    focus['ts'] //= PERIOD
    pf = PF((polygons, beacon_loc), (s, gt_pos))
    for t, beacon_batch in focus.groupby('ts'):
        pf.feed_data(t, beacon_batch[['bID','rssi']]) # add condition beacon_batch is not None and nonempty to run online
        if pf.tracked:
            x, y = meter2geo(pf.adsorb_polygon())
            print(f'{int(t)*PERIOD} at ({x:.3f}, {y:.3f})±{pf.pos_var:.3f}m in polygon #{polygon_id[pf.polygon_idx]};') # polygon_idx==0 means the location must not in any polygon


# %%
