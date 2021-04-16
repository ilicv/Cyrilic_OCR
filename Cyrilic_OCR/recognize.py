import numpy as np 
import keras
from sklearn.model_selection import train_test_split
import random
from time import time
import cv2

from PIL import Image
import PIL as PIL

import tensorflow as tf 


def grayConversion(image):
    grayValue = 0.07 * image[:,:,2] + 0.72 * image[:,:,1] + 0.21 * image[:,:,0]
    gray_img = grayValue.astype(np.uint8)
    return gray_img


def create_model():
    from keras.models import Sequential
    from keras.layers import Conv2D, MaxPooling2D, Dropout, Flatten, Dense, Activation

    model = Sequential()

    model.add(Conv2D(16, (3, 3), activation='relu', input_shape=(lett_w, lett_h, 1)))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))

    model.add(Conv2D(32, (3, 3), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))

    model.add(Conv2D(64, (3, 3), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))

    model.add(Flatten())
    model.add(Dense(128, activation='relu'))
    model.add(Dropout(0.25))
    model.add(Dense(64, activation='relu'))
    model.add(Dropout(0.25))
    model.add(Dense(32, activation='relu'))
    model.add(Dense(24))
    model.add(Activation('sigmoid'))

    model.compile(optimizer="adadelta",loss="binary_crossentropy",metrics=["accuracy"])

    model.summary()

    return model


def predict(df_im):
    predictions1 = model1.predict(df_im, verbose=0)
    predictions2 = model2.predict(df_im, verbose=0)
    predictions3 = model3.predict(df_im, verbose=0)
    predictions4 = model4.predict(df_im, verbose=0)
    predictions = predictions1
    cnt = 0
    for p in predictions:
        predictions[cnt] = (predictions1[cnt] + predictions2[cnt] + predictions3[cnt]+ predictions4[cnt]) / 4
    return predictions


def recognize_letter(img):
    lett_h = 48
    lett_w = 32

    start = 0
    max = 8000

    img = img.resize((lett_w,lett_h), Image.ANTIALIAS)
    img = np.asarray(img)
    gray = grayConversion(img)

    img1 = gray/255
    img1 = np.asarray(img1)
    img1 = img1.reshape(1, lett_w, lett_h, 1)

    res = predict(img1)

    net_out = []

    ss = ''
    for item in res[0]:
        #if item>0.40:
        if item>0.50:
            p=1
        else:
            p=0
        ss = ss+str(p)+','
        net_out.append(p)

    return net_out

def recognize(file_name):
    img = Image.open(file_name)
    net_out = recognize_letter(img)
    return net_out

lett_h = 48
lett_w = 32
imgs_dir = '..\\letters\\'

model1 = create_model()
model2 = create_model()
model3 = create_model()
model4 = create_model()

config = tf.ConfigProto()
config.gpu_options.allow_growth = True
session = tf.Session(config=config)

model1_name = "model_img1.h5"
model2_name = "model_img2.h5"
model3_name = "model_img3.h5"
model4_name = "model_img4.h5"

model1.load_weights(model1_name)
model2.load_weights(model2_name)
model3.load_weights(model3_name)
model3.load_weights(model4_name)

#r = recognize('letter1059.bmp')
#print (r)