#!/usr/bin/env python
# encoding: utf-8

import json
import os
import time
import bottle
import log
import memory

ROOT_PATH = os.path.dirname(os.path.realpath(__file__))
print('ROOT_PATH', ROOT_PATH)
bottle.TEMPLATE_PATH = [os.path.join(ROOT_PATH, 'views'), './', './views']

DEBUG = bool(os.environ.get('DEBUG'))
bottle.debug(DEBUG)

PID = None          # 当前游戏进程ID
PROCESS = None      # 当前游戏进程句柄
IS_HD = None

VERSION = '20240814'


def render_json(data, status=200):
    bottle.response.status = status
    bottle.response.content_type = 'application/json'
    return json.dumps(data)

@bottle.route('/')
def index():
    roundKey = time.time() if DEBUG else VERSION
    return bottle.template('index', **{'DEBUG': DEBUG, 'roundKey': roundKey, 'VERSION': VERSION})

@bottle.route('/static/<path:path>')
def callback(path):
    return bottle.static_file(path, root=os.path.join(ROOT_PATH, 'static'))

@bottle.get('/api/v1/processes')
def get_process_list():
    data = memory.list_process()
    return render_json(data)


@bottle.post('/api/v1/memory')
def read_process_memory():
    pid = int(bottle.request.json['pid'])
    address = bottle.request.json['address']
    size = int(bottle.request.json['size'])

    hProcess = memory.inject_process(pid)
    addr_bytes = bytes.fromhex(memory.address_to_hex_byte(address))
    base_addr = memory.bytes_to_int(addr_bytes, len(addr_bytes))
    log.debug("read %d memory from %s[%x] %d bytes" % (pid, address, base_addr, size))
    buf = memory.read_process(hProcess, base_addr, size)
    memory.close_process(hProcess)

    r = memory.bytes_to_hex_str(buf)
    data = [r[i:i+2] for i in range(0, len(r), 2)]
    return render_json({'data': data})


@bottle.post('/api/v1/bytes2str')
def convert_bytes2str():
    """
    将字节转为字符串
    """
    data = bottle.request.json['data']
    coding = bottle.request.json.get('coding') or 'gbk'

    ret = memory.hex_byte_to_str(data, coding)
    return render_json({'data': ret})


@bottle.post('/api/v1/str2bytes')
def convert_bytes2():
    """
    将字符串转为字节
    """
    data = bottle.request.json['data']
    coding = bottle.request.json.get('coding') or 'gbk'

    ret = memory.str_to_hex_byte(data, coding)
    return render_json({'data': ret})


if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', '9090'))
    print('start with debug:', DEBUG, PORT)
    log.set_level(DEBUG)
    bottle.run(host='0.0.0.0', port=PORT, debug=True, reloader=DEBUG)
