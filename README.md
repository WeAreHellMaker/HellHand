# Description

This repository features a Python-based interface designed to control a robotic hand via an Arduino microcontroller. The system leverages Python's high-level processing power to calculate movements and sends precise commands to the Arduino over Serial communication (UART) to drive servo motors.

![HellHand Gear](https://raw.githubusercontent.com/WeAreHellMaker/HellHand/main/images/HellHand_Gear_1.jpg)

<table align="center">
  <tr>
    <td align="center">
      <img src="https://raw.githubusercontent.com/WeAreHellMaker/HellHand/main/images/HellHand_Gear_1.jpg" width="200"><br>
      <sub><b>기어 파츠 1단계</b><br>메인 동력 전달부</sub>
    </td>
    <td align="center">
      <img src="https://raw.githubusercontent.com/WeAreHellMaker/HellHand/main/images/HellHand_Gear_2.jpg" width="200"><br>
      <sub><b>기어 파츠 2단계</b><br>관절 구동 메커니즘</sub>
    </td>
    <td align="center">
      <img src="https://raw.githubusercontent.com/WeAreHellMaker/HellHand/main/images/HellHand_Gear_3.jpg" width="200"><br>
      <sub><b>기어 파츠 3단계</b><br>최종 조립 완료</sub>
    </td>
  </tr>
</table>

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
