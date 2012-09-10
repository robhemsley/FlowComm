'''
Created on Sep 7, 2012

@author: Rob
'''
import facebook, json, os 

from StateImage import StateImage

class fb_test():
    graph = None
    
    def __init__(self, id):
        self.graph = facebook.GraphAPI(id)

        
    def add_picture(self, file_name, img_des, album_name, album_msg, ):                
        id = self.get_album_id(album_name)
        if id == None:
            self.graph.request("me/albums", post_args = {"name": album_name, "message": album_msg})
            id = self.get_album_id(album_name)
        
        self.graph.put_photo(open(file_name), img_des, id)
        
    def get_album_id(self, name):
        profile = self.graph.get_object("me/albums")
        for value in profile["data"]:
            if value["name"] == name:
                return value["id"]
            
        return None
    
    def get_photos(self, album_name):
        id = self.get_album_id(album_name)
        return self.graph.request(id+"/photos/")
    
    def delete_photo(self, album_name, photo_name):
        id = self.get_album_id(album_name)
        for data in self.graph.request(id+"/photos/")["data"]:
            if data["name"] == photo_name:
                self.graph.delete_object(data["id"])    
                
    def delete_album(self, albumName):
        id = self.get_album_id(albumName)
        self.graph.delete_object(id)   
                
def setupDemo():
    test = fb_test("AAACEdEose0cBAAu3eL0wVZBCULpmtYyuIiTl0xKZB5p9Fk4JuzuXPZAEXyyZCoiAhGEwEruUqNaQR300ZAcYjIFhybt3MhbqHQWTBTDrj2hDaBx6mZAQXd")
    albumName = "Name"
    albumDes = "album description"
    
    for images in os.listdir("images"):
        fullPath = os.path.abspath("images/"+images)
        tmp = StateImage(fullPath)
        for i in tmp.cropImage("img_states/%s"% (images.split(".")[0]), 2, 2):   
            print i
                 
        #test.add_picture(fullPath, images.split(".")[0], albumName, albumDes)
    
    for img in test.get_photos("Name")["data"]:
        print img
        #test.delete_photo("Name", img["name"])
        
    print test.get_photos("Name")
    #test.delete_photo("Name", "Test image upload")
    
if __name__ == '__main__':
    setupDemo()