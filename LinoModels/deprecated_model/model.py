# -*- coding: utf-8 -*-
# @Time    : 2018/4/24 10:04
# @Author  : zhoujun

import cv2
import torch
import torch.nn.functional as F
import torchvision.models as models
from torch.autograd import Variable
from torchvision import transforms


class Pytorch_Model:
    def __init__(self, model_path, img_shape, img_channel=3, gpu_id=None, classes_txt=None):
        """
        Args:
            model_path:
            img_shape:
            img_channel:
            gpu_id:
            classes_txt:
        """
        self.gpu_id = gpu_id
        self.img_shape = img_shape
        self.img_channel = img_channel
        if self.gpu_id is not None and isinstance(self.gpu_id, int) and torch.cuda.is_available():
            self.device = torch.device("cuda:%s" % (self.gpu_id))
        else:
            self.device = torch.device("cpu")

        if self.gpu_id is not None and isinstance(self.gpu_id, int):
            self.use_gpu = True
        else:
            self.use_gpu = False
        if not self.use_gpu:
            self.net = torch.load(
                model_path, map_location=lambda storage, loc: storage.cpu())
        else:
            self.net = torch.load(
                model_path, map_location=lambda storage, loc: storage.cuda(gpu_id))
        model = models.resnet34(pretrained=True)
        model.fc = torch.nn.Linear(512, 6)
        model.load_state_dict(self.net["model"])
        self.net = model
        self.net.eval()

        if classes_txt is not None:
            with open(classes_txt, 'r') as f:
                self.idx2label = dict(line.strip().split(' ') for line in f if line)
        else:
            self.idx2label = None

    def predict(self, img, is_numpy=False, topk=1):
        """
        Args:
            img:
            is_numpy:
            topk:
        """
        if len(self.img_shape) not in [2, 3] or self.img_channel not in [1, 3]:
            raise NotImplementedError

        if not is_numpy and self.img_channel in [1, 3]:  # read image
            img = cv2.imread(img, 0 if self.img_channel == 1 else 1)
        img = cv2.resize(img, (self.img_shape[0], self.img_shape[1]))
        if len(img.shape) == 2 and self.img_channel == 3:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        elif len(img.shape) == 3 and self.img_channel == 1:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        img = img.reshape(
            [self.img_shape[0], self.img_shape[1], self.img_channel])
        tensor = transforms.ToTensor()(img)
        tensor = tensor.unsqueeze_(0)
        tensor = Variable(tensor)

        tensor = tensor.to(self.device)
        outputs = F.softmax(self.net(tensor), dim=1)
        result = torch.topk(outputs.data[0], k=topk)

        if self.device != "cpu":
            index = result[1].cpu().numpy().tolist()
            prob = result[0].cpu().numpy().tolist()
        else:
            index = result[1].numpy().tolist()
            prob = result[0].numpy().tolist()
        if self.idx2label is not None:
            label = []
            for idx in index:
                label.append(self.idx2label[str(idx)])
            result = zip(label, prob)
        else:
            result = zip(index, prob)
        return result
