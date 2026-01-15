#!/usr/bin/env python
# -*- coding: utf-8 -*-
import copy
import argparse

import cv2 as cv
import numpy as np
import mediapipe as mp

from utils import CvFpsCalc

import math
import time
import serial


import tkinter as tk
from tkinter import ttk
import serial.tools.list_ports

#-------------------------------------------------------------------
#   FingerControl Calss
#-------------------------------------------------------------------
class FingerControl:
    def __init__(self, com="COM5"):
        com="COM7"

        self.__time_tick_right = time.time();
        self.__time_tick_left = time.time();

        self.__servo_angle_right  = [0, 0, 0, 0, 0];
        self.__servo_angle_left   = [0, 0, 0, 0, 0];

        self.serial_port = serial.Serial(com, 115200);




    def __vector_length(self, v):
        return math.sqrt(sum(x*x for x in v))

    def __dot_product(self, v1, v2):
        return sum(x*y for x, y in zip(v1, v2))

    def __angle_between_vectors(self, v1, v2):
        dot_prod  = self.__dot_product(v1, v2)
        v1_length = self.__vector_length(v1)
        v2_length = self.__vector_length(v2)
        angle_rad = math.acos(dot_prod / (v1_length * v2_length))

        return math.degrees(angle_rad)

    def __finger_angle(self, x1, x2, q1, q2 ):    
        vector_A = [(x2.x - x1.x), (x2.y - x1.y), (x2.z - x1.z)]
        vector_B = [(q2.x - q1.x), (q2.y - q1.y), (q2.z - q1.z)]

        angle = self.__angle_between_vectors(vector_A, vector_B)

        return angle;
    

    def __linear_transform(self, x, a_min, a_max, b_min, b_max):

        x = max( min( x, a_max ), a_min);
        return (x - a_min) * (b_max - b_min) / (a_max - a_min) + b_min;
    
    def __serial_write_right(self, servo_angle ) : 

        cmd = "FR0%03d1%03d2%03d3%03d4%03d\n" % (servo_angle[0], servo_angle[1], servo_angle[2], servo_angle[3], servo_angle[4] );
        print( cmd.encode() );

        self.serial_port.write( cmd.encode() );

    def __serial_write_left(self, servo_angle ) : 

        cmd = "FL5%03d6%03d7%03d8%03d9%03d\n" % (servo_angle[0], servo_angle[1], servo_angle[2], servo_angle[3], servo_angle[4] );
        print( cmd.encode() );

        self.serial_port.write( cmd.encode() );

    #---------------------------------------------------------------------------
    #   finger robot right
    #---------------------------------------------------------------------------
    def  finger_robot_right(self, world_landmarks) :
        world_angle = [0, 0, 0, 0, 0];
        servo_angle = [0, 0, 0, 0, 0];

        world_angle[0] = self.__finger_angle( world_landmarks.landmark[ 2], world_landmarks.landmark[ 3], world_landmarks.landmark[ 2], world_landmarks.landmark[17] ); # 엄지 : 2 -> 4  / 2 -> 17                
        world_angle[1] = self.__finger_angle( world_landmarks.landmark[ 5], world_landmarks.landmark[ 8], world_landmarks.landmark[ 5], world_landmarks.landmark[ 0] ); # 검지 : 5 -> 8  / 5 -> 0
        world_angle[2] = self.__finger_angle( world_landmarks.landmark[ 9], world_landmarks.landmark[12], world_landmarks.landmark[ 9], world_landmarks.landmark[ 0] ); # 중지 : 9 -> 12 / 9 -> 0
        world_angle[3] = self.__finger_angle( world_landmarks.landmark[13], world_landmarks.landmark[16], world_landmarks.landmark[13], world_landmarks.landmark[ 0] ); # 약지 : 13 -> 16 / 13 -> 0
        world_angle[4] = self.__finger_angle( world_landmarks.landmark[17], world_landmarks.landmark[20], world_landmarks.landmark[17], world_landmarks.landmark[ 0] ); # 소지 : 17 -> 20 / 17 -> 0

        servo_angle[0] = self.__linear_transform( world_angle[0], 60, 120, 90,  0 );

        servo_angle[1] = self.__linear_transform( world_angle[1], 30, 160, 180, 0 );
        servo_angle[2] = self.__linear_transform( world_angle[2], 30, 160, 0, 180 );
        servo_angle[3] = self.__linear_transform( world_angle[3], 30, 160, 180, 0 );
        servo_angle[4] = self.__linear_transform( world_angle[4], 30, 160, 0, 180 );

        time_now = time.time();

        bSendSerial = False;


        for index in range(5) :
            if abs( self.__servo_angle_right[index] - servo_angle[index] ) >= 30 :
                bSendSerial = True;
                break;
        

        if ( time_now - self.__time_tick_right  ) >= 0.03 and  bSendSerial :
            self.__time_tick_right = time_now;
                       
            self.__serial_write_right(servo_angle);


            self.__servo_angle_right  =  servo_angle;
        


        return world_angle, servo_angle;  

    #---------------------------------------------------------------------------
    #   finger robot left
    #---------------------------------------------------------------------------
    def  finger_robot_left(self, world_landmarks) :
        world_angle = [0, 0, 0, 0, 0];
        servo_angle = [0, 0, 0, 0, 0];

        world_angle[0] = self.__finger_angle( world_landmarks.landmark[ 2], world_landmarks.landmark[ 3], world_landmarks.landmark[ 2], world_landmarks.landmark[17] ); # 엄지 : 2 -> 4  / 2 -> 17                
        world_angle[1] = self.__finger_angle( world_landmarks.landmark[ 5], world_landmarks.landmark[ 8], world_landmarks.landmark[ 5], world_landmarks.landmark[ 0] ); # 검지 : 5 -> 8  / 5 -> 0
        world_angle[2] = self.__finger_angle( world_landmarks.landmark[ 9], world_landmarks.landmark[12], world_landmarks.landmark[ 9], world_landmarks.landmark[ 0] ); # 중지 : 9 -> 12 / 9 -> 0
        world_angle[3] = self.__finger_angle( world_landmarks.landmark[13], world_landmarks.landmark[16], world_landmarks.landmark[13], world_landmarks.landmark[ 0] ); # 약지 : 13 -> 16 / 13 -> 0
        world_angle[4] = self.__finger_angle( world_landmarks.landmark[17], world_landmarks.landmark[20], world_landmarks.landmark[17], world_landmarks.landmark[ 0] ); # 소지 : 17 -> 20 / 17 -> 0

        servo_angle[0] = self.__linear_transform( world_angle[0], 60, 110, 180, 0 );

        servo_angle[1] = self.__linear_transform( world_angle[1], 30, 160, 0, 180 );
        servo_angle[2] = self.__linear_transform( world_angle[2], 30, 160, 0, 180 );
        servo_angle[3] = self.__linear_transform( world_angle[3], 30, 160, 180, 0 );
        servo_angle[4] = self.__linear_transform( world_angle[4], 30, 160, 0, 180 );

        time_now = time.time();


        bSendSerial = False;

        for index in range(5) :
            if abs( self.__servo_angle_right[index] - servo_angle[index] ) >= 25 :
                bSendSerial = True;
                break;

        if ( time_now - self.__time_tick_left  ) >= 0.03 and  bSendSerial :
            self.__time_tick_left = time_now;
                       
            self.__serial_write_left(servo_angle);


            self.__servo_angle_right  =  servo_angle;
        

        return world_angle, servo_angle;



