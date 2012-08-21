'''
Created on Aug 12, 2012

@author: Rob
'''

import argparse, random, os, json, copy, time, hashlib, cherrypy

from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from ws4py.websocket import WebSocket
from ws4py.messaging import TextMessage

_clients = {}
_clientsIds = {}

_object_details = {"111111":
                   {"ID": "111111",
                        "targetImgs": [{"http://flow.robhemsley.co.uk/API/v0/123456778/img/"}],
                        "details": {},
                        "interfaces": {
                                "output": {
                                },
                                "input": {
                                            "open": "http://flow.robhemsley.co.uk/API/v0/123456778/data/",
                                } 
                        }
                    },
                   
                   "222222":
                   {"ID": "222222",
                        "targetImgs": [{"img_url": "http://flow.robhemsley.co.uk/API/v0/987654321/img/"}],
                        "details": {},
                        "interfaces": {
                                "output": {
                                           "open": "http://flow.robhemsley.co.uk/API/v0/987654321/open/"
                                },
                                "input": {
                                } 
                        }
                    }
                   }
                   
                   





def clean_msg(msg):
    msg = str(msg).strip()
    jsonMsg = {}
    try:
        jsonMsg = json.loads(msg)
    except ValueError:
        pass
    
    return jsonMsg

def create_reply(in_msg):
    out = FlowMsg(None)
    out.set_from(in_msg.get_to())
    out.set_to(in_msg.get_from())
    out.set_action(in_msg.get_action())
    out.set_status(in_msg.get_status())
    
    return out
        
class FlowMsg:
    msg = None
    
    def __init__(self, msg = None):
        print type(msg)
        if msg == None:
            msg = {"to": "", "from": "", "action": "", "hash": "", "body": "", "status": "", "timestamp": ""}
        elif not isinstance(msg, dict):
            msg = clean_msg(str(msg))
            
        self.msg = msg
        
    def _get_value(self, key):
        if key in self.msg:
            return self.msg[key]
        else:
            return None
        
    def _set_value(self, key, value):
        self.msg[key] = value
        if key != "hash":
            self.set_hash()
        
    def validate_hash(self):
        try:
            tmp = copy.deepcopy(self.msg)
            del tmp["hash"]
            m = hashlib.md5()
            m.update(json.dumps(tmp))
            if self.get_hash() == m.digest().encode("hex"):
                return True
            else:
                return False
        except Exception:
            return False
        
    def get_to(self):
        return self._get_value("to")

    def get_from(self):
        return self._get_value("from")

    def get_action(self):
        return self._get_value("action")
    
    def get_body(self):
        return self._get_value("body")
    
    def get_status(self):
        return self._get_value("status")
    
    def get_hash(self):
        return self._get_value("hash")

    def get_timestamp(self):
        return self._get_value("timestamp")
    
    def set_to(self, val):
        self._set_value("to", val)

    def set_from(self, val):
        self._set_value("from", val)

    def set_action(self, val):
        self._set_value("action", val)
    
    def set_body(self, val):
        self._set_value("body", val)
    
    def set_status(self, val):
        self._set_value("status", val)
        
    def set_timestamp(self, val):
        self._set_value("timestamp", val)
    
    def set_hash(self):
        tmp = copy.deepcopy(self.msg)
        del tmp["hash"]
        m = hashlib.md5()
        m.update(json.dumps(tmp))
        self._set_value("hash", str(m.digest().encode("hex")))
    
    def __repr__(self):
        self.set_timestamp(str(time.time()))
        return str(json.dumps(self.msg))
    
    
def process(conn, msg):
    msg = FlowMsg(msg)
        
    """if not msg.validate_hash():
        try:
            msg.set_hash()
            print str(msg)   
            
            tmp = create_reply(msg)
            tmp.set_status(400)
            conn.send(str(tmp))
        except:
            conn.close()
                    
    else:"""
    action = msg.get_action()
    msg_to =  msg.get_to()
    msg_from = msg.get_from() 
    
    if msg_to == "000000":
        if action == "AUTH_REQUEST":
            conn._deviceID = msg.get_from()
            _clientsIds[conn._deviceID] = conn._wsKey
                
            tmp = create_reply(msg)
            tmp.set_action("AUTH_RESPONSE")
            conn.send(str(tmp))
        
        elif action == "GET_OBJECTS":                
            tmp = create_reply(msg)
            output = []
            for value in _object_details.itervalues():
                output.append(value)
                            
            tmp.set_body(str(output))
            conn.send(str(tmp))  
        
        elif action == "GET_OBJECT":                
            tmp = create_reply(msg)
            output = []

            jsonMsg = json.loads(str(msg.get_body()))
            output.append(_object_details[jsonMsg["deviceId"]])
                            
            tmp.set_body(str(output))
            conn.send(str(tmp))     
            
        else:
            tmp = create_reply(msg)
            tmp.set_status(404)
            conn.send(str(msg))
            
    else:
        if msg_to in _clientsIds:
            _clients[_clientsIds[msg_to]].send(str(msg))
            conn.send("SENT")
            
        else:
            tmp = create_reply(msg)
            tmp.set_status(404)
            conn.send(str(msg))
             
    print _clients
    print _clientsIds

