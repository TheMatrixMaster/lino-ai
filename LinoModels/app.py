import json
import time
from glob import glob
import os

import flask
import numpy as np
from flask import request, Flask
from flask_uploads import UploadSet, IMAGES, configure_uploads

from config import configs
from mynet import Net

from AWS_Controller import AWS_Controller


app = Flask(__name__)
app.config.from_object(configs[app.env])
images = UploadSet('images', IMAGES)
configure_uploads(app, images)



def classify_net(nn, img_data, CLASS_LABELS):
    print('Classifying new image')
    infer_outs = nn.infer_optimized(img_data)
    pred_label = CLASS_LABELS[infer_outs[0][0]]
    pred_conf = infer_outs[1][0][infer_outs[0][0]]

    # save to database
    print(pred_conf)
    # if pred_conf >= 0.95:
    #     aws = AWS_Controller()
    #     aws.save_image(img_data, pred_label)

    return pred_label



@app.route('/room_prediction', methods=['POST'])
def room():
    # initialize model variables
    CLASS_LABELS = ['Backyard', 'Bathroom', 'Bedroom', 'Frontyard', 'Kitchen', 'LivingRoom']
    INPUT_MODEL_PATH = 'static/RoomNet/roomnet'
    IMG_SIDE = 224

    # get img data
    received_data = request.json
    model = received_data['model']
    arr = np.array(received_data['arr'], dtype='uint8')
    print(model, arr.shape)

    # load model
    nn = Net(num_classes=len(CLASS_LABELS), im_side=IMG_SIDE, compute_bn_mean_var=False,
                 optimized_inference=True)
    nn.load(INPUT_MODEL_PATH)

    # classify image
    label = classify_net(nn, arr, CLASS_LABELS)

    return label


@app.route('/kitchen_prediction', methods=['POST'])
def kitchen():
    # initialize model variables
    CLASS_LABELS = ['Chimney', 'Under-cabinet']
    INPUT_MODEL_PATH = 'static/KitchenNet/roomnet'
    IMG_SIDE = 224

    # get img data
    received_data = request.json
    model = received_data['model']
    arr = np.array(received_data['arr'], dtype='uint8')
    print(model, arr.shape)

    # load model
    nn = Net(num_classes=len(CLASS_LABELS), im_side=IMG_SIDE, compute_bn_mean_var=False,
                 optimized_inference=True)
    nn.load(INPUT_MODEL_PATH)

    # classify image
    label = classify_net(nn, arr, CLASS_LABELS)

    return label


@app.route('/bathroom_prediction', methods=['POST'])
def bathroom():

    received_data = request.json
    model = received_data['model']
    arr = np.array(received_data['arr'])
    print(model, arr.shape)

    return "Bathroom module not done yet"




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
