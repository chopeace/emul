import json,redis, mimeparse, os, sys, hashlib, random
from bottle import hook, route, request, run, template,response,abort
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir + '/firebase-python')

import firebase

print parentdir + '/firebase-python'

@hook('after_request')
def enable_cors():
    response.headers['Access-Control-Allow-Origin'] = '*'
    #response.headers['Access-Control-Allow-Origin'] = 'http://cmpt470.csil.sfu.ca:8017'
    response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'


@route('/emulator/')
def index():
   return 'Hello World This is SmartHome Emulator'

URL_ROOT = 'dazzling-heat-6704'

@route('/emulator/<userid>', method='PUT')
def put_task(userid):

    #print "emulator: received for user:%s" % userid
    # Check to make sure JSON is ok
    type = mimeparse.best_match(['application/json'], request.headers.get('Accept'))
    if not type: return abort(406)

    print "content-type: %s" % request.headers.get('Content-Type')

    # Check to make sure the data we're getting is JSON
    #if request.headers.get('Content-Type') != 'application/json': return abort(415)

    #response.headers.append('Content-Type', type)
    # Read in the data
    data = json.load(request.body)
    #print "read josn"
    command = data.get('command')
    devicename = data.get('devicename')
    print "recieved user:%s, command:%s, device:%s" % (userid,command,devicename)
    # Basic sanity checks on the task
    if iscommand(command): command = command
    if not iscommand(command): return abort(400)
    url = URL_ROOT + "/devices/%s" % userid
    
    if command == "turn_off_all":
        firebase_turn_off_all(userid)
    elif command == "turn_on_all":
        firebase_turn_on_all(userid)
        #return json.dumps(dict_device_off, ensure_ascii=False)
    elif command == "turn_on":
        firebase_turn(userid,devicename,1)
    elif command == "turn_off":
        firebase_turn(userid,devicename,0)
    elif command == "add_device":
        firebase_add_device(userid,devicename)
    elif command == "delete_device":
        firebase_delete_device(userid,devicename)
    
    #Return the result
    return {
        "Result": "OK"
    }
def get_dict_with_value(list_devices,value):
    dict_devices = {}
    for k in list_devices:
        dict_devices[k] = value
    print "get_dict_with_value : ", dict_devices
    return dict_devices
def firebase_add_device(userid, devicename):
    url = URL_ROOT + "/devices/%s" %(userid)
    dict_device = {}
    dict_device[devicename] = 0
    firebase.patch(url,dict_device)
    print "add_device with userid:%s,devicename:%s" %(userid,devicename)

def firebase_delete_device(userid, devicename):
    url = URL_ROOT + "/devices/%s" %(userid)

    dict_devices = firebase_get_device_dict(userid)
    print "delete_device(before)dict_devices:%s, devicename:%s " %( dict_devices, devicename)
    result = dict_devices.pop(devicename, None)
    print "delete_device(after) dict_devices:%s, devicename:%s " %( dict_devices, devicename)
    firebase.put(url,dict_devices)
    print "deleted_device with userid:%s,devicename:%s, result:%s" %(userid,devicename,result)


def firebase_turn(userid,devicename,value):
    url = URL_ROOT + "/devices/%s/%s" %(userid,devicename)
    firebase.put(url,value)
    print "turn_on, device:%s,value:%d, URL :%s" % (devicename,value,url)


def firebase_turn_off_all(userid):
    #get all the devices from the user, and set it to 0
    list_devices = firebase_get_device_list(userid)
    if len(list_devices) == 0:
        print "no device to update off all"
    else:
        dict_devices_off = get_dict_with_value(list_devices,0)
        print "dict_device_off" , dict_devices_off
        url = URL_ROOT + "/devices/%s" % userid
        firebase.put(url,dict_devices_off)
        print "turn_off_all, URL :%s" % url


def firebase_turn_on_all(userid):
    #get all the devices from the user, and set it to 0
    list_devices = firebase_get_device_list(userid)
    if len(list_devices) == 0:
        print "no device to update on_all"
    else:
        dict_devices_on = get_dict_with_value(list_devices,1)
        print "dict_device_on " , dict_devices_on
        url = URL_ROOT + "/devices/%s" % userid
        firebase.put(url,dict_devices_on)
        print "turn_on_all, URL :%s" % url

def firebase_get_device_list(userid):
    url = URL_ROOT + "/devices/%s" % userid
    result = firebase.get(url)
    
    device_list = []
    if isinstance(result,dict):
        for key, value in result.iteritems():
            print key, value
            device_list.append(str(key))#with remove unicode string
        print device_list
    else:
        print "firebase-get_device_list: result is not dict:",result
        
    return device_list

def firebase_get_device_dict(userid):
    url = URL_ROOT + "/devices/%s" % userid
    result = firebase.get(url)
    device_dict = {}
    if isinstance(result,dict):
        for key, value in result.iteritems():
            print key, value
            device_dict[str(key)] =str(value)
            print device_dict
    else:
        print "firebase-get_device_dict: result is not dict:",result
    return device_dict

# get instance to use from [0 to about n] instances for the tea
def iscommand(command):
    return True


if __name__ == '__main__':
    run(host='0.0.0.0', port=os.getenv('PORT', 7070), quiet=True)

