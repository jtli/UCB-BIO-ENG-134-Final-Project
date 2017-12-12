import time
import picamera
import numpy as np
#turns out matplotlib doesn't really work, making debugging hard
#import matplotlib.pyplot as plt

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
        if temp>maximum:
            maximum = temp
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

#Essentially, it finds the midpoints of the two horizontal lines of the box (since the box could be trapezoidal or parellelogram if the camera is tilted)
#and then assuming the pH boxes are at least somewhere in the middle, it will take the pixel value along that line based on the relative position from the top.
pH1 = output[round(midTx+midx/9),round(midTy+midy/9)]
pH2 = output[round(midTx+midx*0.1944),round(midTy+midy*0.1944)]
pH3 = output[round(midTx+midx*0.289),round(midTy+midy*0.289)]
pH4 = output[round(midTx+midx*0.378),round(midTy+midy*0.378)]

print ("pH strip positioning done")
print ("pH boxes")
print (pH1)
print (pH2)
print (pH3)
print (pH4)

#if you see pH = 24, something went wrong
estimatedpH = 24
#complicated pH comparison time


if pH3[1]>pH3[0]:
    #then pH<10
    if pH2[0]>pH2[1] and pH2[0]>pH2[2]:
        #then pH<7
        if pH1[2]*1.3>pH1[1] and pH1[2]*1.3>pH1[0]:
            #pH between 5 and 7
            rgRatio = (0+pH2[0])/pH2[1]
            if rgRatio>1.08:
                estimatedpH = 6 - (rgRatio-1.08)/0.114
            else:
                estimatedpH = 6 + (1.08-rgRatio)/0.275
        else:
            rbRatio = (0+pH1[0])/pH1[2]
            if rbRatio<2.55:
                #between 3 and 5
                if rbRatio>2.15:
                    estimatedpH = 4 - (rbRatio-2.15)/0.27
                else:
                    estimatedpH = 4 + (2.15-rbRatio)/1.06
            else:
                #between 0 and 3
                rgRatio = (0+pH1[0])/pH1[1]
                if rgRatio>1.63:
                    estimatedpH = 1
                    #cell culture shouldn't be this acidic anyways, so not much work is done here
                if rgRatio>1.3:
                    estimatedpH = 1+(1.63-rgRatio)/0.33
                else:
                    #between 2 and 3
                    estimatedpH = 2 + (3.97-rbRatio)/1.55
    elif pH2[1]>pH2[0] and pH2[1]>pH2[2]:
        #then pH between 6 and 10
        rbRatio = (0+pH2[0])/pH2[2]
        if rbRatio>1.1:
            #between 6 and 8
            rgRatio = (0+pH2[0])/pH2[1]
            if rgRatio>0.807:
                estimatedpH = 7 - (rgRatio-0.807)/0.275
            else:
                estimatedpH = 7 + (0.807-rgRatio)/0.315
        else:
            #between 8 and 10
            if rbRatio>0.5:
                estimatedpH = 8 + (0.949-rbRatio)/0.449
            else:
                estimatedpH = 9 + (0.5-rbRatio)/0.118
    else:
        #assume also that pH between 6 and 10
        rbRatio = (0+pH2[0])/pH2[2]
        if rbRatio>1.1:
            #between 6 and 8
            rgRatio = (0+pH2[0])/pH2[1]
            if rgRatio>0.807:
                estimatedpH = 7 - (rgRatio-0.807)/0.275
            else:
                estimatedpH = 7 + (0.807-rgRatio)/0.315
        else:
            #between 8 and 10
            if rbRatio>0.5:
                estimatedpH = 8 + (0.949-rbRatio)/0.449
            else:
                estimatedpH = 9 + (0.5-rbRatio)/0.118
else:
    #then pH>9
    #assumes linearish relationship
    rgRatio = (0+pH4[0])/pH4[1]
    if rgRatio>6:
        #in the 13 or 14 range
        estimatedpH = 13 + (rgRatio-6.0)/5.0
    elif rgRatio>2.86:
        estimatedpH = 12 + (rgRatio-2.86)/3.19
    elif rgRatio>1.76:
        estimatedpH = 11 + (rgRatio-1.76)/1.1
    elif rgRatio>1.5:
        estimatedpH = 10 + (rgRatio-1.5)/0.26
    else:
        rgRatio = (0+pH3[0])/pH3[1]
        estimatedpH = 10 - (1.78-rgRatio)/0.91
    


print (" ")
print ("estimated pH")
print (estimatedpH)

