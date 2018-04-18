from subprocess import Popen, PIPE
import json

SET = 'set'
GET = 'get'
EXPOSURE = 'absoluteExposureTime'

def uvcc(action, control=None, value=None):
    cmd = 'uvcc --vendor 0x5a3 --product 0x9520 {0}'.format(action)
    if control:
        cmd += ' {0}'.format(control)
    if value:
        cmd += ' {0}'.format(value)
    p = Popen(cmd.split(' '), stdout=PIPE, stderr=PIPE)
    so = p.communicate()[0].decode().strip()
    return so

def get_ranges():
    return json.loads(uvcc('ranges'))

def get_range(parameter):
    return get_ranges()[parameter]

def get_value(parameter):
    return uvcc(GET, parameter)

def set_value(parameter, value):
    uvcc(SET, parameter, value)

def auto_exposure_on():
    set_value('autoExposureMode', 8)

def auto_exposure_off():
    set_value('autoExposureMode', 1)
