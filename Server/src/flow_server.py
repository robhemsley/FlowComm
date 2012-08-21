
from FlowDB import flowDb
import logging
import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
from tornado.options import define, options

import random, os, json, copy, time, hashlib, os.path, uuid, random

define("port", default=9000, help="run on the given port", type=int)

_clients = {}
_clientsIds = {}

flowDbController = flowDb()

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
    out.set_action(in_msg.get_action()+"_RESPONSE")
    out.set_status(in_msg.get_status())
    out.set_id(in_msg.get_id())
    
    return out
        
class FlowMsg:
    msg = None
    
    def __init__(self, msg = None):
        if msg == None:
            msg = {"to": "", "from": "", "action": "", "hash": "", "body": "", "status": "", "timestamp": "", "msgId": random.randint(0,999999)}
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
    
    def get_id(self):
        return self._get_value("msgId")
    
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
        
    def set_id(self, val):
        return self._set_value("msgId", val)
    
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
            tmpID = msg.get_from()
            if tmpID == "DYNAMIC":                                
                tmp = create_reply(msg)
                tmp.set_action("SET_ID")
                while True:
                    id = random.randint(5000,6000)
                    if id not in flowDbController.get_all_objects():
                        break
                    
                tmp.set_body(json.dumps({"deviceId":str(id)}))
                conn.write_message(str(tmp))
            else:
                conn._deviceID = msg.get_from()
            
                _clientsIds[conn._deviceID] = conn._deviceUUID
                    
                tmp = create_reply(msg)
                tmp.set_action("AUTH_RESPONSE")
                conn.write_message(str(tmp))
            
        elif action == "GET_OBJECTS":                
            tmp = create_reply(msg)
            output = []
            for value in flowDbController.get_all_objects().itervalues():
                output.append(value.process_object())
                            
            tmp.set_body(json.dumps(output))
            conn.write_message(str(tmp))  
        
        elif action == "GET_OBJECT":                
            tmp = create_reply(msg)
            output = []

            jsonMsg = json.loads(str(msg.get_body()))
            output.append(flowDbController.get_object(int(jsonMsg["deviceId"])).process_object())
            tmp.set_body(json.dumps(output))
            conn.write_message(str(tmp))     
            
        else:
            tmp = create_reply(msg)
            tmp.set_status(404)
            conn.write_message(str(msg))
            
    else:
        if msg_to in _clientsIds:
            _clients[_clientsIds[msg_to]].write_message(str(msg))
            tmp = create_reply(msg)

            conn.write_message(str(tmp))        
        else:
            tmp = create_reply(msg)
            tmp.set_status(404)
            tmp.set_body("Device Not Online...")

            conn.write_message(str(tmp))
    

def print_stats():
    output = "\n////////////////////////\n//    Device Stats    //\n////////////////////////\n"
    output += "\nTotals Devices: %d"%(len(_clientsIds))
    logging.info(output)    
    
class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/client", ClientHandler),
            (r"/flowsocket", FlowSocketHandler),
            (r"/admin/(.*)", AdminHandler),
            (r"/API/V0/(.*)", APIHandler),
            (r'/imgdata/(.*)', tornado.web.StaticFileHandler, {'path': "usrfiles/"}),
        ]
        
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=False,
            autoescape=None,
            xheaders=True,
            debug=True
        )
        tornado.web.Application.__init__(self, handlers, **settings)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("flow_app.html")
        
class AdminHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        args = args[0].split("/")
        if args[0] == "":
            self.render("flow_admin.html")
        elif args[0] == "objects":
            self.render("flow_admin_objects.html")
        elif args[0] == "object":
            logging.info("here");
            logging.info(self.get_argument("objId"))
            self.render("flow_admin_object.html", objId=self.get_argument("objId"))
        else:
            self.render("flow_admin.html")
        print args
        print kwargs
        
class APIHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        dir = args[0].split("/")
        
        logging.info("UserID:"+dir[0]);
        if dir[1] == "objects":
            logging.info("objects")
            output = []
            for value in flowDbController.get_all_objects().itervalues():
                output.append(value.process_object())
                            
            self.write(json.dumps(output))
            
        if dir[1] == "object":
            output = []
            logging.info(flowDbController.get_object(dir[2]))
            output.append(flowDbController.get_object(dir[2]).process_object())
                            
            self.write(json.dumps(output))

        print args
        print kwargs
        
    def post(self, *args, **kwargs):
        logging.info(args)
        dir = args[0].split("/")
        if len(dir) > 1:
            if dir[1] == "objDetailsUpdate":
                object = flowDbController.update_object(dir[0])
                object.update_object(self.get_argument("detailsDetails"), self.get_argument("detailsTitle"))
                
            if dir[1] == "objImageUpdate":
                imgHeight = self.get_argument("imgHeight")
                imgWidth = self.get_argument("imgWidth")
                imgUrl = self.get_argument("imgUrl")
                
                object = flowDbController.update_object(dir[0])
                logging.info("cats")
                if "imgFile" in self.request.files:
                    filename = "usrfiles/%s/%s/%s"% (dir[0], dir[0], self.request.files["imgFile"][0]["filename"])
                    logging.info(filename)
                    if not os.path.exists(os.path.dirname(filename)):
                        os.makedirs(os.path.dirname(filename))
                        
                    blah = open(filename, "w")
                    blah.write(self.request.files['imgFile'][0]['body'])
                    blah.close()
                    imgUrl = "%s/%s/%s/%s"% ("http://flow.robhemsley.webfactional.com/imgdata", dir[0], dir[0], self.request.files["imgFile"][0]["filename"])
                    
                    object.create_target(imgHeight, imgWidth, imgUrl)
                else:
                    object.update_target(imgHeight, imgWidth, imgUrl)
    
            if dir[1] == "objImageDelete":
                object = flowDbController.update_object(dir[0])
                object.delete_target(self.get_argument("imgUrl"))
                
            if dir[1] == "objDelete":
                object = flowDbController.update_object(dir[0])
                object.delete_object()
                
            if dir[1] == "objInputUpdate":
                object = flowDbController.update_object(dir[0])
                try:
                    action = str(self.get_argument("action")).upper()
                except:
                    action = ""
                
                try:
                    body = str(self.get_argument("body")).upper()
                except:
                    body = ""

                try:
                    interId = str(self.get_argument("interId")).upper()
                except:
                    interId = "" 
                      
                object.update_interface("input", action, body, interId)
                
            if dir[1] == "objOutputUpdate":
                object = flowDbController.update_object(dir[0])
                
                try:
                    action = str(self.get_argument("action")).upper()
                except:
                    action = ""
                
                try:
                    body = str(self.get_argument("body")).upper()
                except:
                    body = ""

                try:
                    interId = str(self.get_argument("interId")).upper()
                except:
                    interId = ""   
                                
                object.update_interface("output", action, body, interId)
        
            if dir[1] == "objDeleteInterface":
                object = flowDbController.update_object(dir[0])
                object.delete_interface(self.get_argument("interId"))
                
        else:
            if dir[0] == "addObj":
                newObj = flowDbController.create_object()
                newObj.create_object("", self.get_argument("objTitle"))            
                               
        
class ClientHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("flow_client.html")

class FlowSocketHandler(tornado.websocket.WebSocketHandler):
    _deviceID = None
    _deviceUUID = None

    def allow_draft76(self):
        return True

    def open(self):
        while True:
            id = uuid.uuid4()
            if id not in _clients: 
                self._deviceUUID = id
                _clients[self._deviceUUID] = self
                break
                
    def on_close(self):
        del _clients[self._deviceUUID]
        if self._deviceID != None:
            del _clientsIds[self._deviceID]
        print_stats();

    def on_message(self, message):
        logging.info("got message %r", message)
        parsed = tornado.escape.json_decode(message)
        
        process(self, parsed)
        print_stats();

if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = Application()
    #app.listen(options.port)
    app.listen(19708)
    tornado.ioloop.IOLoop.instance().start()