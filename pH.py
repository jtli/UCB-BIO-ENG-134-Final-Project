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

startY=max(ctry,cbry)+40

#top left corner finding for right(reference) box
x=0
y=startY
ctlxr=0
ctlyr=0
temp = 0
cornerTL = False
while (x<480):
    #400 to save on runtime
    while (y<400):
        temp = totalPixelSum(output[x,y])
        if temp<(minimum*1.15+20):
            ctlxr=x
            ctlyr=y
            if totalPixelSum(output[x+5,y+5])<(minimum*1.15+35):
                cornerTL = True
            else:
                print (totalPixelSum(output[x+5,y+5]))
                print (minimum*1.15+20)
            x=480
            break
        y=y+1
    x=x+1
    y=startY
if not cornerTL:
    print("not top left corner right, picture probably too rotated. Fix by rotating sample clockwise")
else:
    #find bottom left corner of reference box
    x=479
    y=startY
    cblxr=0
    cblyr=0
    temp = 0
    cornerBL = False
    while (x>0):
        #400 to save on runtime
        while (y<400):
            temp = totalPixelSum(output[x,y])
            if temp<(minimum*1.15+20):
                if (totalPixelSum(output[x,y-15])>(maximum/2)):
                    cblxr=x
                    cblyr=y
                    if totalPixelSum(output[x-5,y+5])<(minimum*1.15+55):
                        cornerBL = True
                    x=0
                break
            y=y+1
        x=x-1
        y=startY
    if not cornerBL:
        print("not bottom left corner right, picture probably too rotated.")
        #for bottom right corner reference
    print ("almost done...")
    x=479
    y=619
    cbrxr=0
    cbryr=0
    temp = 0
    while (x>0):
        #300 to save on runtime
        while (y>300):
            temp = totalPixelSum(output[x,y])
            if temp<(minimum*1.15+20):
                if (totalPixelSum(output[x,y+20])>(maximum/2)):
                    cbrxr=x
                    cbryr=y
                    x=0
                    break
            y=y-1
        x=x-1
        y=619

#total length of 7.8cm x 13.8 cm
#since the reference box may be trapezoidal or a parellelogram, using the relative positions of the bottom line to find the vertical component.
lengthX = (cblxr-ctlxr)/7.8
lengthY = (cbryr-cblyr)/13.8
p01 = output[round((cblxr*(13.8-1.05)+cbrxr*1.05)/13.8-lengthX*1.4),round(cblyr+lengthY*1.05)]
p02 = output[round((cblxr*(13.8-1.05)+cbrxr*1.05)/13.8-lengthX*2.1),round(cblyr+lengthY*1.05)]
p03 = output[round((cblxr*(13.8-1.05)+cbrxr*1.05)/13.8-lengthX*2.75),round(cblyr+lengthY*1.05)]
p04 = output[round((cblxr*(13.8-1.05)+cbrxr*1.05)/13.8-lengthX*3.4),round(cblyr+lengthY*1.05)]

p11 = output[round((cblxr*(13.8-1.75)+cbrxr*1.75)/13.8-lengthX*1.4),round(cblyr+lengthY*1.75)]
p12 = output[round((cblxr*(13.8-1.75)+cbrxr*1.75)/13.8-lengthX*2.1),round(cblyr+lengthY*1.75)]
p13 = output[round((cblxr*(13.8-1.75)+cbrxr*1.75)/13.8-lengthX*2.75),round(cblyr+lengthY*1.75)]
p14 = output[round((cblxr*(13.8-1.75)+cbrxr*1.75)/13.8-lengthX*3.4),round(cblyr+lengthY*1.75)]

p21 = output[round((cblxr*(13.8-2.5)+cbrxr*2.5)/13.8-lengthX*1.4),round(cblyr+lengthY*2.5)]
p22 = output[round((cblxr*(13.8-2.5)+cbrxr*2.5)/13.8-lengthX*2.1),round(cblyr+lengthY*2.5)]
p23 = output[round((cblxr*(13.8-2.5)+cbrxr*2.5)/13.8-lengthX*2.75),round(cblyr+lengthY*2.5)]
p24 = output[round((cblxr*(13.8-2.5)+cbrxr*2.5)/13.8-lengthX*3.4),round(cblyr+lengthY*2.5)]

p31 = output[round((cblxr*(13.8-3.15)+cbrxr*3.15)/13.8-lengthX*1.4),round(cblyr+lengthY*3.15)]
p32 = output[round((cblxr*(13.8-3.15)+cbrxr*3.15)/13.8-lengthX*2.1),round(cblyr+lengthY*3.15)]
p33 = output[round((cblxr*(13.8-3.15)+cbrxr*3.15)/13.8-lengthX*2.75),round(cblyr+lengthY*3.15)]
p34 = output[round((cblxr*(13.8-3.15)+cbrxr*3.15)/13.8-lengthX*3.4),round(cblyr+lengthY*3.15)]