#
#   Call Class
#
FingerControl = FingerControl();



   



################################################################################
#
################################################################################
def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--device", type=int, default=0)
    parser.add_argument("--width", help='cap width', type=int, default=960)
    parser.add_argument("--height", help='cap height', type=int, default=540)

    parser.add_argument("--model_complexity",
                        help='model_complexity(0,1(default))',
                        type=int,
                        default=1)

    parser.add_argument("--max_num_hands", type=int, default=2)
    parser.add_argument("--min_detection_confidence",
                        help='min_detection_confidence',
                        type=float,
                        default=0.7)
    parser.add_argument("--min_tracking_confidence",
                        help='min_tracking_confidence',
                        type=int,
                        default=0.5)

    parser.add_argument('--use_brect', action='store_true')
    parser.add_argument('--plot_world_landmark', action='store_true')

    args = parser.parse_args()

    return args






def get_serial_ports():
    """연결된 시리얼 포트 목록을 가져옵니다."""
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

def refresh_ports():
    """포트 목록을 새로고침합니다."""
    port_list = get_serial_ports()
    combo_port['values'] = port_list
    if port_list:
        combo_port.set(port_list[0])
    else:
        combo_port.set("포트 없음")

def connect_serial():
    """선택된 포트로 연결 로직을 실행합니다."""
    selected_port = combo_port.get()
    if selected_port and selected_port != "포트 없음":
        label_status.config(text=f"연결 시도 중: {selected_port}", fg="blue")
        # 여기서 실제로 serial.Serial(selected_port, baudrate=9600) 등을 실행합니다.
    else:
        label_status.config(text="선택된 포트가 없습니다.", fg="red")

