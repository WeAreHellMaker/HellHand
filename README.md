# Description

This repository features a Python-based interface designed to control a robotic hand via an Arduino microcontroller. The system leverages Python's high-level processing power to calculate movements and sends precise commands to the Arduino over Serial communication (UART) to drive servo motors.

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


<div align="center">
  <img src="https://raw.githubusercontent.com/WeAreHellMaker/HellHand/main/images/HellHand_Gear_Part.jpg" width="600">
  <p><b>Full Assembly Parts List</b></p>
  <p><i>3D Printed / Servo  / Microcontroller Unit / Etc</i></p>
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
