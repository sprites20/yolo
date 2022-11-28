# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'hub.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets

import argparse
import os
import sys
from pathlib import Path
import cv2

import torch

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import os
import shutil

import time
import glob


class ScaledPixmapLabel(QtWidgets.QLabel):
    def paintEvent(self, event):
        if self.pixmap():
            pm = self.pixmap()
            originalRatio = pm.width() / pm.height()
            currentRatio = self.width() / self.height()
            if originalRatio != currentRatio:
                qp = QtGui.QPainter(self)
                pm = self.pixmap().scaled(self.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
                rect = QtCore.QRect(0, 0, pm.width(), pm.height())
                rect.moveCenter(self.rect().center())
                qp.drawPixmap(rect, pm)
                return
        super().paintEvent(event)

class Ui_MainWindow(object):
    loaded_model = None
    cam_running = None
    vid_running = None
    opt = None
    
    num_stop = 1 
    output_folder = 'output/'
    vid_writer = None
    
    openfile_name_model = None
    vid_name = None
    img_name = None
    cap_statue = None
    save_dir = None
    img_over = None

    timer = QtCore.QTimer()
    
    #        Button_open_cam.clicked.connect(video_button)
    cap_video = 0
    flag = 0
    img = []
    
    video_stream = None
    
    alreadystarted_cam = None
    alreadystarted_vid = None
    cam_port = 0
    cam = cv2.VideoCapture(cam_port)
    
    curr_framecount = 0
    curr_fps = 30
    curr_maxframe = 0
    
    recording = None
    saving = None
    
    selected = None
    
    def init_slots(self):
        self.button_load_model.clicked.connect(self.load_model)

        self.button_load_image.clicked.connect(self.open_img)
        self.button_load_video.clicked.connect(self.open_vid)
        self.button_load_camera.clicked.connect(self.open_cam)
        self.button_record.clicked.connect(self.record)
        self.button_save.clicked.connect(self.save)
        # self.ui.pushButton_9.clicked.connect(self.save_ss)
        # self.timer_video.timeout.connect(self.show_video_cam_frame)

        self.button_load_image.setDisabled(True)
        self.button_load_video.setDisabled(True)
        self.button_load_camera.setDisabled(True)
        #self.button_record.setDisabled(True)
        #self.button_save.setDisabled(True)
        
        pass
    def open_img(self):
        self.selected = "img"
        self.button_record.setDisabled(True)
        self.button_save.setDisabled(True)
        # try except
        self.cam_running = False
        self.vid_running = False
        dir = 'detections/images'
        if not os.path.exists(dir):
            #shutil.rmtree(dir)
            os.makedirs(dir)
        try:
            # self.img_name 选择图片路径
            self.img_name, _ = QtWidgets.QFileDialog.getOpenFileName(None, "Select Image", "data/images", "*.jpg ; *.png ; All Files(*)")
        except OSError as reason:
            print(str(reason))
        else:
            im0 = cv2.imread(self.img_name)
            im0 = cv2.cvtColor(im0, cv2.COLOR_BGR2RGB)
            FlippedImage = im0
            image = QtGui.QImage(FlippedImage, FlippedImage.shape[1],FlippedImage.shape[0], FlippedImage.shape[1] * 3, QtGui.QImage.Format_RGB888)
            pix = QtGui.QPixmap(image)
            
            #ConvertToQtFormat = QImage(FlippedImage.data, FlippedImage.shape[1], FlippedImage.shape[0], QImage.Format_RGB888)
            #Pic = ConvertToQtFormat.scaled(640, 640, Qt.KeepAspectRatio)
            #cv2.imshow("test", FlippedImage)
            self.image_box_1.setPixmap(QtGui.QPixmap(pix))
            
            results = self.loaded_model(self.img_name)#.save()
            results.ims
            results.render()
            for im in results.ims:
                #im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
                #cv2.imshow("test", im)
                FlippedImage = im
                image = QtGui.QImage(FlippedImage, FlippedImage.shape[1],FlippedImage.shape[0], FlippedImage.shape[1] * 3, QtGui.QImage.Format_RGB888)
                pix = QtGui.QPixmap(image)
                #ConvertToQtFormat = QImage(FlippedImage.data, FlippedImage.shape[1], FlippedImage.shape[0], QImage.Format_RGB888)
                #Pic = ConvertToQtFormat.scaled(640, 640, Qt.KeepAspectRatio)
                #cv2.imshow("test", FlippedImage)
                FlippedImage = cv2.cvtColor(FlippedImage, cv2.COLOR_BGR2RGB)
                cv2.imwrite("detections/images/" + str(time.time()) + ".jpg", FlippedImage)
                self.image_box_2.setPixmap(QtGui.QPixmap(pix))
        pass
    def open_vid(self):
        self.selected = "video"
        self.cam_running = False
        self.button_record.setDisabled(False)
        self.button_save.setDisabled(False)
        try:
            # self.img_name 选择图片路径
            self.vid_name, _ = QtWidgets.QFileDialog.getOpenFileName(None, "打开视频", "data/videos", "*.mp4;*.mkv;All Files(*)")
        except OSError as reason:
            print(str(reason))
        else:
            if not self.vid_name:
                #QtWidgets.QMessageBox.warning(self, u"Warning", u"打开视频失败", buttons=QtWidgets.QMessageBox.Ok, defaultButton=QtWidgets.QMessageBox.Ok)
                #self.ui.message_box.append("视频载入失败。")
                pass
            else:
                cap = cv2.VideoCapture(self.vid_name)

                if not cap.isOpened(): 
                    print("could not open :",self.vid_name)
                    return
                    
                length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps    = cap.get(cv2.CAP_PROP_FPS)
                
                print(length, width, height, fps)
                
                self.curr_fps = fps
                self.curr_maxframe = length
                self.curr_framecount = 0
                
                dir = 'detections/cache'
                if os.path.exists(dir):
                    shutil.rmtree(dir)
                    os.makedirs(dir)
                else:
                    os.makedirs(dir)
                
                self.vid_running = True
                self.video_stream = cv2.VideoCapture(self.vid_name)
                self.timer.start(20)
                #vid = QtGui.QPixmap(self.vid_name)#.scaled(self.image_box_1.width(), self.image_box_1.height())
                #self.image_box_1.setPixmap(vid)
                
    def open_cam(self):
        self.selected = "cam"
        self.cam_running = True
        self.vid_running = False
        self.button_record.setDisabled(False)
        self.button_save.setDisabled(False)
        dir = 'detections/cache'
        if os.path.exists(dir):
            shutil.rmtree(dir)
            os.makedirs(dir)
        else:
            os.makedirs(dir)
        if not self.alreadystarted_cam:
            self.alreadystarted_cam = True
            self.cap_video = cv2.VideoCapture(0)
            self.timer.start(20)
            
    def show_video(self):
        result, image = None, None
        if self.vid_running:
            result, image = self.video_stream.read()
        if result:
            im0 = image
            im0 = cv2.cvtColor(im0, cv2.COLOR_BGR2RGB)
            FlippedImage = im0
            image = QtGui.QImage(FlippedImage, FlippedImage.shape[1],FlippedImage.shape[0], FlippedImage.shape[1] * 3, QtGui.QImage.Format_RGB888)
            pix = QtGui.QPixmap(image)
            #ConvertToQtFormat = QImage(FlippedImage.data, FlippedImage.shape[1], FlippedImage.shape[0], QImage.Format_RGB888)
            #Pic = ConvertToQtFormat.scaled(640, 640, Qt.KeepAspectRatio)
            #cv2.imshow("test", FlippedImage)
            #FlippedImage = cv2.cvtColor(FlippedImage, cv2.COLOR_BGR2RGB)
            cv2.imwrite("data/images/temp_vid.jpg", FlippedImage)
            self.image_box_1.setPixmap(QtGui.QPixmap(pix))
            
            results = self.loaded_model('data/images/temp_vid.jpg')#.save()
            results.ims
            results.render()
            for im in results.ims:
                im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
                #cv2.imshow("test", im)
                FlippedImage = im
                image = QtGui.QImage(FlippedImage, FlippedImage.shape[1],FlippedImage.shape[0], FlippedImage.shape[1] * 3, QtGui.QImage.Format_RGB888)
                pix = QtGui.QPixmap(image)
                #ConvertToQtFormat = QImage(FlippedImage.data, FlippedImage.shape[1], FlippedImage.shape[0], QImage.Format_RGB888)
                #Pic = ConvertToQtFormat.scaled(640, 640, Qt.KeepAspectRatio)
                if self.recording:
                    FlippedImage = cv2.cvtColor(FlippedImage, cv2.COLOR_BGR2RGB)
                    cv2.imwrite("detections/cache/" + str(time.time()) + ".jpg", FlippedImage)
                self.image_box_2.setPixmap(QtGui.QPixmap(pix))
            self.curr_framecount += 1
            if self.curr_framecount == self.curr_maxframe:
                self.vid_running = False
                #Save Video
    def show_video_cam(self):
        # reading the input using the camera
        result, image = None, None
        if self.cam_running:
            result, image = self.cap_video.read()

        # If image will detected without any error, 
        # show result
        if result:
            im0 = image
            im0 = cv2.cvtColor(im0, cv2.COLOR_BGR2RGB)
            FlippedImage = im0
            image = QtGui.QImage(FlippedImage, FlippedImage.shape[1],FlippedImage.shape[0], FlippedImage.shape[1] * 3, QtGui.QImage.Format_RGB888)
            pix = QtGui.QPixmap(image)
            #ConvertToQtFormat = QImage(FlippedImage.data, FlippedImage.shape[1], FlippedImage.shape[0], QImage.Format_RGB888)
            #Pic = ConvertToQtFormat.scaled(640, 640, Qt.KeepAspectRatio)
            #cv2.imshow("test", FlippedImage)
            #FlippedImage = cv2.cvtColor(FlippedImage, cv2.COLOR_BGR2RGB)
            cv2.imwrite("data/images/temp_cam.jpg", FlippedImage)
            self.image_box_1.setPixmap(QtGui.QPixmap(pix))
            
            results = self.loaded_model('data/images/temp_cam.jpg')#.save()
            results.ims
            results.render()
            for im in results.ims:
                im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
                #cv2.imshow("test", im)
                FlippedImage = im
                image = QtGui.QImage(FlippedImage, FlippedImage.shape[1],FlippedImage.shape[0], FlippedImage.shape[1] * 3, QtGui.QImage.Format_RGB888)
                pix = QtGui.QPixmap(image)
                #ConvertToQtFormat = QImage(FlippedImage.data, FlippedImage.shape[1], FlippedImage.shape[0], QImage.Format_RGB888)
                #Pic = ConvertToQtFormat.scaled(640, 640, Qt.KeepAspectRatio)
                #cv2.imshow("test", FlippedImage)
                if self.recording:
                    FlippedImage = cv2.cvtColor(FlippedImage, cv2.COLOR_BGR2RGB)
                    cv2.imwrite("detections/cache/" + str(time.time()) + ".jpg", FlippedImage)
                self.image_box_2.setPixmap(QtGui.QPixmap(pix))
                
    def record(self):
        _translate = QtCore.QCoreApplication.translate
        self.recording = not self.recording
        if self.recording:
            self.button_record.setText(_translate("MainWindow", "Recording..."))
        else:
            self.button_record.setText(_translate("MainWindow", "Record"))
        
    def save(self):
        if self.selected == 'video':
            dir = 'detections/videos'
            if not os.path.exists(dir):
                #shutil.rmtree(dir)
                os.makedirs(dir)
            
            try:
                dimensions = None
                for filename in glob.glob('detections/cache/*.jpg'):
                    img = cv2.imread(filename)
                    dimensions = img.shape
                    break
                print("Saving...")
                frameSize = (dimensions[1], dimensions[0])
                
                #fourcc = cv2.VideoWriter_fourcc(*'MJPG')
                out = cv2.VideoWriter('detections/videos/' + str(time.time()) + ".mp4",cv2.VideoWriter_fourcc(*'mpv4'), int(self.curr_fps), frameSize)

                for filename in glob.glob('detections/cache/*.jpg'):
                    print(filename)
                    
                    img = cv2.imread(filename)
                    #cv2.imshow('test', img)
                    out.write(img)
                print("Saved!")
                out.release()
            except Exception as e:
                print(e)
        if self.selected == 'cam':
            dir = 'detections/cams'
            if not os.path.exists(dir):
                #shutil.rmtree(dir)
                os.makedirs(dir)
            
            try:
                dimensions = None
                for filename in glob.glob('detections/cache/*.jpg'):
                    img = cv2.imread(filename)
                    dimensions = img.shape
                    break
                print("Saving...")
                frameSize = (dimensions[1], dimensions[0])
                
                #fourcc = cv2.VideoWriter_fourcc(*'MJPG')
                out = cv2.VideoWriter('detections/cams/' + str(time.time()) + ".mp4",cv2.VideoWriter_fourcc(*'mpv4'), int(self.curr_fps), frameSize)

                for filename in glob.glob('detections/cache/*.jpg'):
                    print(filename)
                    
                    img = cv2.imread(filename)
                    #cv2.imshow('test', img)
                    out.write(img)
                print("Saved!")
                out.release()
            except Exception as e:
                print(e)
        
    def load_model(self):
        try:
            self.openfile_name_model, some = QtWidgets.QFileDialog.getOpenFileName(None, 'yolov5.pt', 'weights', "*.pt")
        except OSError as reason:
            print(str(reason))
        else:
            if self.openfile_name_model:
                print(self.openfile_name_model)
                
                try:
                    self.loaded_model = torch.hub.load('ultralytics/yolov5', 'custom', path=self.openfile_name_model, force_reload=True)
                except:
                    self.loaded_model = torch.hub.load(r'D:\yolo\yolov5-master\weights', 'custom', path=self.openfile_name_model, force_reload=True)
                # Images
                #img = "C:\\Users\\NakaMura\\Desktop\\Screenshot 2022-11-27 223302.jpg"  # or file, Path, PIL, OpenCV, numpy, list
                
                # Inference
                #results = model(img)
                
                # Results
                #results.save()  # or .show(), .save(), .crop(), .pandas(), etc.
                
                #QtWidgets.QMessageBox.warning(self, u"Ok!", u"loading complete！", buttons=QtWidgets.QMessageBox.Ok, defaultButton=QtWidgets.QMessageBox.Ok)
                self.output_box.append("Model loading complete!")
                self.button_load_image.setDisabled(False)
                self.button_load_video.setDisabled(False)
                self.button_load_camera.setDisabled(False)
            else:
                #QtWidgets.QMessageBox.warning(self, u"Warning", u"无权重文件，请先选择权重文件，否则会发生未知错误。", buttons=QtWidgets.QMessageBox.Ok, defaultButton=QtWidgets.QMessageBox.Ok)
                self.output_box.append("Warning!")
        # self.model_init(self,  **self.openfile_name_model )
        
    def initialize(self):
        self.init_slots()
        self.timer.timeout.connect(self.show_video_cam)
        self.timer.timeout.connect(self.show_video)
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(903, 431)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.button_load_model = QtWidgets.QPushButton(self.centralwidget)
        self.button_load_model.setGeometry(QtCore.QRect(10, 50, 131, 31))
        self.button_load_model.setObjectName("button_load_model")
        self.button_load_image = QtWidgets.QPushButton(self.centralwidget)
        self.button_load_image.setGeometry(QtCore.QRect(10, 90, 131, 31))
        self.button_load_image.setObjectName("button_load_image")
        self.button_load_video = QtWidgets.QPushButton(self.centralwidget)
        self.button_load_video.setGeometry(QtCore.QRect(10, 130, 131, 31))
        self.button_load_video.setObjectName("button_load_video")
        self.button_load_camera = QtWidgets.QPushButton(self.centralwidget)
        self.button_load_camera.setGeometry(QtCore.QRect(10, 170, 131, 31))
        self.button_load_camera.setObjectName("button_load_camera")
        self.button_record = QtWidgets.QPushButton(self.centralwidget)
        self.button_record.setGeometry(QtCore.QRect(10, 210, 131, 31))
        self.button_record.setObjectName("button_record")
        self.output_box = QtWidgets.QTextEdit(self.centralwidget)
        self.output_box.setGeometry(QtCore.QRect(10, 290, 131, 121))
        self.output_box.setObjectName("output_box")
        self.image_box_1 = ScaledPixmapLabel(MainWindow)
        self.image_box_1.setGeometry(QtCore.QRect(160, 50, 361, 361))
        self.image_box_1.setFrameShape(QtWidgets.QFrame.Box)
        self.image_box_1.setText("")
        self.image_box_1.setObjectName("image_box_1")
        self.image_box_1.setScaledContents(True)
        self.image_box_2 = ScaledPixmapLabel(MainWindow)
        self.image_box_2.setGeometry(QtCore.QRect(530, 50, 361, 361))
        self.image_box_2.setFrameShape(QtWidgets.QFrame.Box)
        self.image_box_2.setText("")
        self.image_box_2.setObjectName("image_box_2")
        self.image_box_2.setScaledContents(True)
        self.image_label_1 = QtWidgets.QLabel(self.centralwidget)
        self.image_label_1.setGeometry(QtCore.QRect(260, 20, 131, 21))
        self.image_label_1.setAlignment(QtCore.Qt.AlignCenter)
        self.image_label_1.setObjectName("image_label_1")
        self.image_label_2 = QtWidgets.QLabel(self.centralwidget)
        self.image_label_2.setGeometry(QtCore.QRect(650, 20, 131, 21))
        self.image_label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.image_label_2.setObjectName("image_label_2")
        self.button_save = QtWidgets.QPushButton(self.centralwidget)
        self.button_save.setGeometry(QtCore.QRect(10, 250, 131, 31))
        self.button_save.setObjectName("button_save")
        MainWindow.setCentralWidget(self.centralwidget)
        
        self.initialize()
        
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.button_load_model.setText(_translate("MainWindow", "Load Model"))
        self.button_load_image.setText(_translate("MainWindow", "Load Image"))
        self.button_load_video.setText(_translate("MainWindow", "Load Video"))
        self.button_load_camera.setText(_translate("MainWindow", "Load Camera"))
        self.button_record.setText(_translate("MainWindow", "Record"))
        self.image_label_1.setText(_translate("MainWindow", "Image 1"))
        self.image_label_2.setText(_translate("MainWindow", "Image 2"))
        self.button_save.setText(_translate("MainWindow", "Save"))
        

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
