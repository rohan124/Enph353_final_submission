from numpy import expand_dims
from keras.preprocessing.image import load_img
from keras.preprocessing.image import img_to_array
from keras.preprocessing.image import ImageDataGenerator
from matplotlib import pyplot
import cv2
import os
from PIL import Image
import numpy as np
import random

from skimage.util import random_noise
# load the image
raw_pics_path = '/home/fizzer/Enph353-Comp/cnn/raw_pics/'
save_pics_path = '/home/fizzer/Enph353-Comp/cnn/aug_letters/'
# augmented = []
# augment_names = []


files = [img for img in os.listdir(raw_pics_path) if os.path.isfile(os.path.join(raw_pics_path, img)) and img.endswith('.png')] 
#random shuffle
np.random.shuffle(files)
#can chan
MAX_NUM_IMAGES = len(files)#len(files)

IM_HEIGHT = 60
IM_WIDTH = 40

def blur(img):
    return (cv2.blur(img,(int(random.uniform(10,40)),int(random.uniform(10,40)))))

for j, img_path in enumerate(files):

    #if j == MAX_NUM_IMAGES:
    #if j == 10:
        #break
    if j % 5 == 0:
        print('on image: ' + str(j))

    #add random shift
    data = img_to_array(load_img(raw_pics_path+img_path))
    samples = expand_dims(data, 0)
    datagen = ImageDataGenerator(width_shift_range=[int(random.uniform(-8.0,-5.0)),int(random.uniform(5.0,8.0))])
    it = datagen.flow(samples, batch_size=1)
    # generate samples and plot
    for i in range(2):
        # define subplot
        # pyplot.subplot(330 + 1 + i)
        # generate batch of images
        im_shifted = it.next()
        
        #brightness change

        datagen = ImageDataGenerator(brightness_range=[0.4,1.3], preprocessing_function= blur,zoom_range=0.08,height_shift_range=[int(random.uniform(-8.0,-5.0)),int(random.uniform(5.0,8.0))])
        it = datagen.flow(im_shifted, batch_size=1)
        # generate samples and plot
        for i in range(2):
            # define subplot
            # pyplot.subplot(330 + 1 + i)
            # generate batch of images
            im_shifted_brightness = it.next()

            datagen = ImageDataGenerator(rotation_range=random.uniform(0.5, 3))
            it = datagen.flow(im_shifted_brightness, batch_size=1)

            # generate samples and plot
            for i in range(int(random.uniform(1,2))):
                # define subplot
                # pyplot.subplot(330 + 1 + i)
                # generate batch of images
                im_shifted_rotation = it.next()
           
                datagen = ImageDataGenerator(shear_range=random.uniform(0.5, 3))
                it = datagen.flow(im_shifted_rotation, batch_size=1)

                # generate samples and plot
                for i in range(int(random.uniform(1,2))):
                    # define subplot
                    # pyplot.subplot(330 + 1 + i)
                    # generate batch of images
                    im_shifted_shear = it.next()[0].astype('uint8')


                    rand_down_per = random.uniform(0.05, 0.5)

                    width = int(im_shifted_shear.shape[1])
                    height = int(im_shifted_shear.shape[0])
                    shift_down = (int(width*rand_down_per), int(height*rand_down_per))
                    down_sized = cv2.resize(im_shifted_shear, shift_down)

                    shift_up = (im_shifted_shear.shape[1], im_shifted_shear.shape[0])
                    im_shifted_shear_resized = cv2.resize(down_sized, shift_up)
                    #cv2.imwrite(save_pics_path+img_path,im_shifted_shear_resized)
                            
                    #if j%10 == 0:
                        #grayim_final = cv2.cvtColor(data, cv2.COLOR_BGR2GRAY)
                    #else:
                    grayim_final = cv2.cvtColor(im_shifted_shear_resized, cv2.COLOR_BGR2GRAY)
                    #cv2.imwrite(save_pics_path+img_path,grayim_final)

                    def split_ims(im, yi, xi, dy, dx, final_size):
                    #y_i, x_i, dy, dx all arrays of same size
                        ims = []
                        for i, _ in enumerate(yi):
                            im_temp = im[ yi[i] : yi[i] + dy[i], xi[i] : xi[i]+dx[i]]
                            ims.append(cv2.resize(im_temp, final_size))
                        return ims
                        
                    yi = [1320, 1320]
                    xi = [40, 140]
                    dy = [180, 180]
                    dx = [ 120, 120]
                    final_size = (IM_WIDTH, IM_HEIGHT)

                    ims = split_ims(grayim_final, yi, xi, dy, dx, final_size)

                    for i, im in enumerate(ims):
                        rand=random.uniform(0,10000)
                        if i <= 3: 
                            letter = img_path[i]
                        else:
                            letter = img_path[6]
                        filename = letter + "_" + str(j) + "_%d.png" %(rand)
                        cv2.imwrite(save_pics_path + filename, ims[i])