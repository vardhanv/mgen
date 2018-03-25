


import sys
import argparse

# my imports
import newdata
import Db


#from: https://chase-seibert.github.io/blog/2014/03/21/python-multilevel-argparse.html
class CmdLineParser(object):
    
    def __init__(self, worker):
        self.e = worker
        
        cmds = ["list", "ingest", "searchObj", "searchTime"]
        parser = argparse.ArgumentParser(
            description = "Manages labeled video data",
            usage       =  "".join(sys.argv[0]) + ''' <command> [<args>]

The commands available are:
   list             list all ingested video files
   ingest           ingest video and accompanying csv file
   searchObj        search by class-name nad object-id in all video files
   searchTime       search by time in specified video file        
            ''')
                
        parser.add_argument("command", choices=cmds)
        args = parser.parse_args(sys.argv[1:2])
        
        if (args.command in cmds):        
            getattr(self,args.command)()
        
    def list(self):
        self.e.listVideos()
    
    def ingest(self):
        parser = argparse.ArgumentParser (description = "ingest new video and csv files",
                                          usage = " ".join(sys.argv[0:2]) + " video-file csv-file")
        
        parser.add_argument("video_file", help = "video-file path")
        parser.add_argument("--csv_file",   help = "csv-file path")
        parser.set_defaults(csv_file=None)

        args = parser.parse_args(sys.argv[2:])
        
        print ("ingesting...burp!")        
        self.e.process_csv_file(args.csv_file, args.video_file)
        
    def searchObj(self):
        parser = argparse.ArgumentParser (description = "search for classes of objects and specific objects",
                                          usage = " ".join(sys.argv[0:2]) + " <options>")

        parser.add_argument("object_class", help = "the type of object to find")
        
        parser.add_argument("-n", help = "don't annotate the output", dest = 'a', action = 'store_false')
        parser.set_defaults(a=True)

        parser.add_argument("-d", help = "view the video as we process it (slow...)", dest = 'display', action = 'store_true')
        parser.set_defaults(display=False)
        
        
        parser.add_argument("-o", help = "output directory", dest = "od")
        parser.set_defaults(od="")
        
        args = parser.parse_args(sys.argv[2:])
   
        print ("searching by object")                
        self.e.find_all_objects(args)
        
        
    def searchTime(self):
        
        parser = argparse.ArgumentParser (description = "search by time",
                                          usage = " ".join(sys.argv[0:2]) + " <options>")

        parser.add_argument("video_name", help = "the video to use for time based searching")
        parser.add_argument("start_time", help = "the start-time (in seconds) to start searching from", type = int)
        parser.add_argument("end_time",   help = "the end-time (in seconds) to search upto", type = int)
        
        parser.add_argument("-n", help = "don't annotate the output", dest = 'a', action = 'store_false')
        parser.set_defaults(a=True)

        parser.add_argument("-d", help = "view the video as we process it (slow...)", dest = 'display', action = 'store_true')
        parser.set_defaults(display=False)
                
        parser.add_argument("-o", help = "output directory", dest = "od")
        parser.set_defaults(od="")        
        
        args = parser.parse_args(sys.argv[2:])
        
        print ("searching by time...")        
        self.e.find_time(args)
        
  
CmdLineParser(newdata.Executor(Db.DbQuery()))

test_video_file = "../data/8gANMceD-Ag.mp4"
test_csv_file   = "../data/8gANMceD-Ag.csv"

#newdata.process_csv_file(test_csv_file, test_video_file, db)
#newdata.process_csv_file("../data/L8Q0lJgaUi4.csv", "../data/L8Q0lJgaUi4.mp4", db)
#newdata.process_csv_file("../data/LM5YuzTdBX8.csv", "../data/LM5YuzTdBX8.mp4", db)


#queries.list_all_videos(db)    

#queries.search_by_objects(db, "giraffe")   

#queries.search_by_time(db, "test_video_file",0,0)   

#videos.mark_object_in_video(db,"giraffe", test_video_file)



      