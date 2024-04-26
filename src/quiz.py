from cv2.typing import MatLike
from imutils.contours import sort_contours
from imutils.perspective import four_point_transform
from pathlib import Path
import argparse
import cv2
import imutils
import numpy as np

# For visualization purposes
def cv2_imshow(**kwargs):

    for window, img in kwargs.items():
        cv2.namedWindow(window, cv2.WINDOW_NORMAL)
        cv2.imshow(window, img)

    cv2.waitKey(0)
    cv2.destroyAllWindows()


def get_document_edges(img: MatLike) -> MatLike:

    # Instantiate a new kernel
    kernel = np.ones((5,5), np.uint8) 

    # Basic filtering
    filtered = cv2.medianBlur(img, 11)
    filtered = cv2.bilateralFilter(filtered, 9, 30, 5)

    # Canny edge detection and morphological operations to reduce noise and 
    # close the edges 
    canny = cv2.Canny(filtered, 30, 200)
    canny = cv2.dilate(canny, kernel, iterations=13)
    canny = cv2.erode(canny, kernel, iterations=7)

    return canny
    

def get_document_contours(img: MatLike) -> MatLike:

    cnts = cv2.findContours(
        img.copy(), 
        cv2.RETR_EXTERNAL, 
        cv2.CHAIN_APPROX_SIMPLE
    )
    contours = imutils.grab_contours(cnts)
    document_contour = None

    if len(contours) > 0:

        # Sort contours by largest area
        contours = sorted(contours, key=cv2.contourArea, reverse=True)

        # Find the largest closed, 4 edged contour (rectangular shaped) 
        for contour in contours:
            peri = cv2.arcLength(contour, closed=True)
            approx = cv2.approxPolyDP(contour, 0.04 * peri, closed=True)

            if len(approx) == 4: # Edges
                document_contour = approx
                break

    if document_contour is None:
        raise Exception("Document was not detected.")
    
    return document_contour


def get_bubble_contours(thresh: MatLike) -> list[MatLike]:

    cnts = cv2.findContours(
        thresh.copy(), 
        cv2.RETR_EXTERNAL,
	    cv2.CHAIN_APPROX_SIMPLE
    )
    contours = imutils.grab_contours(cnts)
    bubble_contours = []

    for contour in contours:
	    
        (x, y, w, h) = cv2.boundingRect(contour)
        ASPECT_RATIO = w / h

	    # Validate dimensions and aspect ratio of bubble bounding rectangle
        if w >= 30 and h >= 30 and 1.1 >= ASPECT_RATIO >= 0.9:
            bubble_contours.append(contour)

    return bubble_contours


def grade(thresh: MatLike, paper, bubble_contours, answer_key) -> float:
        
        num_correct = 0

        # Grab unique letters from the answer key
        possible_answers = sorted(set(answer_key))

        # N number of possible answers for a given row
        N = len(possible_answers)

        # A map used to convert letters to numbers (i.e. A->0, B->1)
        # used for comparing to the answer key
        amap = {letter: index for index, letter in enumerate(possible_answers)}
        
        # Group the bubbles into their respective questions/rows
        bubble_contours = sort_contours(bubble_contours,
	        method="top-to-bottom")[0]
        
        # Iterate through each question (row)
        for (q, i) in enumerate(np.arange(0, len(bubble_contours), N)):

            cnts = sort_contours(bubble_contours[i : i+N])[0]
            bubbled = None

            # Iterate through each potential answer/bubble for the question (row)
            for (index, contour) in enumerate(cnts):

                # Mask for current bubble, count total non-zero px inside
                mask = np.zeros(thresh.shape, dtype="uint8")
                cv2.drawContours(mask, [contour], -1, 255, -1)
                mask = cv2.bitwise_and(thresh, thresh, mask=mask)
                total = cv2.countNonZero(mask)
		
                # New answer if more filled in than the previous bubble
                if bubbled is None or total > bubbled[0]:
                    bubbled = (total, index)

                # Set contour color and the correct bubble index
                color = (0, 0, 255)
                answer_index = amap[answer_key[q]]

	        # Answer is correct?
            if answer_index == bubbled[1]:
                color = (255, 0, 0)
                num_correct += 1
	
            # draw the outline of the correct answer on the test
            cv2.drawContours(paper, [cnts[answer_index]], -1, color, 6)

        # Calculate grade
        score = round(((num_correct / q) * 100), 2)
        print(f"Grading finished, test score: {score}%" )

        cv2.putText(paper, f"Grade: {score}%", (40, 80), 
            cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 4)
        cv2_imshow(graded_paper=paper)


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-i', 
        '--image', 
        required=True,
        metavar='image',
        type=Path,
        help="path to the gradeable quiz image"
    )
    parser.add_argument(
        '-a', 
        '--answers', 
        nargs='*',
        default=[],
        metavar='answer',
        help="list of alphabetical answers (e.g. A B C D E)"
    )

    # Get cmdln arguments
    args = parser.parse_args()
    answers = [a.upper() for a in args.answers]
    path = args.image

    if not path.exists() or not path.is_file():
        raise Exception("Image path does not exist or is not a valid file.")

    # Try to open image
    try:
        img = cv2.imread(str(path))
    except Exception as e:
        raise Exception("Could not open the image file. Details:\n"+e)
    
    # Grayscale for better results
    img_grayscale = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Finding edges/contours of the document
    img_edged = get_document_edges(img=img_grayscale)
    img_contoured = get_document_contours(img_edged)

    # Transform/warp focus onto the document, birds-eye view
    paper = four_point_transform(img, img_contoured.reshape(4, 2))
    warp = four_point_transform(img_grayscale, img_contoured.reshape(4, 2))

    # Binarize the document
    thresh = cv2.threshold(warp, 0, 255, 
        cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    
    bubble_contours = [
        contour for contour in get_bubble_contours(thresh)
    ]

    grade(thresh, paper, bubble_contours, answers)

if __name__ == "__main__":

    main()