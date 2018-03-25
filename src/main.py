
import sys
import argparse
from pathlib import Path

# my imports
import newdata
import Db


#from: https://chase-seibert.github.io/blog/2014/03/21/python-multilevel-argparse.html
class CmdLineParser(object):
    
    def __init__(self, worker):
        self.e = worker
        
        cmds = ["list-files", "list-objects", "ingest", "get-object", "get-timeslice"]
        parser = argparse.ArgumentParser(
            description = "Manages labeled video data",
            usage       =  "".join(sys.argv[0]) + ''' <command> [<args>]

The commands available are:
   list-files       list all ingested video files
   list-objects     list all ingested objects   
   ingest           ingest video and accompanying csv file
   get-object       search by object name in all video files
   get-timeslice    search by time in specified video file        
            ''')
                
        parser.add_argument("command", choices=cmds)
        args = parser.parse_args(sys.argv[1:2])
        
        cmd = args.command.replace("-", "_")
        
        if (args.command in cmds):        
            getattr(self,cmd)()
        
    def list_files(self):
        self.e.list_videos()
        
    def list_objects(self):
        self.e.list_classes()        
    
    def ingest(self):
        parser = argparse.ArgumentParser (description = "ingest new video and csv files",
                                          usage = " ".join(sys.argv[0:2]) + " video-file csv-file")
        
        parser.add_argument("video_file",   help = "video file path", metavar = "video-file")
        parser.add_argument("-c",  help = "csv file path (optional, default: video-file.csv)", dest = "csv_file", metavar = "csv-file")
        parser.set_defaults(csv_file=None)

        args = parser.parse_args(sys.argv[2:])
        
        print ("ingesting %s   ...burp!" % args.video_file)        
        self.e.process_csv_file(args.csv_file, args.video_file)
        
    def get_object(self):
        parser = argparse.ArgumentParser (description = "search for specific objects in all files",
                                          usage = " ".join(sys.argv[0:2]) + " <options>")

        parser.add_argument("object_class", help = "the type of object to find", metavar = "object-name")
        
        parser.add_argument("-n", help = "don't annotate the output", dest = 'a', action = 'store_false')
        parser.set_defaults(a=True)

        parser.add_argument("-v", help = "view the video as we process it (slow...)", dest = 'display', action = 'store_true')
        parser.set_defaults(display=False)
        
        
        parser.add_argument("-o", help = "output directory", dest = "od", metavar = "out-dir")
        parser.set_defaults(od="")
        
        args = parser.parse_args(sys.argv[2:])
        
        if (Path(args.od).is_dir() == False):
            print("error: output directory does not exist")
            return
        
   
        print ("searching by object")                
        self.e.find_all_objects(args)
        
        
    def get_timeslice(self):
        
        parser = argparse.ArgumentParser (description = "search by time",
                                          usage = " ".join(sys.argv[0:2]) + " <options>")

        parser.add_argument("video_name", help = "the video to use for time based searching", metavar = "video-name")
        parser.add_argument("start_time", help = "the start time (in seconds) to start searching from", type = int, metavar = "start-time")
        parser.add_argument("end_time",   help = "the end time (in seconds) to search upto", type = int, metavar = "end-time")
        
        parser.add_argument("-n", help = "don't annotate the output", dest = 'a', action = 'store_false')
        parser.set_defaults(a=True)

        parser.add_argument("-d", help = "view the video as we process it (slow...)", dest = 'display', action = 'store_true')
        parser.set_defaults(display=False)
                
        parser.add_argument("-o", help = "output directory", dest = "od", metavar = "output-directory")
        parser.set_defaults(od="")        
        
        args = parser.parse_args(sys.argv[2:])
        
        print ("searching by time...")        
        self.e.get_time_slice(args)
        
  
CmdLineParser(newdata.Executor(Db.DbQuery()))