p41 = output[round((cblxr*(13.8-3.9)+cbrxr*3.9)/13.8-lengthX*1.4),round(cblyr+lengthY*3.9)]
p42 = output[round((cblxr*(13.8-3.9)+cbrxr*3.9)/13.8-lengthX*2.1),round(cblyr+lengthY*3.9)]
p43 = output[round((cblxr*(13.8-3.9)+cbrxr*3.9)/13.8-lengthX*2.75),round(cblyr+lengthY*3.9)]
p44 = output[round((cblxr*(13.8-3.9)+cbrxr*3.9)/13.8-lengthX*3.4),round(cblyr+lengthY*3.9)]

p51 = output[round((cblxr*(13.8-4.6)+cbrxr*4.6)/13.8-lengthX*1.4),round(cblyr+lengthY*4.6)]
p52 = output[round((cblxr*(13.8-4.6)+cbrxr*4.6)/13.8-lengthX*2.1),round(cblyr+lengthY*4.6)]
p53 = output[round((cblxr*(13.8-4.6)+cbrxr*4.6)/13.8-lengthX*2.75),round(cblyr+lengthY*4.6)]
p54 = output[round((cblxr*(13.8-4.6)+cbrxr*4.6)/13.8-lengthX*3.4),round(cblyr+lengthY*4.6)]

p61 = output[round((cblxr*(13.8-5.3)+cbrxr*5.3)/13.8-lengthX*1.4),round(cblyr+lengthY*5.3)]
p62 = output[round((cblxr*(13.8-5.3)+cbrxr*5.3)/13.8-lengthX*2.1),round(cblyr+lengthY*5.3)]
p63 = output[round((cblxr*(13.8-5.3)+cbrxr*5.3)/13.8-lengthX*2.75),round(cblyr+lengthY*5.3)]
p64 = output[round((cblxr*(13.8-5.3)+cbrxr*5.3)/13.8-lengthX*3.4),round(cblyr+lengthY*5.3)]

p71 = output[round((cblxr*(13.8-6)+cbrxr*6)/13.8-lengthX*1.4),round(cblyr+lengthY*6)]
p72 = output[round((cblxr*(13.8-6)+cbrxr*6)/13.8-lengthX*2.1),round(cblyr+lengthY*6)]
p73 = output[round((cblxr*(13.8-6)+cbrxr*6)/13.8-lengthX*2.75),round(cblyr+lengthY*6)]
p74 = output[round((cblxr*(13.8-6)+cbrxr*6)/13.8-lengthX*3.4),round(cblyr+lengthY*6)]

p81 = output[round((cblxr*(13.8-8.1)+cbrxr*8.1)/13.8-lengthX*1.4),round(cblyr+lengthY*8.1)]
p82 = output[round((cblxr*(13.8-8.1)+cbrxr*8.1)/13.8-lengthX*2.1),round(cblyr+lengthY*8.1)]
p83 = output[round((cblxr*(13.8-8.1)+cbrxr*8.1)/13.8-lengthX*2.75),round(cblyr+lengthY*8.1)]
p84 = output[round((cblxr*(13.8-8.1)+cbrxr*8.1)/13.8-lengthX*3.4),round(cblyr+lengthY*8.1)]

p91 = output[round((cblxr*(13.8-8.8)+cbrxr*8.8)/13.8-lengthX*1.4),round(cblyr+lengthY*8.8)]
p92 = output[round((cblxr*(13.8-8.8)+cbrxr*8.8)/13.8-lengthX*2.1),round(cblyr+lengthY*8.8)]
p93 = output[round((cblxr*(13.8-8.8)+cbrxr*8.8)/13.8-lengthX*2.75),round(cblyr+lengthY*8.8)]
p94 = output[round((cblxr*(13.8-8.8)+cbrxr*8.8)/13.8-lengthX*3.4),round(cblyr+lengthY*8.8)]

pA1 = output[round((cblxr*(13.8-9.5)+cbrxr*9.5)/13.8-lengthX*1.4),round(cblyr+lengthY*9.5)]
pA2 = output[round((cblxr*(13.8-9.5)+cbrxr*9.5)/13.8-lengthX*2.1),round(cblyr+lengthY*9.5)]
pA3 = output[round((cblxr*(13.8-9.5)+cbrxr*9.5)/13.8-lengthX*2.75),round(cblyr+lengthY*9.5)]
pA4 = output[round((cblxr*(13.8-9.5)+cbrxr*9.5)/13.8-lengthX*3.4),round(cblyr+lengthY*9.5)]

pB1 = output[round((cblxr*(13.8-10.2)+cbrxr*10.2)/13.8-lengthX*1.4),round(cblyr+lengthY*10.2)]
pB2 = output[round((cblxr*(13.8-10.2)+cbrxr*10.2)/13.8-lengthX*2.1),round(cblyr+lengthY*10.2)]
pB3 = output[round((cblxr*(13.8-10.2)+cbrxr*10.2)/13.8-lengthX*2.75),round(cblyr+lengthY*10.2)]
pB4 = output[round((cblxr*(13.8-10.2)+cbrxr*10.2)/13.8-lengthX*3.4),round(cblyr+lengthY*10.2)]

