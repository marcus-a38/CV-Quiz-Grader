# Computer Vision (and Image Processing) Quiz Grader
A simple multiple choice grader using OpenCV for Python, completed as practice for a class on graphics programming.

---

## Credit
The bulk of the code for this project can be attributed to [**this tutorial**](https://pyimagesearch.com/2016/10/03/bubble-sheet-multiple-choice-scanner-and-test-grader-using-omr-python-and-opencv/) by Adrian Rosebrock.

---

## Introduction
As mentioned above, this script was created for practice as a beginner in graphics programming. The goal of this script is 
to process an image of a multiple choice quiz and determine a grade based on filled in bubbles with a user-provided answer key.  

#

Currently, there are a few problems that I anticipate fixing at some point:

1. Low contrast, high-texture backgrounds trip up the Canny edge detector. I've tried to remedy with various preprocessing setups,
   but I suspect that I will need to learn more about adaptive thresholding and/or advanced filtering algorithms.
   
2. There is no handle for instances where a question is left blank. In this case, it's up to the script to "randomly" pick an answer
   for you, determined by the count of internal dark pixels for a given bubble.
   
3. While the script properly grades the papers visually, it spits out percentages that aren't entirely accurate. For example, I have
   a 7/10 score based on the image output from the script. It should be instantly obvious that the grade is 70%, yet I've been getting
   values of 77.7%. Probably some incredibly small and obvious math error that I've overlooked.

---

## Concept / Pipeline 
This script can be broken down and grouped into a few simple steps:

### 1. Edge / Contour Detection

#### &ensp;Flowchart
&emsp;![Step 1 Flowchart](media/Step1.png)

#### &ensp;Example

##### &emsp;Provided Answer Key
&emsp;[1,1,1,1,1,1,1]

##### &emsp;Original Image
&emsp;![Step 1 Original Image](media/Step1Example-Grayscale.png)

##### &emsp;Convert to Grayscale
&emsp;![Step 1 Grayscale Image](media/Step1Example-Grayscale.png)

##### &emsp;Canny Edge Detect 
&emsp;![Step 1 Canny Image](media/Step1Example-Grayscale.png)

##### &emsp;Find Contours
&emsp;![Step 1 Contour Image](media/Step1Example-Grayscale.png)

#

### 2. Transformations / Morphing

#### &ensp;Flowchart
&emsp;![Step 2 Flowchart](media/Step2.png)

#### &ensp;Example

##### &emsp;Warp Image
&emsp;![Step 2 Warped Image](media/Step2Example-Warped.png)

##### &emsp;Binarize Image
&emsp;![Step 2 Binarized Image](media/Step2Example-Binarized.png)

#

### 3. "Bubble" Detection

#### &ensp;Flowchart
&emsp;![Step 3 Flowchart](media/Step3.png)

#### &ensp;Example

##### &emsp;Bubble Contours
&emsp;![Step 3 Example](media/Step3Example.png)

#

### 4. Grading

#### &ensp;Flowchart
&emsp;![Step 4 Flowchart](media/Step4.png)

#### &ensp;Example

##### &emsp;Graded Quiz Image / Output
&emsp;![Step 4 Example](media/Step4Example.png)

---

## Usage
*To-do*