################################################################################
#   Main
################################################################################
def main():










    #---------------------------------------------------------------------------
    #   인수 해석
    #---------------------------------------------------------------------------
    args = get_args()

    cap_device  = args.device
    cap_width   = args.width
    cap_height  = args.height

    model_complexity = args.model_complexity

    max_num_hands = args.max_num_hands
    min_detection_confidence = args.min_detection_confidence
    min_tracking_confidence = args.min_tracking_confidence

    use_brect = args.use_brect
    plot_world_landmark = args.plot_world_landmark


    #---------------------------------------------------------------------------
    #   카메라 준비
    #---------------------------------------------------------------------------  
    
    cap = cv.VideoCapture(cap_device, cv.CAP_DSHOW)
    
    cap.set(cv.CAP_PROP_FRAME_WIDTH, cap_width )
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, cap_height )

    #---------------------------------------------------------------------------
    #   모델 로드
    #---------------------------------------------------------------------------
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        model_complexity=model_complexity,
        max_num_hands=max_num_hands,
        min_detection_confidence=min_detection_confidence,
        min_tracking_confidence=min_tracking_confidence,
    )

    #---------------------------------------------------------------------------
    #   FPS 측정 모듈
    #---------------------------------------------------------------------------    
    cvFpsCalc = CvFpsCalc(buffer_len=10)

    #---------------------------------------------------------------------------    
    #   World 좌표 플롯
    #---------------------------------------------------------------------------        
    if plot_world_landmark:
        import matplotlib.pyplot as plt

        fig = plt.figure()
        r_ax = fig.add_subplot(121, projection="3d")
        l_ax = fig.add_subplot(122, projection="3d")
        fig.subplots_adjust(left=0.0, right=1, bottom=0, top=1)

    while True:
        display_fps = cvFpsCalc.get()

        #   카메라 캡처
        ret, image = cap.read()
        if not ret:
            break

        image = cv.flip(image, 1)  #    미러 표시
        debug_image = copy.deepcopy(image)

        #   검출 실시
        image = cv.cvtColor(image, cv.COLOR_BGR2RGB)

        results = hands.process(image)


        #   그리기
        if results.multi_hand_landmarks is not None:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks,
                                                  results.multi_handedness):
                #   손의 평중심 계산
                cx, cy = calc_palm_moment(debug_image, hand_landmarks)

                #   외접 직사각형의 계산
                brect = calc_bounding_rect(debug_image, hand_landmarks)

                #   그리기
                debug_image = draw_landmarks(debug_image, cx, cy,
                                             hand_landmarks, handedness)
                
                debug_image = draw_bounding_rect(use_brect, debug_image, brect)

        cv.putText(debug_image, "FPS:" + str(display_fps), (10, 30),
                   cv.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2, cv.LINE_AA)
    




        #-----------------------------------------------------------------------
        #  World 좌표
        #-----------------------------------------------------------------------
        if results.multi_hand_world_landmarks is not None:

            #-------------------------------------------------------------------
            # World좌표 표시
            #-------------------------------------------------------------------
            if plot_world_landmark:
                plot_world_landmarks(
                    plt,
                    [r_ax, l_ax],
                    results.multi_hand_world_landmarks,
                    results.multi_handedness,
                )

            #-------------------------------------------------------------------
            # Hand Robot Control
            #-------------------------------------------------------------------
            work_left   = False;            
            work_right  = False;
            
            for landmarks, handedness in zip(results.multi_hand_world_landmarks, results.multi_handedness):
                
                #---------------------------------------------------------------
                #   Left
                #---------------------------------------------------------------
                if handedness.classification[0].label == 'Left' and not work_left:

                    work_left = True;
                    world_angle, servo_angle =  FingerControl.finger_robot_left(landmarks);

                #---------------------------------------------------------------
                #   Right
                #---------------------------------------------------------------
                elif handedness.classification[0].label == 'Right' and not work_right:

                    work_right = True;
                    world_angle, servo_angle =  FingerControl.finger_robot_right(landmarks);
                                   
        #-----------------------------------------------------------------------
        #   키 처리(ESC：종료)
        #-----------------------------------------------------------------------        
        key = cv.waitKey(1)
        if key == 27:  # ESC
            break

        #-----------------------------------------------------------------------
        #   화면 출력
        #-----------------------------------------------------------------------
        cv.namedWindow('Hell Hand', cv.WINDOW_NORMAL)
        cv.setWindowProperty('Hell Hand', cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)
            
        cv.imshow('Hell Hand', debug_image)

    cap.release()
    cv.destroyAllWindows()

