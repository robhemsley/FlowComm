import os, sys, webbrowser, json, time, copy, hashlib, tempfile, popen2, urllib2, subprocess

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *

global webView
    
if sys.platform == 'darwin':
    def openFolder(path):
        subprocess.check_call(['open', '--', path])
elif sys.platform == 'linux2':
    def openFolder(path):
        subprocess.check_call(['gnome-open', '--', path])
elif sys.platform == 'windows':
    def openFolder(path):
        subprocess.check_call(['explorer', path])
        
class FlowMsg:
    msg = None
    
    def __init__(self, msg = None):
        if msg == None:
            msg = {"to": "", "from": "", "action": "", "hash": "", "body": "", "status": "", "timestamp": "", "msgId": random.randint(0,999999)}
        elif not isinstance(msg, dict):
            msg = str(msg).strip()
            jsonMsg = {}
            try:
                jsonMsg = json.loads(msg)
            except ValueError:
                pass
            self.msg = jsonMsg
        
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
    

class CustomWebView(QWebView):
    def __init__(self, parent = None):
        QWebView.__init__(self, parent)
        
    def createWindow(self, webWindowType):
        self.view = CustomWebView()
        self.view.show()
        return self.view
    
class OpenHandler(QObject):
    def __init__(self, parent=None):
        super(OpenHandler, self).__init__(parent)

    @pyqtSlot(str)
    def process(self, message):
        print str(message)
        tmp = FlowMsg(message)
        webbrowser.open_new(tmp.get_body())
        
class PrintHandler(QObject):
    def __init__(self, parent=None):
        super(PrintHandler, self).__init__(parent)

    @pyqtSlot(str)
    def process(self, message):
        print str(message)
        tmp = FlowMsg(message)
        
        f = urllib2.urlopen(tmp.get_body())
        data = f.read()
        outputfile = tempfile.gettempdir()+"/"+tmp.get_body().split('/')[-1]
        with open(outputfile, "wb") as code:
            code.write(data)
        
        popen2.popen2(["lpr", "-P", 'ecopress_media_mit_edu', outputfile])
        
class CopyHandler(QObject):
    def __init__(self, parent=None):
        super(CopyHandler, self).__init__(parent)

    @pyqtSlot(str)
    def process(self, message):
        print str(message)
        tmp = FlowMsg(message)
        
        f = urllib2.urlopen(tmp.get_body())
        data = f.read()
        
        
        outputDir = os.path.join(os.path.expanduser("~"), "Flow")
        if not os.path.exists(outputDir):
            os.makedirs(outputDir)
            
        outputfile = outputDir+"/"+tmp.get_body().split('/')[-1]
        with open(outputfile, "wb") as code:
            code.write(data)
        
        openFolder(outputDir)




def main():
    global webView

    app = QApplication(sys.argv)

    webView = CustomWebView()
    webView.settings().setAttribute(QWebSettings.JavascriptEnabled, True)
    webView.settings().setAttribute(QWebSettings.JavascriptCanOpenWindows, True)
    webView.settings().setAttribute(QWebSettings.JavascriptCanAccessClipboard, True)
    
    webView.loadFinished.connect(addHandlers)
    webView.load(QUrl("http://127.0.0.1:9000/client"))
    
    window = QMainWindow()
    window.setCentralWidget(webView)
    window.show()    

    sys.exit(app.exec_())
    
def addhandler(handler, handlerName, action):
    webView.page().mainFrame().addToJavaScriptWindowObject(handlerName, handler)
    webView.page().mainFrame().evaluateJavaScript("flowConnector.addHandler('"+action+"', "+handlerName+".process, true);");
    
def addHandlers():
    addhandler(OpenHandler(), "openHandler", "OPEN")    
    addhandler(PrintHandler(), "printHandler", "PRINT")
    addhandler(CopyHandler(), "copyHandler", "COPY")

if __name__ == "__main__":
    main()

