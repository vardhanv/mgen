

from pymongo import MongoClient
from bson import ObjectId


class DbQuery(object):
    
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db           = self.client.video_database
        self.vt           = self.db.video_table
        self.cntable      = self.db.class_name_table
        self.u_class      = self.db.unique_class_table
        
        
    def list_all_videos(self):
        return self.vt.find() 

        
    def search_by_objects(self,obj_class):            
        return [self.cntable.find({"class_name" : obj_class, "video_id" : filename['_id']}).sort("timestamp") for filename in self.list_all_videos()]


        
    def search_by_time(self,video_file, start_time, end_time, annotated = False):
        time_slot = self.vt.find( { "video_file" : video_file})
        return
    
    
    def video_table_update(self, obj_to_update):
        if(self.vt.update_one(obj_to_update, { "$set" : obj_to_update } , upsert = True).matched_count > 0):
            return False
        else:
            return True
    
    def unique_class_table_update(self, obj_to_update):
        self.u_class.update_one(obj_to_update, { "$set" : obj_to_update } , upsert = True)


    def video_table_find_id(self, obj):
        return self.vt.find_one(obj)["_id"]


    def find_list_of_classes_in_file_file(self, fkey):
        myId = self.vt.find_one( { "video_file" : fkey})["_id"]
        class_in_file = self.u_class.find({ "video_id" : myId})
        myList = [ self.cntable.find({"class_name" : i["class_name"], "video_id": myId}) for i in class_in_file]
        return myList
        
        
    
    def class_table_insert(self, obj_to_update):
        self.db.class_name_table.insert_one(obj_to_update)

    