################################################################################
#
################################################################################
def calc_palm_moment(image, landmarks):
    image_width, image_height = image.shape[1], image.shape[0]

    palm_array = np.empty((0, 2), int)

    for index, landmark in enumerate(landmarks.landmark):
        landmark_x = min(int(landmark.x * image_width), image_width - 1)
        landmark_y = min(int(landmark.y * image_height), image_height - 1)

        landmark_point = [np.array((landmark_x, landmark_y))]

        if index == 0:  #   손목 1
            palm_array = np.append(palm_array, landmark_point, axis=0)
        if index == 1:  #   손목 2
            palm_array = np.append(palm_array, landmark_point, axis=0)
        if index == 5:  #   검지:지근
            palm_array = np.append(palm_array, landmark_point, axis=0)
        if index == 9:  #   가운데 손가락: 뿌리
            palm_array = np.append(palm_array, landmark_point, axis=0)
        if index == 13: #   약지 : 뿌리
            palm_array = np.append(palm_array, landmark_point, axis=0)
        if index == 17: #   새끼 손가락: 뿌리
            palm_array = np.append(palm_array, landmark_point, axis=0)

    M = cv.moments(palm_array)
    cx, cy = 0, 0
    if M['m00'] != 0:
        cx = int(M['m10'] / M['m00'])
        cy = int(M['m01'] / M['m00'])

    return cx, cy

################################################################################
#
################################################################################
def calc_bounding_rect(image, landmarks):
    image_width, image_height = image.shape[1], image.shape[0]

    landmark_array = np.empty((0, 2), int)

    for _, landmark in enumerate(landmarks.landmark):
        landmark_x = min(int(landmark.x * image_width), image_width - 1)
        landmark_y = min(int(landmark.y * image_height), image_height - 1)

        landmark_point = [np.array((landmark_x, landmark_y))]

        landmark_array = np.append(landmark_array, landmark_point, axis=0)

    x, y, w, h = cv.boundingRect(landmark_array)

    return [x, y, x + w, y + h]