class FlowClientWebSocketHandler(WebSocket):
    _deviceID = None
    _wsKey = None
    
    def __init__(self, *args, **kw):
        WebSocket.__init__(self, *args, **kw)
        self._wsKey = args[3]['HTTP_SEC_WEBSOCKET_KEY']
        _clients[self._wsKey] = self

    def received_message(self, m):
        process(self, m)
        #cherrypy.engine.publish('websocket-broadcast', m)
        
    def closed(self, code, reason="A client left the room without a proper explanation."):
        cherrypy.engine.publish('websocket-broadcast', TextMessage(reason))
        del _clients[self._wsKey]
        if self._deviceID != None:
            del _clientsIds[self._deviceID]
        
class Root(object):
    def __init__(self, host, port, ssl=False):
        self.host = host
        self.port = port
        self.scheme = 'wss' if ssl else 'ws'

    @cherrypy.expose
    def index(self):
        return """<html>
    <head>
      <script type='application/javascript' src='/js/jquery-1.6.2.min.js'></script>
      <script type='application/javascript'>
        $(document).ready(function() {

          websocket = '%(scheme)s://%(host)s:%(port)s/ws';
          if (window.WebSocket) {
            ws = new WebSocket(websocket);
          }
          else if (window.MozWebSocket) {
            ws = MozWebSocket(websocket);
          }
          else {
            console.log('WebSocket Not Supported');
            return;
          }

          window.onbeforeunload = function(e) {
            $('#chat').val($('#chat').val() + 'Bye bye...\\n');
            ws.close(1000, '%(username)s left the room');
                 
            if(!e) e = window.event;
            e.stopPropagation();
            e.preventDefault();
          };
          ws.onmessage = function (evt) {
             $('#chat').val($('#chat').val() + evt.data + '\\n');
          };
          ws.onopen = function() {
             ws.send('{"body": "", "status": 200, "from": "%(username)s", "timestamp": 1344790819.18658, "to": "000000", "action": "AUTH_REQUEST", "hash": "c8091b15922941dbbd8201c462c0ca8a"}');
          };
          ws.onclose = function(evt) {
             $('#chat').val($('#chat').val() + 'Connection closed by server: ' + evt.code + ' \"' + evt.reason + '\"\\n');  
          };

          $('#send').click(function() {
             console.log($('#message').val());
             ws.send($('#message').val());
             $('#message').val("");
             return false;
          });
        });
      </script>
    </head>
    <body>
    <form action='#' id='chatform' method='get'>
      <textarea id='chat' cols='35' rows='10'></textarea>
      <br />
      <label for='message'>%(username)s: </label><input type='text' id='message' />
      <input id='send' type='submit' value='Send' />
      </form>
    </body>
    </html>
    """ % {'username': "%d" % random.randint(0, 10000), 'host': self.host, 'port': self.port, 'scheme': self.scheme}

    @cherrypy.expose
    def ws(self):
        cherrypy.request.ws_handler.send("test")
        cherrypy.log("Handler created: %s" % repr(cherrypy.request.ws_handler))
        
    @cherrypy.expose
    def notify(self, msg):
        for conn in _clients.itervalues():
            conn.send(msg)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Echo CherryPy Server')
    parser.add_argument('--host', default='18.111.4.200')
    parser.add_argument('-p', '--port', default=9000, type=int)
    parser.add_argument('--ssl', action='store_true')
    args = parser.parse_args()

    cherrypy.config.update({'server.socket_host': args.host,
                            'server.socket_port': args.port,
                            'tools.staticdir.root': os.path.abspath(os.path.join(os.path.dirname(__file__), 'static'))})

    if args.ssl:
        cherrypy.config.update({'server.ssl_certificate': './server.crt',
                                'server.ssl_private_key': './server.key'})
                            
    WebSocketPlugin(cherrypy.engine).subscribe()
    cherrypy.tools.websocket = WebSocketTool()

    cherrypy.quickstart(Root(args.host, args.port, args.ssl), '', config={
        '/ws': {
            'tools.websocket.on': True,
            'tools.websocket.handler_cls': FlowClientWebSocketHandler
            },
        '/js': {
              'tools.staticdir.on': True,
              'tools.staticdir.dir': 'js'
            },
         '/test': {
              'tools.staticdir.on': True,
              'tools.staticdir.dir': 'test'
            }
        }
    )
