
import csv
import os
import cv2




class Executor(object):
    
    # returns the output file key
    def _ofkey(self, fname):
        vfilename, _ = os.path.splitext(fname)
        return vfilename.split('/')[-1]
       
    def _peak_file_name(self, obj_list):
        copy_list = obj_list
        head = next(copy_list, None)
        if(head != None):
            return head['full_path']
        else:
            return "error" 
        

    def get_rect_coordinates(self, obj, obj_look_ahead, x_max,y_max,frame_count):
        xmin = int(obj['xmin']*x_max)
        ymin = int(obj['ymin']*y_max)
        xmax = int(obj['xmax']*x_max)
        ymax = int(obj['ymax']*y_max)
        
        if( obj_look_ahead != None and 
            obj_look_ahead['object_presence'] == "present" and
            obj["class_name"] == obj_look_ahead["class_name"] and 
            obj["obj_id"] == obj_look_ahead["obj_id"]):
            # interpolating tracking
            
            xmin = int(xmin + frame_count * (obj_look_ahead['xmin']*x_max - obj['xmin']*x_max)/30)
            ymin = int(ymin + frame_count * (obj_look_ahead['ymin']*y_max - obj['ymin']*y_max)/30)
            xmax = int(xmax + frame_count * (obj_look_ahead['xmax']*x_max - obj['xmax']*x_max)/30)
            ymax = int(ymax + frame_count * (obj_look_ahead['ymax']*y_max - obj['ymax']*y_max)/30)
        
        xmin = xmin if xmin > 0 else 0
        ymin = ymin if ymin > 0 else 0
        xmax = xmax if xmax < x_max else int(x_max)
        ymax = ymax if ymax < y_max else int(y_max)        
                
        return ((xmin,ymin), (xmax,ymax))

    def _draw_rectangle(self, obj, annotate, obj_look_ahead, x_max, y_max, frame_count, cv2, frame):
        if(obj["object_presence"] == "present" and annotate == True):
            (Xcord, Ycord) = self.get_rect_coordinates(obj, obj_look_ahead, x_max, y_max, frame_count)
            cv2.rectangle(frame, Xcord, Ycord, (0,255,0), 2)
            return True
        else:
            return False
                                                                                                     
                  

    
    def __init__(self, myDb):
        self.db = myDb
        # read csv file
        self.fieldnames = ("timestamp", "class_name", "object_id", "object_presence", "xmin", "xmax", "ymin", "ymax")
        
    
    def list_videos(self):
        video_list = self.db.list_all_videos()
        for r in video_list:
            print (r['video_file'] + r['ext'])


    def list_classes(self):
        class_list = self.db.find_list_of_classes()
        for r in class_list:
            print (r)


    
    def process_csv_file(self,csvfname, vfname):
    
        # just the filename
        vpath, ext = os.path.splitext(vfname)
        vfilename = self._ofkey(vfname)
        obj_video_table = {
            "video_file" : vfilename,
            "ext"        : ext
            }
        
        if(csvfname == None):
            #print("Warning: csv file has not been specified. Searching for csvfile with same name as video_file")
            csvfname = vpath + ".csv"
                
            
        if (self.db.video_table_update(obj_video_table) == False):
            print ("Warning: ignoring duplicate file")
            return False
                
        with open(csvfname) as csvfile:
            r = csv.DictReader(csvfile, self.fieldnames)
            for row in r:    
                vid = self.db.video_table_find_id(obj_video_table)
                self.db.class_table_insert({
                    "class_name": row["class_name"],
                    "obj_id"    : row['object_id'],
                    "object_presence" : row['object_presence'],
                    "video_id"  :  vid,
                    "full_path" : vfname,
                    "timestamp" : int(row["timestamp"]),
                    "xmin"      :  float(row["xmin"]),
                    "xmax"      :  float(row["xmax"]),
                    "ymin"      :  float(row["ymin"]),
                    "ymax"      :  float(row["ymax"])
                    })
                
                # upsert into unique class_names
                # keeps a list of all the animals seen
                # and the files seen in
                self.db.unique_class_table_update({"class_name": row['class_name'], "video_id" : vid})

                    

    def find_all_objects(self, args):
        myList = self.db.search_by_objects(args.object_class)
        for obj_list in myList:
            if (obj_list.count() != 0 ):
                fn = self._peak_file_name(obj_list)
                print ("Found %d instances of %s in file %s" % (obj_list.count(), args.object_class, fn))
                self.mark_object_in_video(obj_list,args)


    def object_exists_in_time_window(self, obj_list, args):
        new_obj_list = obj_list
        obj = next(new_obj_list, None)
        if (obj != None):
            if (obj['timestamp'] >= args.start_time*1000 and obj['timestamp'] < args.end_time*1000):
                return True
        
        return False
                
        

    def get_time_slice(self,args):
        myList = self.db.find_list_of_classes_in_file(self._ofkey(args.video_name))
        
        atLeastOnce = False        

        for obj_list in myList:            
            if(self.object_exists_in_time_window(obj_list, args)):
                self.mark_oject_in_video_time(args, obj_list)
                atLeastOnce = True
        
        if (atLeastOnce == False):
            self.mark_oject_in_video_time(args, None)
            
        

        
    # for time
    def mark_oject_in_video_time(self, args, obj_list):

        # init
        w = None        
        obj_cls_name = "None"
        obj_processed = False
        obj = None
        frame_count = 0 #for interpolation
        obj_look_ahead = None
        
        
        if (obj_list != None):
            obj_processed = False
            obj = next(obj_list, None)
            frame_count = 0 #for interpolation
            obj_look_ahead = next(obj_list, None)
                
            if (obj != None):
                obj_cls_name = obj["class_name"]
            
        # get the outpuf file name
        of_key = self._ofkey(args.video_name)
        
        if (args.od == ""):
            ofname = "./" + of_key + "-" + obj_cls_name + "-" + str(args.start_time) + "-"  + str(args.end_time) + ".mp4"
        else:
            ofname = args.od + "/" + of_key + "-" + obj_cls_name + "-" + str(args.start_time) + "-"  + str(args.end_time) + ".mp4"            

        print ("Creating new file: %s" % ofname)
        
        
        cap    = cv2.VideoCapture(args.video_name)
        y_max  = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        x_max  = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        fps    = cap.get(cv2.CAP_PROP_FPS)
        #fourcc = cap.get(cv2.CAP_PROP_FOURCC)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')

        frames_available   =  True  
        
        while(frames_available and cap.isOpened()):
            frames_available, frame = cap.read()
                                   
            c_pos = cap.get(cv2.CAP_PROP_POS_MSEC)
                                                          
            if(c_pos >= args.start_time*1000 and c_pos < args.end_time*1000):
                if ( w == None):  # create the writer           
                    w = cv2.VideoWriter(ofname, int(fourcc), int(fps), (int(x_max),int(y_max)))
                    
                if(obj != None and args.a == True):
                    if(c_pos < obj['timestamp']):
                        True # Do nothing   
                    elif(c_pos >= obj['timestamp'] and c_pos < obj['timestamp']+1000 ):
                        if(self._draw_rectangle(obj, args.a, obj_look_ahead, x_max, y_max, frame_count, cv2, frame) == True):
                            frame_count = frame_count + 1                        
                    else :
                        obj_processed = True
                                            
                    if (obj_processed == True):
                        prev_obj = obj
                        obj = obj_look_ahead
                        obj_look_ahead = next(obj_list, None)
                        frame_count = 0
                        obj_processed = False
                        if(obj == None or ( \
                                            obj["class_name"] == prev_obj["class_name"] and 
                                            obj["obj_id"] == prev_obj["obj_id"] and \
                                            obj["timestamp"] == prev_obj["timestamp"] + 1000) == False):
                            # Nothing to do
                            True
                    
                w.write(frame)
                
                if (args.display == True):
                    cv2.imshow("Viewer", frame)                        
                    if (cv2.waitKey(1) & 0xFF == ord('q')):
                        break
            
            elif (c_pos >= args.end_time * 1000): 
                #print ("Closing file...")                
                w.release()
                ofname = None
                break
                                                            
                    
        # shutdown processes
        if(w != None):
            # close any open files
            w.release()
            ofname = None
            
        cap.release()
        cv2.destroyAllWindows()
        
        return
        
    # for by object search
    def mark_object_in_video(self, obj_list, args):


        ofname = None
        obj_processed = False
        obj  = None
        frame_count = 0 #for interpolation
        obj_look_ahead = None
        
        
        if (obj_list != None):
            obj_processed = False
            obj = next(obj_list, None)
            frame_count = 0 #for interpolation
            obj_look_ahead = next(obj_list, None)

        
        if(obj == None):
            return 

        # just the filename
        vfilename, _ = os.path.splitext(obj["full_path"])
        of_key = vfilename.split('/')[-1]
        
        cap    = cv2.VideoCapture(obj["full_path"])
        y_max  = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        x_max  = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        fps    = cap.get(cv2.CAP_PROP_FPS)
        #fourcc = cap.get(cv2.CAP_PROP_FOURCC)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        
                
    
        while(cap.isOpened()):
            _, frame = cap.read()
            
            assert(obj != None)
                
            c_pos = cap.get(cv2.CAP_PROP_POS_MSEC)
            
            '''
            if(c_pos % 1000 == 0):
                print ("current frame time: %d" % c_pos)
                print ("Object %s is %s at time %d" % (obj["class_name"], obj['object_presence'], obj["timestamp"]))
            '''
            
            if (c_pos < obj['timestamp']):

                if (args.display == False):
                    # seek to position
                    seek_pos = int(obj['timestamp']/(1000/fps))
                    cap.set(cv2.CAP_PROP_POS_FRAMES, seek_pos)
                
            elif(c_pos >= obj['timestamp'] and c_pos < obj['timestamp']+1000):

                if(self._draw_rectangle(obj, args.a, obj_look_ahead, x_max, y_max, frame_count, cv2, frame) == True):
                    frame_count = frame_count + 1
                                
                # Start creating the video segments
                if(ofname == None): 
                    if (args.od == ""):
                        ofname = "./" + of_key + "-" + obj["class_name"] + "-" + str(obj["obj_id"]) + "-" + str(obj["timestamp"]) + ".mp4"
                    else:
                        ofname = args.od + "/" + of_key + "-" + obj["class_name"] + "-" + str(obj["obj_id"]) + "-" + str(obj["timestamp"]) + ".mp4"            
                                                           
                    print ("Creating new file: %s" % ofname)
                    w = cv2.VideoWriter(ofname, int(fourcc), int(fps), (int(x_max),int(y_max)))
                    w.write(frame)
                else:
                    assert(w != None)
                    w.write(frame)
                                                                             
            else :
                obj_processed = True
                    
                
            if (obj_processed == True):
                prev_obj = obj
                obj = obj_look_ahead
                obj_look_ahead = next(obj_list, None)
                frame_count = 0
                obj_processed = False
                if(obj == None or ( \
                                    obj["class_name"] == prev_obj["class_name"] and 
                                    obj["obj_id"] == prev_obj["obj_id"] and \
                                    obj["timestamp"] == prev_obj["timestamp"] + 1000) == False):
                    #print ("Closing file...")
                    # Not a contiguous object, close the video-writer
                    w.release()
                    ofname = None
                                            
        
            if (args.display == True):
                cv2.imshow("Viewer", frame)                        
                if (cv2.waitKey(1) & 0xFF == ord('q')):
                    break
            
            if (obj == None):
                #this file has been fully processed, exit
                break
    
        
        # shutdown processes
        if(ofname != None):
            # close any open files
            w.release()
            ofname = None
            
        cap.release()
        cv2.destroyAllWindows()
        
        return

