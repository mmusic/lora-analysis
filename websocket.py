import websocket
import json
import csv
import datetime
import time


def date2ts(date):
    return datetime.datetime.timestamp(datetime.datetime.strptime(date, "%Y/%m/%d %H:%M:%S"))


def ts2date(timestamp):
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')


filename = ts2date(time.time()) + '.csv'
f = open(filename, 'a')
f_csv = csv.writer(f)

router_info = {
    '20080029c69feeb': {'lat': 22.3482, 'lon': 114.1955, 'name': 'SPK  五芳街'},
    '20180029c69feeb': {'lat': 22.3482, 'lon': 114.1955, 'name': 'SPK  五芳街'},
    '20080029c1e38f3': {'lat': 22.33859328048492, 'lon': 114.19964039078596, 'name': 'SPK'},
    '20080029c5e3677': {'lat': 22.34135627968526, 'lon': 114.20243539614061, 'name': 'Diamond Hill'},
    '20180029c4574b6': {'lat': -1, 'lon': -1, 'name': '畢架山'},
    '20080029c4574b6': {'lat': -1, 'lon': -1, 'name': '畢架山'},
    '20080029c1ea300': {'lat': -1, 'lon': -1, 'name': 'Kowloon Bay'},
    '2005813d31be7ec': {'lat': 22.336689562679826, 'lon': 114.19884682603602, 'name': 'SPK   八達街'},
    '20180029c7b7b60': {'lat': 22.325141812687036, 'lon': 114.21082667902576, 'name': 'Kowloon Bay(Metro Center 2)'},
    '20080029c69ffc2': {'lat': -22.314991786929966, 'lon': 114.1830702585825, 'name': '何文田邨適文樓'},
}

def on_message(wsapp, message):
    try:
        j = json.loads(message)
        routers = j['upinfo']
        for router in routers:
            # print(hex(router['routerid'])[2:], router['rssi'], router_info[hex(router['routerid'])[2:]]['name'])
            data = [hex(router['routerid'])[2:], router['rssi'], router['ArrTime']]
            print(data)
            f_csv.writerow([message])
            f.flush()
    except Exception as e:
        print('Error!', e, message)


wsapp = websocket.WebSocketApp("ws://lns-test.southeastasia.cloudapp.azure.com/owner-c::6305", on_message=on_message)
wsapp.run_forever()

# recv = '{"DR":2,"Freq":923600000,"FPort":2,"DevEui":"AC-1F-09-FF-FE-06-7C-36","FCntUp":14,"SessID":5146582690336,"dClass":"A","region":"AS923","upinfo":[{"rtt":[77,84,89],"snr":-10.5,"rssi":-108,"muxid":0,"xtime":3505071380,"doorid":0,"rxtime":1656823276.3180239201,"ArrTime":1656823276.3425583839,"RxDelay":0,"RX1DRoff":0,"regionid":1001,"routerid":144255936775943350},{"rtt":[76,82,122],"snr":-10,"rssi":-107,"muxid":0,"xtime":3503548156,"doorid":0,"rxtime":1656823276.3322520256,"ArrTime":1656823276.3496935368,"RxDelay":0,"RX1DRoff":0,"regionid":1001,"routerid":144537411752654006},{"rtt":[97,109,125],"snr":-6.25,"rssi":-108,"muxid":0,"xtime":3574180052,"doorid":0,"rxtime":1656823276.3133571148,"ArrTime":1656823276.3586163521,"RxDelay":0,"RX1DRoff":0,"regionid":1001,"routerid":144255936773399296},{"rtt":[82,88,100],"snr":1,"rssi":-107,"muxid":0,"xtime":506581508,"doorid":0,"rxtime":1656823276.3327329159,"ArrTime":1656823276.3816521168,"RxDelay":0,"RX1DRoff":0,"regionid":1020,"routerid":144537411755048683}],"DevAddr":14054310,"confirm":false,"msgtype":"upinfo","ciphered":false,"regionid":1099578475516,"AFCntDown":10,"AppSKeyEnv":null,"FRMPayload":"555354555354","upid":173594477218405472}'
# j = json.loads(recv)
# routers = j['upinfo']
# for router in routers:
#     print(hex(router['routerid'])[2:], router['rssi'], router_info[hex(router['routerid'])[2:]]['name'])
