import cv2
import numpy as np

def order_points_float32(pts):
	# initialzie a list of coordinates that will be ordered
	# such that the first entry in the list is the top-left,
	# the second entry is the top-right, the third is the
	# bottom-right, and the fourth is the bottom-left
	rect = np.zeros((4, 2), dtype = "float32")
 
	# the top-left point will have the smallest sum, whereas
	# the bottom-right point will have the largest sum
	s = pts.sum(axis = 2)
	rect[0] = pts[np.argmin(s)]
	rect[2] = pts[np.argmax(s)]
 
	# now, compute the difference between the points, the
	# top-right point will have the smallest difference,
	# whereas the bottom-left will have the largest difference
	diff = np.diff(pts, axis = 2)
	rect[1] = pts[np.argmin(diff)]
	rect[3] = pts[np.argmax(diff)]
 
	# return the ordered coordinates
	return rect


def order_points(pts):
	# initialzie a list of coordinates that will be ordered
	# such that the first entry in the list is the top-left,
	# the second entry is the top-right, the third is the
	# bottom-right, and the fourth is the bottom-left
	rect = np.zeros((4, 2), dtype = "int32")
 
	# the top-left point will have the smallest sum, whereas
	# the bottom-right point will have the largest sum
	s = pts.sum(axis = 2)
	rect[0] = pts[np.argmin(s)]
	rect[2] = pts[np.argmax(s)]
 
	# now, compute the difference between the points, the
	# top-right point will have the smallest difference,
	# whereas the bottom-left will have the largest difference
	diff = np.diff(pts, axis = 2)
	rect[1] = pts[np.argmin(diff)]
	rect[3] = pts[np.argmax(diff)]
 
	# return the ordered coordinates
	return rect


def four_point_transform(image, pts):
	# obtain a consistent order of the points and unpack them
	# individually
	# rect = order_points_float32(pts)
    rect = pts
    (tl, tr, br, bl) = rect
	# compute the width of the new image, which will be the
	# maximum distance between bottom-right and bottom-left
	# x-coordiates or the top-right and top-left x-coordinates
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))

    # compute the height of the new image, which will be the
    # maximum distance between the top-right and bottom-right
    # y-coordinates or the top-left and bottom-left y-coordinates
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))

    # now that we have the dimensions of the new image, construct
    # the set of destination points to obtain a "birds eye view",
    # (i.e. top-down view) of the image, again specifying points
    # in the top-left, top-right, bottom-right, and bottom-left
    # order
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype = "float32")

    # compute the perspective transform matrix and then apply it
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

    # return the warped image
    return warped

def get_area(thing):
    return thing[0]


def get_raw_plate(cv_image):

    mplate1 = cv2.inRange(cv_image, (99, 99, 99), (103, 103, 103)) #Top left background
    mplate2 = cv2.inRange(cv_image, (118, 118, 118), (125, 125, 125)) #bottom background
    mplate3 = cv2.inRange(cv_image, (198, 198, 198), (206, 206, 206)) #right background
    
    mblack = cv2.inRange(cv_image, (0, 0, 0), (45, 45, 45)) #black

    mplate4 = 0#cv2.inRange(cv_image, (170, 167, 166), (177, 174, 173)) # right plate
    mplate5 = 0#cv2.inRange(cv_image, (87, 85, 85), (92, 97, 90 )) #top left plate
    mplate6 = 0#cv2.inRange(cv_image, (103, 101, 99), (109, 104, 103 )) #another top left plate
    
    mask_plates_full = cv2.add(cv2.add(cv2.add(cv2.add(mplate1, mplate2), mplate3), mplate4), mplate5)
    mask_plates_full = cv2.add(cv2.add(mask_plates_full, mplate6), mblack)

    contour_show = cv_image.copy()
    contour_show_bin = mask_plates_full.copy()

    _, contours, _ = cv2.findContours(mask_plates_full, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    all_areas = []

    for cnt in contours: 
        area = cv2.contourArea(cnt)
        if area > 1300: # was 1000 #was 700 # was 500 
            alength = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt,  0.0080 * cv2.arcLength(cnt, True), True) #was 0.009 @was 0.0095
            if len(approx)==4:
                all_areas.append((area, approx))
                contour_show = cv2.drawContours(contour_show, [approx], 0, (0, 0, 255), 5) 
                contour_show_bin = cv2.drawContours(contour_show_bin, [approx], 0, (0, 0, 255), 5) 

                hull = cv2.convexHull(approx,returnPoints = False)
                defects = cv2.convexityDefects(approx,hull)

    all_areas.sort(reverse=True, key=get_area)  
    if len(all_areas ) > 0:
        print("area size: " + str(all_areas[0][0]))     
        contour_show = cv2.drawContours(contour_show, [all_areas[0][1]], 0, (0, 255, 0), 5) 
        contour_show_bin = cv2.drawContours(contour_show_bin, [all_areas[0][1]], 0, (0, 255, 0), 5) 
        
        p_order = order_points(all_areas[0][1])
        
        sizeL = p_order[0][1] - p_order[3][1]
        sizeR = p_order[1][1] - p_order[2][1]

        #drop_ratio = 1.26
        drop_ratio = 1.4458
        p_adjusted = p_order.copy()
        p_adjusted[3][1] = int(max(p_adjusted[3][1] + ((1-drop_ratio)*sizeL), 0))
        p_adjusted[2][1] = int(max(p_adjusted[2][1] + ((1-drop_ratio)*sizeR), 0))

        contour_show = cv2.drawContours(contour_show, [p_adjusted], 0, (255, 0, 0), 5)         
        
        float_p_adjusted = p_adjusted.copy().astype('float32')
        # for i in range(len(float_p_adjusted)-1):
        #     for j in range(len(float_p_adjusted[i])-1):
        #         float_p_adjusted[i][j] = float(float_p_adjusted[i][j])

        transformed_image =four_point_transform(cv_image, float_p_adjusted)
    else: 
        transformed_image = None
        
    return transformed_image
