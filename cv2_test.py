# import the opencv library
import cv2
import mediapipe as mp
import time
  
HAND_LANDMARKS = [0, 4, 8, 12, 16, 20]
# define a video capture object
vid = cv2.VideoCapture(0)
mpHands = mp.solutions.hands
# https://google.github.io/mediapipe/solutions/hands.html 
hands = mpHands.Hands() #default params

#method from MP 
mpDraw = mp.solutions.drawing_utils

pTime = 0 # previous time
cTime = 0 # current time

while(True):
      
    # Capture the video frame
    # by frame
    ret, frame = vid.read()
    imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  #inverts our imagee
    results = hands.process(imgRGB)
    #print(results.multi_hand_landmarks) # detects hand information

    #open up the results to extract the information 
    if results.multi_hand_landmarks:
      for hand_landmark in results.multi_hand_landmarks: #21 points (landmarks) 
        for id, lm in enumerate(hand_landmark.landmark):
          # print(id, lm) #20 x: 0.4845593571662903 y: -0.0872521698474884 z: -0.21339912712574005
          h, w, c = frame.shape
          cx, cy = int(lm.x * w), int(lm.y * h) #convert into pixel values
          print(id, cx, cy) 
          # important landmarks are 0, 

          if id in HAND_LANDMARKS: #first landmark 
            cv2.circle(frame, (cx, cy), 15, (255, 0, 255), cv2.FILLED)
        #mpHands.HAND_CONNECTIONS = the lines between landmarks
        mpDraw.draw_landmarks(frame, hand_landmark, mpHands.HAND_CONNECTIONS)

    # code of time and frames per second
    cTime = time.time()
    fps = 1/(cTime - pTime)
    pTime = cTime
    #Put frames onto our video stream
    cv2.putText(frame, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)
    
    # display the resulting frame
    cv2.imshow('frame', frame)
      
    # press q to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
  
# After the loop release the cap object
vid.release()
# Destroy all the windows
cv2.destroyAllWindows()