import time
import picamera
import numpy as np
#turns out matplotlib doesn't really work, making debugging hard
#import matplotlib.pyplot as plt

#the code was adapted from the pH strip, which is a harder problem.
#thus, some variables still say pH1, although this is actually the value of the glucose, not pH

camera = picamera.PiCamera()
camera.resolution = (640,480)
time.sleep(2)
output = np.empty((480, 640, 3), dtype=np.uint8)
camera.capture('output.png')
camera.capture(output, 'rgb')
print ("End capture")

def totalPixelSum(x):
    return 0+x[0]+x[1]+x[2]
x=0
y=0
minimum = 255*3
maximum = 0
temp = 0
while (x<480):
    while (y<640):
        temp = totalPixelSum(output[x,y])
        if temp<minimum:
            minimum = temp
            #print ("Min coordinates"+str(x)+","+str(y)+","+str(temp))
        if temp>maximum:
            maximum = temp
            #print ("Max coordinates"+str(x)+","+str(y)+","+str(temp))
        y=y+2
    x=x+2
    y=0

print ("done min/max")

#top left corner finding for left(pH strip) box
x=0
y=0
ctlx=0
ctly=0
temp = 0
cornerTL = True
while (x<480):
    #200 to save on runtime
    while (y<200):
        temp = totalPixelSum(output[x,y])
        if temp<(minimum*1.2+15):
            ctlx=x
            ctly=y
            if totalPixelSum(output[x+5,y+5])<(minimum*1.2+25):
                cornerTL = True
            x=480
            break
        y=y+1
    x=x+1
    y=0
if not cornerTL:
    print("not top left corner, picture probably too rotated. Fix by rotating sample clockwise")
else:
    #find bottom left corner of pH strip box
    x=479
    y=0
    cblx=0
    cbly=0
    temp = 0
    cornerBL = True
    while (x>0):
        #200 to save on runtime
        while (y<200):
            temp = totalPixelSum(output[x,y])
            if temp<(minimum*1.2+15):
                cblx=x
                cbly=y
                if totalPixelSum(output[x-5,y+5])<(minimum*1.2+25):
                    cornerBL = True
                x=0
                break
            y=y+1
        x=x-1
        y=0
    if not cornerBL:
        print("not bottom left corner, picture probably too rotated.")
    else:
        #finding top right corner
        x=ctlx+10
        y=ctly+10
        ctrx=0
        ctry=0
        temp = 0
        while (y<200):
            temp = totalPixelSum(output[x,y])
            if temp>(minimum*1.2+30):
                ctry=y
                while (x>0):
                    temp = totalPixelSum(output[x,y-10])
                    if temp>(minimum*1.2+30):
                        ctrx = x
                        break
                    x=x-1
                break
            y=y+1

        #finding bottom right corner
        x=cblx-10
        y=cbly+10
        cbrx=0
        cbry=0
        temp = 0
        while (y<200):
            temp = totalPixelSum(output[x,y])
            if temp>(minimum*1.2+30):
                cbry=y
                while (x<480):
                    temp = totalPixelSum(output[x,y-10])
                    if temp>(minimum*1.2+30):
                        cbrx = x
                        break
                    x=x+1
                break
            y=y+1

midTx = (ctlx+ctrx)/2.0
midTy = (ctly+ctry)/2.0
midBx = (cblx+cbrx)/2.0
midBy = (cbly+cbry)/2.0
midx = midBx-midTx
midy = midBy-midTy

#pH boxes ordered from top to bottom
#actual position proportions found via ruler
pH1 = output[round(midTx+midx/9),round(midTy+midy/9)]

print ("glucose strip positioning done")
print (pH1)

#glucose concentration determination time
glucose = 1000
rgRatio = (0+pH1[0])/pH1[1]
rbRatio = (0+pH1[0])/pH1[2]

if rgRatio<1.15:
    #between 0 and 5
    if rbRatio<1.286:
        glucose = max(1-(1.286-rbRatio)/0.286,0)
    elif rbRatio<1.836:
        glucose = 2.5-(1.836-rbRatio)/0.3667
    else:
        glucose = 2.5+(rbRatio-1.836)/0.1596
else:
    #greater than 5
    if rgRatio<1.33:
        glucose = 5+(rgRatio-1.15)/0.036
    else:
        glucose = 10+(rgRatio-1.33)/0.022
    

print ("glucose:")
print (glucose)


