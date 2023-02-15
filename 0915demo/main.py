# python3.6

import random
import json
from paho.mqtt import client as mqtt_client
import time
from math import radians, degrees, cos, sqrt
import pandas as pd
import numpy as np
from ParticleFilter import PF
import threading
import flask
from flask import make_response, request, jsonify
import logging
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.setLevel(logging.ERROR)

g_coor = (0,0)

app = flask.Flask(__name__)

def distance(p1, p2):
    return sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

# def get_gi():
#     with open('LAB.txt', 'r') as gi_file:
#         gi = gi_file.read().split('\n\n')
#     polygons = eval(gi[0].replace('\n','')[7:])
#     polygon_id = np.array(list(polygons.keys()))
#     polygons = np.array(tuple(((v[0],v[1]) for p in polygons.values() for v in p))).reshape(len(polygons),4,2).transpose(2,1,0)
#     beacon_str = gi[1].replace('\n','')[21:-3].split("),'")
#     bx = np.empty(len(beacon_str))
#     by = np.empty(len(beacon_str))
#     for i, b in enumerate(beacon_str):
#         idx = b.index('x=')
#         bx[i] = float(b[idx+2:b.index(', ',idx)])
#         idx = b.index('y=')
#         by[i] = float(b[idx+2:b.index(', ',idx)])
#         #idx = b.index('z=')
#         #bz[i] = int(b[idx+2:b.index(', ',idx)])
#     beacon_loc = pd.DataFrame(columns=['bID',0,1])
#     beacon_loc['bID'] = np.array(list(map(lambda b:b[:15], beacon_str)))
#     beacon_loc[0] = bx; beacon_loc[1] = by
#     beacon_loc = beacon_loc.set_index('bID')
#     center = (polygons.max(axis=(1,2))+polygons.min(axis=(1,2)))/2
#     def geo2meter(coordinate):
#         x = radians(coordinate[0] - center[0]) * 6371000 * cos(radians(center[1]))
#         y = radians(coordinate[1] - center[1]) * 6371000
#         return (x,y)
#     def meter2geo(coordinate):
#         lon = center[0] + degrees(coordinate[0] / (6371000 * cos(radians(center[1]))))
#         lat = center[1] + degrees(coordinate[1] / 6371000)
#         return (lon, lat)
#     polygons[0] = np.radians(polygons[0]-center[0]) * 6371000 * cos(radians(center[1]))
#     polygons[1] = np.radians(polygons[1]-center[1]) * 6371000
#     beacon_loc[0] = np.radians(beacon_loc[0]-center[0]) * 6371000 * cos(radians(center[1]))
#     beacon_loc[1] = np.radians(beacon_loc[1]-center[1]) * 6371000
#     return polygons, polygon_id, beacon_loc, geo2meter, meter2geo
# polygons, polygon_id, beacon_loc, geo2meter, meter2geo = get_gi()


polygons = np.array([[[114.26359574227803,22.33694120317442],[114.26375783225222,22.336940266120138],[114.26374995813325,22.33569671804098],[114.26358989428513,22.335696718083014]]]) 
polygons = polygons.reshape(len(polygons),4,2).transpose(2,1,0)
beacon_loc = pd.DataFrame(columns=['bID',0,1])
beacon_loc[0] = np.array((114.26364674099, 114.26365383241)); beacon_loc[1] = np.array((22.335764784157, 22.33685118156))
beacon_loc['bID'] = np.array(['mtrec-02', 'mtrec-03'])
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

#pf = {'rak-7c34':PF((polygons, beacon_loc)), 'rak-79d5':PF((polygons, beacon_loc))}
pf = PF((polygons, beacon_loc))




broker = 'nam1.cloud.thethings.network'
port = 1883
topic = "#"
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 100)}'
username = 'ust-demo-lora@ttn'
password = 'NNSXS.FE35NNNLTG2KRG446KOYZXC7QANBJG4HRRJ4FGI.4JGJCFCF227ZLD7YXS5JAVQ33YQM5Z27AEASC5F5TLYFYFLSY5EQ'


def write_json(new_data, filename):
    with open("mqtt-data.json", 'r+') as file:
        file_data = json.load(file)
        file_data["useful_data"].append(new_data)
        file.seek(0)
        json.dump(file_data, file, indent=2)


def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

# tag_id = ['rak-79d5', 'rak-7c34']
def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        global pf
        global g_coor
        # print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        payload_data = json.loads(msg.payload.decode())
        # print(time.time(), payload_data)

        for r in payload_data['uplink_message']['rx_metadata']:
            print(time.time(), payload_data['end_device_ids']['device_id'], r['gateway_ids']['gateway_id'], r['rssi'])
        # TODO: feed pf
        beacon_batch = pd.DataFrame(columns=['bID', 'rssi'])
        tag_id = payload_data['end_device_ids']['device_id']
        gateways = [g['gateway_ids']['gateway_id'] for g in payload_data['uplink_message']['rx_metadata']]
        rssi = [r['rssi'] for r in payload_data['uplink_message']['rx_metadata']]
        beacon_batch['bID'] = gateways; beacon_batch['rssi'] = rssi

        # print(tag_id, beacon_batch)
        if payload_data['end_device_ids']['device_id'] =='rak-7c34':
            pf.feed_data(time.time(), beacon_batch)
            coor = meter2geo(pf.pos_estimate)
            print(pf.tracked, coor[0])
            g_coor = coor
        #print(payload_data['uplink_message']['rx_metadata'])

    client.subscribe(topic)
    client.on_message = on_message


def run123():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()


@app.route('/latest_target_status', methods=['get', 'post'])
def latest_sensor_status():
    global g_coor
    data = [{
        'id': 'tag_id',
        'ts': time.time(),
        'date': 'date',
        'lat': g_coor[1],
        'lng':  g_coor[0],
        'error': 0,
        'status': 0,
    }]
    res = make_response(data)
    res.headers['Access-Control-Allow-Origin'] = '*'
    res.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
    res.headers['Access-Control-Allow-Headers'] = 'x-requested-with, content-type'
    return res


if __name__ == '__main__':
    # run()
    t = threading.Thread(target=run123)
    t.start()
    app.run(port=8080, debug=True, host='127.0.0.1')

# %%
