# UCB-BIO-ENG-134-Final-Project

Description: Code that will extract information of a pH strip and output its pH. Also has a version for glucose.

Usage: The code in this repository is intended to be used in a raspberry PI. It is advised to ensure that the camera is able to completely capture both black boxes along with some white paper border. Try to get it as straight as possible. The pH strip box should be to the left. The four boxes on the pH strip should be on the top. The reference paper is taken directly from the box that the pH strips come from.
The code is more robust for slight rotations of the camera, such that the rectangles look like trapezoids or parellelograms, but not as robust for rotations that cause the rectangle lines to be not parallel to the edge of the image.

To run the code on the raspberry pi, type in python3 (file/path) in the terminal and hit enter. Note that python3 must be used, for some of the libraries do not work with python 2.

File descriptions:

template pH.docx: The sheet of paper to be printed out. The pH strip goes onto the skinnier box, and the reference goes into the fatter box.

test.py: Outputs an image onto the raspberry PI, so the user can ensure that the camera and paper is positioned properly. The picture is outputed at "output.png" where the test.py is located.

pH.py: Outputs the pH of the pH strip. A picture will be outputed at "output.png" where the pH.py is located, although it does NOT use this image

pHNoReference.py: Outputs the pH of the pH strip without using a reference. (useful if the reference can't be obtained or there is a problem correctly getting the reference boxes right). A picture will be outputed at "output.png" where the pHNoReference.py is located, although it does NOT use this image

glucose.py: Outputs the glucose level of the glucose strip. A picture will be outputed at "output.png" where the glucose.py is located, although it does NOT use this image

example: How the paper should be set up

setupExample.jpg: An example of a crude, but cheap, setup of the camera and paper system
