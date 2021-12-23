import glob
import json

import numpy as np
import cv2
import requests


# Numpy Array to JSON
arr = cv2.imread('bathroom.jpg')
arr1 = cv2.imread('bedroom.jpg')
arr2 = cv2.imread('kitchen.jpg')

arr3 = cv2.imread('0-3891.jpg')
arr4 = cv2.imread('0-1085-15407.jpg')
arr5 = cv2.imread('0-2656.jpg')

data = {'model': 'RoomNet', 'arr': arr5.tolist()}
data1 = {'model': 'KitchenNet', 'arr': arr4.tolist()}

# Call to API pour envoyer une numpy image en json
r = requests.post('http://127.0.0.1:5000/kitchen_prediction', json=data)
print(r.status_code)
print(r.text)


r = requests.post('http://127.0.0.1:5000/kitchen_prediction', json=data1)
print(r.status_code)
print(r.text)