################################################################################
#
################################################################################
def draw_landmarks(image, cx, cy, landmarks, handedness):
    image_width, image_height = image.shape[1], image.shape[0]

    landmark_point = []

    #   키포인트
    for index, landmark in enumerate(landmarks.landmark):
        if landmark.visibility < 0 or landmark.presence < 0:
            continue

        landmark_x = min(int(landmark.x * image_width), image_width - 1)
        landmark_y = min(int(landmark.y * image_height), image_height - 1)
        # landmark_z = landmark.z

        landmark_point.append((landmark_x, landmark_y))

        if index == 0:  #   손목 1
            cv.circle(image, (landmark_x, landmark_y),  5, (0, 255, 0), 1)
        if index == 1:  #   손목 2
            cv.circle(image, (landmark_x, landmark_y),  5, (0, 255, 0), 1)
        if index == 2:  #   엄지: 뿌리
            cv.circle(image, (landmark_x, landmark_y),  5, (0, 255, 0), 1)
        if index == 3:  #   엄지: 첫 번째 관절
            cv.circle(image, (landmark_x, landmark_y),  5, (0, 255, 0), 1)
        if index == 4:  #   엄지: 손가락 끝
            cv.circle(image, (landmark_x, landmark_y),  5, (0, 255, 0), 1)
            cv.circle(image, (landmark_x, landmark_y), 12, (0, 255, 0), 1)
        if index == 5:  #   검지:지근
            cv.circle(image, (landmark_x, landmark_y),  5, (0, 255, 0), 1)
        if index == 6:  #   검지: 두 번째 관절
            cv.circle(image, (landmark_x, landmark_y),  5, (0, 255, 0), 1)
        if index == 7:  #   검지: 첫 번째 관절
            cv.circle(image, (landmark_x, landmark_y),  5, (0, 255, 0), 1)
        if index == 8:  #   검지: 손가락 끝
            cv.circle(image, (landmark_x, landmark_y),  5, (0, 255, 0), 1)
            cv.circle(image, (landmark_x, landmark_y), 12, (0, 255, 0), 1)
        if index == 9:  #   가운데 손가락: 뿌리
            cv.circle(image, (landmark_x, landmark_y),  5, (0, 255, 0), 1)
        if index == 10: #   가운데 손가락: 두 번째 관절
            cv.circle(image, (landmark_x, landmark_y),  5, (0, 255, 0), 1)
        if index == 11: #   가운데 손가락: 첫 번째 관절
            cv.circle(image, (landmark_x, landmark_y),  5, (0, 255, 0), 1)
        if index == 12: #   가운데 손가락: 먼저 가리킨다
            cv.circle(image, (landmark_x, landmark_y),  5, (0, 255, 0), 1)
            cv.circle(image, (landmark_x, landmark_y), 12, (0, 255, 0), 1)
        if index == 13: #   약지 : 뿌리
            cv.circle(image, (landmark_x, landmark_y),  5, (0, 255, 0), 1)
        if index == 14: #   약지 : 두 번째 관절
            cv.circle(image, (landmark_x, landmark_y),  5, (0, 255, 0), 1)
        if index == 15: #   약지 : 첫 번째 관절
            cv.circle(image, (landmark_x, landmark_y),  5, (0, 255, 0), 1)
        if index == 16: #   약지 : 손가락 끝
            cv.circle(image, (landmark_x, landmark_y),  5, (0, 255, 0), 1)
            cv.circle(image, (landmark_x, landmark_y), 12, (0, 255, 0), 1)
        if index == 17: #   새끼 손가락: 뿌리
            cv.circle(image, (landmark_x, landmark_y),  5, (0, 255, 0), 1)
        if index == 18: #   새끼 손가락 : 두 번째 관절
            cv.circle(image, (landmark_x, landmark_y),  5, (0, 255, 0), 1)
        if index == 19: #   새끼 손가락: 첫 번째 관절
            cv.circle(image, (landmark_x, landmark_y),  5, (0, 255, 0), 1)
        if index == 20: #   새끼손가락: 먼저 가리킨다
            cv.circle(image, (landmark_x, landmark_y),  5, (0, 255, 0), 1)
            cv.circle(image, (landmark_x, landmark_y), 12, (0, 255, 0), 1)
        
    #---------------------------------------------------------------------------
    #   연결선
    #---------------------------------------------------------------------------    
    if len(landmark_point) > 0:
        #   엄지손가락
        cv.line(image, landmark_point[ 2], landmark_point[ 3], (0, 255, 0), 1)
        cv.line(image, landmark_point[ 3], landmark_point[ 4], (0, 255, 0), 1)

        #   검지
        cv.line(image, landmark_point[ 5], landmark_point[ 6], (0, 255, 0), 1)
        cv.line(image, landmark_point[ 6], landmark_point[ 7], (0, 255, 0), 1)
        cv.line(image, landmark_point[ 7], landmark_point[ 8], (0, 255, 0), 1)

        #   가운데 손가락
        cv.line(image, landmark_point[ 9], landmark_point[10], (0, 255, 0), 1)
        cv.line(image, landmark_point[10], landmark_point[11], (0, 255, 0), 1)
        cv.line(image, landmark_point[11], landmark_point[12], (0, 255, 0), 1)

        #   약지
        cv.line(image, landmark_point[13], landmark_point[14], (0, 255, 0), 1)
        cv.line(image, landmark_point[14], landmark_point[15], (0, 255, 0), 1)
        cv.line(image, landmark_point[15], landmark_point[16], (0, 255, 0), 1)

        #   새끼 손가락
        cv.line(image, landmark_point[17], landmark_point[18], (0, 255, 0), 1)
        cv.line(image, landmark_point[18], landmark_point[19], (0, 255, 0), 1)
        cv.line(image, landmark_point[19], landmark_point[20], (0, 255, 0), 1)

        #   손의 평
        cv.line(image, landmark_point[ 0], landmark_point[ 1], (0, 255, 0), 1)
        cv.line(image, landmark_point[ 1], landmark_point[ 2], (0, 255, 0), 1)
        cv.line(image, landmark_point[ 2], landmark_point[ 5], (0, 255, 0), 1)
        cv.line(image, landmark_point[ 5], landmark_point[ 9], (0, 255, 0), 1)
        cv.line(image, landmark_point[ 9], landmark_point[13], (0, 255, 0), 1)
        cv.line(image, landmark_point[13], landmark_point[17], (0, 255, 0), 1)
        cv.line(image, landmark_point[17], landmark_point[ 0], (0, 255, 0), 1)

    #   무게중심 + 좌우
    if len(landmark_point) > 0:
        # handedness.classification[0].index
        # handedness.classification[0].score

        cv.circle(image, (cx, cy), 12, (0, 0, 255), 1)

        # label[0]:첫 글자만
        cv.putText(image, handedness.classification[0].label[0],
                   (cx - 6, cy + 6), cv.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255),
                   1, cv.LINE_AA) 
        
    return image


