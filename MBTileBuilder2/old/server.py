#!/usr/bin/python
import os

try:
    virtenv = os.environ['OPENSHIFT_PYTHON_DIR'] + '/virtenv/'
    virtualenv = os.path.join(virtenv, 'bin/activate_this.py')
    try:
        execfile(virtualenv, dict(__file__=virtualenv))
    except IOError:
        pass
except:
    pass

import glob
import TileStache

def get_config():
    config = {
        "cache": {
                    "name": "Test",
                    "path": "/tmp/stache",
                    "umask": "0000"
                },
        "layers": {}
    }
    folders = glob.glob('data/*')
    for folder in folders:
        config["layers"][folder.replace('data/','')] = {
            "provider": {
                "name": "mapnik",
                "mapfile":  glob.glob(folder + '/style.xml')[0]
            },
            "projection": "spherical mercator"
        }
    return config

config = TileStache.Config.buildConfiguration(get_config())
application = TileStache.WSGITileServer(config)

if __name__ == '__main__':
    from werkzeug.serving import run_simple
    # use_reloader=True
    run_simple('127.0.0.1', 5555, application)

