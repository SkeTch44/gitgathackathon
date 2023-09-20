'''This script checks for originality of the image uploaded by user'''
import cv2 # import opencv module to work with image matching
import os # import os module to work with commands related to operating system

def images_similar(sus_img_name, image):
    '''function that takes two images and compares both of the images to check for potential similarity between them'''
    dim = (640, 480)
    sus_img = cv2.imread(sus_img_name) # open the suspicious image
    sus_img = cv2.resize(sus_img, dim, interpolation = cv2.INTER_AREA) # resize the image to smaller size

    img = cv2.imread(image) # open the image to compare with
    img = cv2.resize(img, dim, interpolation = cv2.INTER_AREA) # resize the image to a smaller size

    # convert the images to grayscale for faster comparision
    sus_img_gray = cv2.cvtColor(sus_img, cv2.COLOR_BGR2GRAY)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # compare both of the images
    matched_template = cv2.matchTemplate(sus_img_gray, img_gray, cv2.TM_CCOEFF_NORMED)

    # get the probability of how similar the images are
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(matched_template)

    # if images are similar then tag the image as duplicate
    if max_val >= 0.95: # this 0.95 is the threshold value to check for similar images (calculated after many trials)
        return True
    else:
        return False

def is_original(sus_image):
    '''this function calls the above function "images_similar" recursively on all of the files in the database and checks if the suspicious image is original'''
    
    similar_found = False # flag to check if any similar image was found
    images_db = os.listdir("static/nft_gallery") # list all images in database
    for img in images_db:
        if images_similar(sus_image, "static/nft_gallery/"+img): # call the function 'images_similar'
            similar_found = True # if image was similar set the flag similar_found to True
            break
    if similar_found:
        return False # if similar_found flag was True return False because image is not original
    else:
        return True # else return True since image is original
