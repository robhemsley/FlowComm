
import MySQLdb
import MySQLdb.cursors 

class flowDb:
    db = None
    cur = None
    localDb = False;
    
    def __init__(self):
        self._connect()
            
    def _connect(self):
        if self.localDb == False:
            self.db = MySQLdb.connect(host='robhemsley.webfactional.com',
                                      user='robhemsley_flow',
                                      passwd='wgpmilo1988',
                                      db='robhemsley_flow',
                                      cursorclass = MySQLdb.cursors.DictCursor)
        else:
            self.db = MySQLdb.connect(host='127.0.0.1',
                                      user='root',
                                      passwd='',
                                      db='robhemsley_flow',
                                      cursorclass = MySQLdb.cursors.DictCursor)
        
                
    def get_object(self, obj_id):
        if not self.db.open: self._connect()
        return dbObject(self.db, obj_id)
    
    def get_all_objects(self):
        if not self.db.open: self._connect()
        output = {}
        cur = self.db.cursor()
        cur.execute("SELECT * FROM object")
        for object in cur:
            output[object["id"]] = self.get_object(object["id"])
            
        return output    
    
    def add_user(self):
        if not self.db.open: self._connect()
        pass
    
    def get_user(self):
        if not self.db.open: self._connect()
        pass
    
    def create_object(self):
        if not self.db.open: self._connect()
        return dbObject(self.db)
    
    def update_object(self, obj_id):
        if not self.db.open: self._connect()
        return dbObject(self.db, obj_id)

class dbObject:
    cur = None
    obj_id = None
    db = None
    obj_json_details = None
    
    def __init__(self, db, obj_id = 0):
        self.db = db
        self.cur = db.cursor()
        self.obj_id = str(obj_id)

    def create_interface(self, type, action, body):
        self.cur.execute("INSERT INTO interface (`obj_id`, `type`, `action`, `body`) VALUES (%s, \"%s\", \"%s\", \"%s\")"% (self.obj_id, type, action, body))
        self.db.commit()
        
    def update_interface(self, type, action, body, id):
        self.cur.execute("UPDATE interface SET `obj_id`=%s, `type`=\"%s\", `action`=\"%s\", `body`=\"%s\" WHERE `id`=%s"% (self.obj_id, type, action, body, id))
        self.db.commit()
        
    def delete_interface(self, id):
        self.cur.execute("DELETE FROM interface WHERE `id`=%s"% (id))
        self.db.commit()
    
    def create_target(self, height, width, url):
        self.cur.execute("INSERT INTO img_target (`obj_id`, `url`, `width`, `height`) VALUES (%s, \"%s\", %s, %s)"% (self.obj_id, url, width, height))
        self.db.commit()
        
    def update_target(self, height, width, url = None):
        if url == None:
            self.cur.execute("UPDATE img_target SET `obj_id`=\"%s\", `width`=\"%s\", `height`=\"%s\" WHERE `obj_id`=%s AND `url`=\"%s\""% (self.obj_id, width, height, self.obj_id, url))
        else:    
            self.cur.execute("UPDATE img_target SET `obj_id`=\"%s\", `url`=\"%s\", `width`=\"%s\", `height`=\"%s\" WHERE `obj_id`=%s AND `url`=\"%s\""% (self.obj_id, url, width, height, self.obj_id, url))
        self.db.commit()
    
    def create_object(self, details, title):
        self.cur.execute("INSERT INTO object (`details`, `title`) VALUES (\"%s\", \"%s\")"% (details, title))
        self.db.commit()
        self.obj_id = self.cur.lastrowid
        return self.obj_id
    
    def update_object(self, details, title):    
        self.cur.execute("UPDATE object SET `details`=\"%s\", `title`=\"%s\" WHERE `id`=%s"% (details, title, self.obj_id))
        self.db.commit()
        
    def delete_target(self, url):
        self.cur.execute("DELETE FROM img_target WHERE `obj_id`=%s AND `url`=\"%s\""% (self.obj_id, url))
        self.db.commit()
        
    def delete_object(self):
        self.cur.execute("DELETE FROM img_target WHERE `obj_id`=%s"% (self.obj_id))
        self.cur.execute("DELETE FROM interface WHERE `obj_id`=%s"% (self.obj_id))
        self.cur.execute("DELETE FROM object WHERE `id`=%s"% (self.obj_id))
        self.db.commit()

    def get_object_details(self):
        output = {}
        self.cur.execute("SELECT * FROM object WHERE `object`.`id` = %s"% (self.obj_id))
        output = self.cur.fetchall()
        if len(output) == 0:
            return None
        output = output[0]
        self.cur.execute("SELECT * FROM interface WHERE `interface`.`obj_id` = %s"% (self.obj_id))
        output["interface"] = list(self.cur.fetchall())
        
        self.cur.execute("SELECT * FROM img_target WHERE `img_target`.`obj_id` = %s"% (self.obj_id))
        output["targetImgs"] = list(self.cur.fetchall())
        
        return output

    def process_object(self):
        if self.obj_json_details == None:
            obj = self.get_object_details()
            if obj == None:
                obj_out = {"id": self.obj_id, "details": "", "title": "", "interfaces": {}, "targetImgs": {}}
            else:
                obj_out = {"id": obj["id"], "details": obj["details"], "title": obj["title"]}
                interface = {}
                target_imgs = []
                for inter in obj["interface"]:
                    if inter["type"] not in interface:
                        interface[inter["type"]] = {}
                        
                    interface[inter["type"]][inter["id"]] = {"action": inter["action"], "body": inter["body"]}
                    
                for img in obj["targetImgs"]:
                     target_imgs.append({"imgUrl": img["url"], "width": img["width"], "height": img["height"]})
                     
                obj_out["interfaces"] = interface
                obj_out["targetImgs"] = target_imgs
                self.obj_json_details = obj_out
        else:
            obj_out = self.obj_json_details
        return obj_out

if __name__ == "__main__":
    flowDbController = flowDb()
    print flowDbController.get_all_objects()
    
    #Creates some basic objects
    """eco_tv = flowDbController.create_object()
    eco_tv.create_object("Info Eco TV")
    eco_tv.create_interface("output", "OPEN", "Something here not sure what")
    eco_tv.create_target("http://www.robhemsley.co.uk/share/img/laptop.jpg", 35.5, 21)
    print eco_tv.get_object_details()
        
    mean_girls = flowDbController.create_object()
    mean_girls.create_object("Mean Girls DVD")
    mean_girls.create_interface("input", "OPEN", "http://www.youtube.com/watch?v=6YjSIvmNjT8")
    mean_girls.create_target("http://www.robhemsley.co.uk/share/img/meanGirls.jpg", 12.5, 18)
    print mean_girls.get_object_details()"""