pC1 = output[round((cblxr*(13.8-10.9)+cbrxr*10.9)/13.8-lengthX*1.4),round(cblyr+lengthY*10.9)]
pC2 = output[round((cblxr*(13.8-10.9)+cbrxr*10.9)/13.8-lengthX*2.1),round(cblyr+lengthY*10.9)]
pC3 = output[round((cblxr*(13.8-10.9)+cbrxr*10.9)/13.8-lengthX*2.75),round(cblyr+lengthY*10.9)]
pC4 = output[round((cblxr*(13.8-10.9)+cbrxr*10.9)/13.8-lengthX*3.4),round(cblyr+lengthY*10.9)]

pD1 = output[round((cblxr*(13.8-11.6)+cbrxr*11.6)/13.8-lengthX*1.4),round(cblyr+lengthY*11.6)]
pD2 = output[round((cblxr*(13.8-11.6)+cbrxr*11.6)/13.8-lengthX*2.1),round(cblyr+lengthY*11.6)]
pD3 = output[round((cblxr*(13.8-11.6)+cbrxr*11.6)/13.8-lengthX*2.75),round(cblyr+lengthY*11.6)]
pD4 = output[round((cblxr*(13.8-11.6)+cbrxr*11.6)/13.8-lengthX*3.4),round(cblyr+lengthY*11.6)]

pE1 = output[round((cblxr*(13.8-12.3)+cbrxr*12.3)/13.8-lengthX*1.4),round(cblyr+lengthY*12.3)]
pE2 = output[round((cblxr*(13.8-12.3)+cbrxr*12.3)/13.8-lengthX*2.1),round(cblyr+lengthY*12.3)]
pE3 = output[round((cblxr*(13.8-12.3)+cbrxr*12.3)/13.8-lengthX*2.75),round(cblyr+lengthY*12.3)]
pE4 = output[round((cblxr*(13.8-12.3)+cbrxr*12.3)/13.8-lengthX*3.4),round(cblyr+lengthY*12.3)]

#if you see pH = 24, something went wrong
estimatedpH = 24
#complicated pH comparison time

def pHcomp(x,y):
    tolerance = 0.05
    return (x[1]>(y[1]*(1-tolerance)) and x[1]>(y[1]*(1+tolerance))) and (x[0]>(y[0]*(1-tolerance)) and x[0]>(y[0]*(1+tolerance))) and (x[2]>(y[2]*(1-tolerance)) and x[2]>(y[2]*(1+tolerance)))
comparisonFound = True
#Todo for the future: instead of trying to just comparing the reference, actually use the reference to calculate the pH that are not just integer values
#The pH given not using the reference actually is accurate enough (within 0.5 for most of my runs)
if pH2[0]>pH2[1] and pH2[0]>pH2[2]:
    #then ph<7
    if pH1[2]*1.3>pH1[1] and pH1[2]*1.3>pH1[0]:
        if pHcomp(pH1, p54):
            estimatedpH = 5
        elif pHcomp(pH1, p64):
            estimatedpH = 6
        elif pHcomp(pH1, p74):
            estimatedpH = 7
        else:
            comparisonFound = False
    if pHcomp(pH1,p04):
        estimatedpH = 0
    elif pHcomp(pH1, p14):
        estimatedpH = 1
    elif pHcomp(pH1, p24):
        estimatedpH = 2
    elif pHcomp(pH1, p34):
        estimatedpH = 3
    elif pHcomp(pH1, p44):
        estimatedpH = 4
    elif pHcomp(pH1, p54):
        estimatedpH = 5
    elif pHcomp(pH1, p64):
        estimatedpH = 6
    else:
        comparisonFound = False
elif pH2[1]>pH2[0] and pH2[1]>pH2[2]:
    #then ph>6 and ph<10
    if pHcomp(pH2,p63):
        estimatedpH = 6
    elif pHcomp(pH2,p73):
        estimatedpH = 7
    elif pHcomp(pH2,p73):
        estimatedpH = 7
    elif pHcomp(pH2,p83):
        estimatedpH = 8
    elif pHcomp(pH2,p93):
        estimatedpH = 9
    elif pHcomp(pH2,pA3):
        estimatedpH = 10
    else:
        comparisonFound = False
else:
    #then pH>9
    if pHcomp(pH3,p92):
        estimatedpH = 9
    elif pHcomp(pH3,pA2) and pHcomp(pH4,pA1):
        estimatedpH = 10
    elif pHcomp(pH3,pB2) and pHcomp(pH4,pB1):
        estimatedpH = 11
    elif pHcomp(pH3,pC2) and pHcomp(pH4,pC1):
        estimatedpH = 12
    elif pHcomp(pH3,pD2) and pHcomp(pH4,pD1):
        estimatedpH = 13
    elif pHcomp(pH3,pE2) and pHcomp(pH4,pE1):
        estimatedpH = 14
    else:
        comparisonFound = False

#the specific numbers was based on the colors on the reference strip. I assumed a linear relationship.
if not comparisonFound:
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

