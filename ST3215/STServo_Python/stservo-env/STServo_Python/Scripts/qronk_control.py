import sys
import os
import time
import math
from tkinter import *

angle_1 = 180
angle_2 = 180

if os.name == 'nt':
    import msvcrt
    def getch():
        return msvcrt.getch().decode()
else:
    import sys, tty, termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    def getch():
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

sys.path.append("..")
from STservo_sdk import *                   # Uses STServo SDK library

BAUDRATE                    = 1000000           # STServo default baudrate : 1000000
DEVICENAME                  = '/dev/ttyACM0'    # When RPi connected to HAT Bus Servo by USB-C

STS_MOVING_SPEED            = 2400          # SCServo moving speed
STS_MOVING_ACC              = 50            # SCServo moving acc

# Servo IDs for relevant limbs
SHOULDER_ID = 6
FLOAT_ID = 11

# If, when looking at a motor, a clockwise motion lowers the leg from neutral, then it has a direction of 1. Reverse case, -1.
SHOULDER_DIRECT = 1
FLOAT_DIRECT = -1

# Length of limbs
L0 = 60
L1 = 100

# portHandler = PortHandler(DEVICENAME)
# packetHandler = sts(portHandler)
# groupSyncRead = GroupSyncRead(packetHandler, STS_PRESENT_POSITION_L, 11)

# # Generic function to set up ports
# def port_setup():
#     global portHandler, packetHandler
#     # Open port
#     if portHandler.openPort():
#         print("Succeeded to open the port")
#     else:
#         print("Failed to open the port")
#         print("Press any key to terminate...")
#         getch()
#         quit()

#     # Set port baudrate
#     if portHandler.setBaudRate(BAUDRATE):
#         print("Succeeded to change the baudrate")
#     else:
#         print("Failed to change the baudrate")
#         print("Press any key to terminate...")
#         getch()
#         quit()

# Convert a position in mm to a set of IK angles
def convert_position_angle(x,y):
    theta1 = math.acos((x**2 + y**2 - (L0**2 + L1**2))/(2*L0*L1))
    theta0 = math.atan2(y,x) - math.atan2(L1 * math.sin(theta1),(L0 + (L1*math.cos(theta1))))

    return (theta0, theta1)

# Converts an angle in radians into a motor angle
def rad_to_motor(value):
    return value*4095/(2*math.pi)

# Convert a set of IK angles into positions that the motors should turn to
def convert_angles_leg_motion(theta0, theta1, shoulder_direction, float_direction):
    ##TODO: validate that this position is within the range of motion achievable by the servo (r slightly less than l0 + l1)

    # Servo angle ranges from 0 to 4095, middle position is 2047
    shoulder_pos = int(2047 + (shoulder_direction * rad_to_motor(theta0)))
    float_pos = int(2047 + (float_direction * rad_to_motor(theta0 + theta1 - math.pi/2)))

    return (shoulder_pos, float_pos)

# Moves the motor to a position and halts program until it has finished moving
def go_to_angle(th0, th1):
    (a0, a1) = convert_angles_leg_motion(th0, th1, SHOULDER_DIRECT, FLOAT_DIRECT)

#     print("Shoulder pos: {}, Float pos: {}".format(a0, a1))

#     sts_addparam_result_shoulder = packetHandler.SyncWritePosEx(SHOULDER_ID, a0, STS_MOVING_SPEED, STS_MOVING_ACC)
#     sts_addparam_result_float = packetHandler.SyncWritePosEx(FLOAT_ID, a1, STS_MOVING_SPEED, STS_MOVING_ACC)

#     sts_comm_result = packetHandler.groupSyncWrite.txPacket()

#     # Clear syncwrite parameter storage
#     packetHandler.groupSyncWrite.clearParam()
#     time.sleep(0.002) #wait for servo status moving=1

#     while 1:
#         sts_addparam_result_shoulder = groupSyncRead.addParam(SHOULDER_ID)
#         sts_addparam_result_float = groupSyncRead.addParam(FLOAT_ID)

#         sts_comm_result = groupSyncRead.txRxPacket()

#         sts_last_moving = 0

#         for sts_id in (SHOULDER_ID, FLOAT_ID):
#             sts_data_result, sts_error = groupSyncRead.isAvailable(sts_id, STS_PRESENT_POSITION_L, 11)
            
#             if sts_data_result == True and groupSyncRead.getData(sts_id, STS_MOVING, 1) == 1:
#                 sts_last_moving = 1

#         groupSyncRead.clearParam()
#         if sts_last_moving==0:
#             break

def update_motor_1(a):
    angle_1 = int(a)
    go_to_angle(angle_1, angle_2)

def update_motor_2(a):
    angle_2 = int(a)
    go_to_angle(angle_1, angle_2)

# Main loop: add the actual code in here
if __name__ == "__main__":
    # port_setup()

    root = Tk()
    root.geometry("400x300")

    scale_1 = Scale(root, from_=0, to=360, resolution=1, orient=HORIZONTAL, label="Motor 1", command=update_motor_1)
    scale_2 = Scale(root, from_=0, to=360, resolution=1, orient=HORIZONTAL, label="Motor 2", command=update_motor_2)

    scale_1.pack(anchor=CENTER)
    scale_2.pack(anchor=CENTER)

    root.mainloop()

