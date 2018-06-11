#!/usr/bin/env python

import os
from functools import reduce
import shutil

from tensorboard_logger import configure, log_value
import numpy as np
import torch
import torch.nn as nn

from .meter import AverageMeter
from .visualizer import Visualizer

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

class Trainer(object):
    def __init__(self, title=None, config=None, data=None, model=None):
        super(Trainer, self).__init__()
        self.title = title
        self.config = config
        self.data = data

        # logs
        self.batch_time = AverageMeter()
        self.data_time = AverageMeter()
        self.losses = AverageMeter()
        self.top1 = AverageMeter()
        self.top5 = AverageMeter()

        self.train_loss = 0

        # parameters / model
        self.model = model
        self.trainable_parameters = 0
        self.completed_epochs = 0
        self.lr = self.config.hyperparameters['lr']

        self.criterion = None
        self.optimizer = None
        self.curr_lr = 0

        # visualization config
        # self.visualizer = Visualizer(title=self.title)

    def setName(self, name):
        self.name = name
        return True

    def setConfig(self, config):
        self.config = config
        return True

    def setData(self, data):
        self.data = data
        return True

    def setModel(self, model):
        self.model = model
        self.count_parameters()
        return True

    def setCriterion(self, criterion):
        self.criterion = criterion
        return True

    def setOptimizer(self, optimizer):
        self.optimizer = optimizer
        return True

    def count_parameters(self):
        if self.model is None:
            raise ValueError('[-] No model has been provided')

        self.trainable_parameters = sum(reduce( lambda a, b: a*b, x.size()) for x in self.model.parameters())

    def getTrainableParameters(self):
        if self.model is not None and self.trainable_parameters == 0:
            self.count_parameters()

        return self.trainable_parameters

    def step(self):
        pass

    def save_checkpoint(self, state, is_best, checkpoint=None):
        if checkpoint is None:
            ckpt_path = os.path.join(self.config.checkpoints['loc'], self.config.checkpoints['ckpt_fname'])
        else:
            ckpt_path = os.path.join(self.config.checkpoints['loc'], checkpoint)
        best_ckpt_path = os.path.join(self.config.checkpoints['loc'], \
                            self.config.checkpoints['best_ckpt_fname'])
        torch.save(state, ckpt_path)
        if is_best:
            shutil.copy(ckpt_path, best_ckpt_path)

    def load_saved_checkpoint(self, checkpoint=None):
        if checkpoint is None:
            path = os.path.join(self.config.checkpoints['loc'], \
                    self.config.checkpoints['ckpt_fname'])
        else:
            path = os.path.join(self.config.checkpoints['loc'], checkpoint)
        torch.load(path)

        start_epoch = checkpoint['epoch']
        best_prec1 = checkpoint['best_prec1']
        self.model.load_state_dict(checkpoint['state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer'])

        print("[#] Loaded Checkpoint '{}' (epoch {})"
            .format(self.config.checkpoints['ckpt_fname'], checkpoint['epoch']))
        return (start_epoch, best_prec1)

    def adjust_learning_rate(self, epoch):
        """Sets the learning rate to the initial LR decayed by 10 every 30 epochs"""
        self.curr_lr = self.config.hyperparameters['lr'] * (self.config.hyperparameters['lr_decay'] ** (epoch // self.config.hyperparameters['lr_decay_epoch']))
        for param_group in self.optimizer.param_groups:
            param_group['lr'] = self.curr_lr

    def train(self, epoch):
        if self.model is None:
            raise ValueError('[-] No model has been provided')
        if self.config is None:
            raise ValueError('[-] No Configurations present')
        if self.criterion is None:
            raise ValueError('[-] Loss Function hasn\'t been mentioned for the model')
        if self.optimizer is None:
            raise ValueError('[-] Optimizer hasn\'t been mentioned for the model')
        if self.data is None:
            raise ValueError('[-] No Data available to train on')

        self.train_loss = 0
        # training mode
        self.model.train()
        for batch_idx, (images, labels) in enumerate(self.data):
            if self.config.gpu:
                images = images.to(device)
                labels = labels.to(device)

            output = self.model(images)
            loss = self.criterion(output, labels)

            self.optimizer.zero_grad()
            loss.backward()
            self.train_loss = loss.item()
            self.optimizer.step()

            log_value('train_loss', loss.item())
            if batch_idx % self.config.logs['log_interval'] == 0:
                print(
                    'Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}\tlr: {:.6f}'.format(
                    epoch+1, batch_idx * len(images), len(self.data.dataset),
                    100. * batch_idx / len(self.data),
                    loss.item() / len(self.data), self.curr_lr)
                )



        # self.visualizer.add_values(epoch, loss_train=self.train_loss)
        # self.visualizer.redraw()
        # self.visualizer.block()
