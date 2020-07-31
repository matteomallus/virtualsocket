from time import time

import eventlet
import socketio
import logging

# from costants import API_KEY
logger = logging.getLogger(__name__)

# logger.info("SIO server")
print("SIO server")

sio = socketio.Server(cors_allowed_origins='*')
app = socketio.WSGIApp(sio)

clients = {
    "django": {},
    "node": {}
}


@sio.event
def connect(sid, environ):
    print("ENVIRON=", environ)
    if environ["HTTP_CLIENT_TYPE"] != 'django':
        sio.emit("node_connected", {
            "client_type": environ["HTTP_CLIENT_TYPE"],
            "client_id": environ["HTTP_CLIENT_ID"],
            "sid": sid
        })
        # assert environ['HTTP_AUTHENTICATION'] == API_KEY
        # HTTP_CLIENT_TYPE = environ["HTTP_CLIENT_TYPE"]
        # clients[HTTP_CLIENT_TYPE][sid] = {"environ": environ}
        # print("Connected {} {}".format(HTTP_CLIENT_TYPE, sid))
        # connected = "{}_connected".format(HTTP_CLIENT_TYPE)
        # print(connected)
        # sio.emit(connected, "client_id_here")


@sio.event
def node_command(sid, data):
    try:
        data['sender'] = sid  # Django
        print('node_command from {}:  {}', sid, data)
        node_sid = data['node_sid']
        # assert node_sid in clients['node'], "Not a Node"
        return sio.call("node_command", data, to=node_sid)
    except Exception as e:
        return {"error": str(e)}


@sio.event
def node_event(sid, data):
    """
    chiamato dal nodo
    :param sid:
    :param data:
    :return:
    """
    print(time())
    print('node_event from {}:  {}', sid, data)
    sio.emit("node_event", data)


@sio.event
def disconnect(sid):
    print('disconnect ', sid)
    for k, v in clients.items():
        if sid in v:
            sio.emit("{}_disconnected".format(k), "client_id_here")


print("Listen ...")

eventlet.wsgi.server(eventlet.listen(('', 80)), app)
