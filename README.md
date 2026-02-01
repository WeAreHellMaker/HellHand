# 🦾 HellHand: Real-time Biomimetic Robot Hand

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green.svg)

**HellHand**는 Python 기반의 Computer Vision 기술을 활용하여 사람의 손동작을 실시간으로 추적하고 미러링하는 지능형 로봇 손 프로젝트입니다. 

단순한 관절 구동을 넘어, 사용자의 움직임을 데이터화하여 로봇에 즉각적으로 투영하는 **Embodied AI(체감형 AI)**의 기초를 목표로 제작되었습니다.


<table align="center">
  <tr>
    <td align="center">
      <img src="https://raw.githubusercontent.com/WeAreHellMaker/HellHand/main/images/HellHand_Gear_1.jpg" width="200"><br>
      <sub><b>Hell Hand Gear</b><br>Front</sub>
    </td>
    <td align="center">
      <img src="https://raw.githubusercontent.com/WeAreHellMaker/HellHand/main/images/HellHand_Gear_2.jpg" width="200"><br>
      <sub><b>Hell Hand Gear</b><br>Back</sub>
    </td>
    <td align="center">
      <img src="https://raw.githubusercontent.com/WeAreHellMaker/HellHand/main/images/HellHand_Gear_3.jpg" width="200"><br>
      <sub><b>Hell Hand Gear</b><br>Side</sub>
    </td>
  </tr>
</table>


## 📸 Full Assembly Overview
전체 조립 부품 구성도입니다. 모든 메커니즘은 정밀한 동력 전달을 위한 기어 시스템을 기반으로 설계되었습니다.

<div align="center">
  <img src="https://raw.githubusercontent.com/WeAreHellMaker/HellHand/main/images/HellHand_Gear_Part.jpg" width="400">
  <p><b>Full Assembly Parts List</b></p>
  <p><i>3D Printed / Servo  / Microcontroller Unit / Etc</i></p>
</div>


### 📦 Components Specification (부품 구성)

<div align="center">
  <img src="https://raw.githubusercontent.com/WeAreHellMaker/HellHand/main/images/HellHand_Gear_PartsList.jpg" width="500">
  <p><b>Parts List</b></p>
</div>


# System Architecture

Python Host: Processes input (GUI, Computer Vision, or Scripts) and calculates joint angles.
Serial Bridge: Sends data packets (e.g., <90, 45, 180...>) to the Arduino.
Arduino Firmware: Receives commands and generates PWM signals to control the robotic fingers.

# Key Features:

Firmware Optimized for Arduino: Lightweight C++ code for stable motor control.
Serial Protocol: Robust communication between Python and Arduino using pySerial.
Dynamic Mapping: Easily map Python-calculated values to 0-180 degree servo angles.

Plug & Play: Auto-detection of COM/tty ports for quick setup.

Technical Stack:

Software: Python 3.x, pySerial

Hardware: Arduino (Uno/Nano/Mega), Servo Motors (MG996R/SG90), External 5V/6V Power Supply