################################################################################
#
################################################################################
def plot_world_landmarks(
    plt,
    ax_list,
    multi_hands_landmarks,
    multi_handedness,
    visibility_th=0.5,
):
    ax_list[0].cla()
    ax_list[0].set_xlim3d(-0.1, 0.1)
    ax_list[0].set_ylim3d(-0.1, 0.1)
    ax_list[0].set_zlim3d(-0.1, 0.1)
    ax_list[1].cla()
    ax_list[1].set_xlim3d(-0.1, 0.1)
    ax_list[1].set_ylim3d(-0.1, 0.1)
    ax_list[1].set_zlim3d(-0.1, 0.1)

    for landmarks, handedness in zip(multi_hands_landmarks, multi_handedness):
        handedness_index = 0
        
        if handedness.classification[0].label == 'Left':
            handedness_index = 0
        elif handedness.classification[0].label == 'Right':
            handedness_index = 1

        landmark_point = []

        for index, landmark in enumerate(landmarks.landmark):
            landmark_point.append(
                [landmark.visibility, (landmark.x, landmark.y, landmark.z)])

        palm_list = [0, 1, 5, 9, 13, 17, 0]
        thumb_list = [1, 2, 3, 4]
        index_finger_list = [5, 6, 7, 8]
        middle_finger_list = [9, 10, 11, 12]
        ring_finger_list = [13, 14, 15, 16]
        pinky_list = [17, 18, 19, 20]

        #   손바닥
        palm_x, palm_y, palm_z = [], [], []
        for index in palm_list:
            point = landmark_point[index][1]
            palm_x.append(point[0])
            palm_y.append(point[2])
            palm_z.append(point[1] * (-1))

        #   엄지손가락
        thumb_x, thumb_y, thumb_z = [], [], []
        for index in thumb_list:
            point = landmark_point[index][1]
            thumb_x.append(point[0])
            thumb_y.append(point[2])
            thumb_z.append(point[1] * (-1))

        #   집게 손가락
        index_finger_x, index_finger_y, index_finger_z = [], [], []
        for index in index_finger_list:
            point = landmark_point[index][1]
            index_finger_x.append(point[0])
            index_finger_y.append(point[2])
            index_finger_z.append(point[1] * (-1))

        #   가운데 손가락
        middle_finger_x, middle_finger_y, middle_finger_z = [], [], []
        for index in middle_finger_list:
            point = landmark_point[index][1]
            middle_finger_x.append(point[0])
            middle_finger_y.append(point[2])
            middle_finger_z.append(point[1] * (-1))

        #   약지
        ring_finger_x, ring_finger_y, ring_finger_z = [], [], []
        for index in ring_finger_list:
            point = landmark_point[index][1]
            ring_finger_x.append(point[0])
            ring_finger_y.append(point[2])
            ring_finger_z.append(point[1] * (-1))

        #   새끼 손가락
        pinky_x, pinky_y, pinky_z = [], [], []
        for index in pinky_list:
            point = landmark_point[index][1]
            pinky_x.append(point[0])
            pinky_y.append(point[2])
            pinky_z.append(point[1] * (-1))

        ax_list[handedness_index].plot(palm_x, palm_y, palm_z)
        ax_list[handedness_index].plot(thumb_x, thumb_y, thumb_z)
        ax_list[handedness_index].plot(index_finger_x, index_finger_y,
                                       index_finger_z)
        ax_list[handedness_index].plot(middle_finger_x, middle_finger_y,
                                       middle_finger_z)
        ax_list[handedness_index].plot(ring_finger_x, ring_finger_y,
                                       ring_finger_z)
        ax_list[handedness_index].plot(pinky_x, pinky_y, pinky_z)

    plt.pause(.001)

    return

################################################################################
#
################################################################################
def draw_bounding_rect(use_brect, image, brect):
    if use_brect:
        #   경계 직사각형
        cv.rectangle(image, (brect[0], brect[1]), (brect[2], brect[3]),
                     (0, 255, 0), 2)

    return image


if __name__ == '__main__':
    main()
