
import cv2

test_video_file = "../data/8gANMceD-Ag.mp4"

cap = cv2.VideoCapture(test_video_file)
y_max  = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
x_max  = cap.get(cv2.CAP_PROP_FRAME_WIDTH)

fps    = cap.get(cv2.CAP_PROP_FPS)
fourcc = cap.get(cv2.CAP_PROP_FOURCC)
    
w = cv2.VideoWriter("output.mp4", int(fourcc), int(fps), (int(x_max),int(y_max)))

    

print ("Width = %d" % cap.get(cv2.CAP_PROP_FRAME_WIDTH)) 
print ("Height = %d" % cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
  
while (cap.isOpened()):
    ret, frame = cap.read()
    w.write(frame)
        
    cv2.imshow("Viewer", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    

w.release()
cap.release()
cv2.destroyAllWindows()
 
    
    