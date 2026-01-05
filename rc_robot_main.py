import RPi.GPIO as GPIO
import time
from picamera import PiCamera
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import random
import math
import numpy as np
import json
#from numba import njit
#import pickle
import cProfile
import solver
import threading

class Stepper:

    def __init__(self, DIR, STEP, EN, HALL):
        self.DIR_PIN = DIR
        self.STEP_PIN = STEP
        self.ENABLE_PIN = EN
        GPIO.setup(self.DIR_PIN, GPIO.OUT)
        GPIO.setup(self.STEP_PIN, GPIO.OUT)
        GPIO.setup(self.ENABLE_PIN, GPIO.OUT)
        GPIO.output(self.ENABLE_PIN, GPIO.HIGH)
        self.pos = 0
        #self.delay = 0.0007
        self.delay = 0.0005
        #self.delay = 0.00035
        self.direction = GPIO.HIGH
        self.HALL_PIN = HALL
        GPIO.setup(self.HALL_PIN, GPIO.IN)
        #print(GPIO.input(self.HALL_PIN))
        pass

    def turn(self, steps):
        GPIO.output(self.ENABLE_PIN, GPIO.LOW)
        GPIO.output(self.DIR_PIN, self.direction)

        for _ in range(steps-10):
            GPIO.output(self.STEP_PIN, GPIO.HIGH)
            time.sleep(self.delay)
            GPIO.output(self.STEP_PIN, GPIO.LOW)
            time.sleep(self.delay)

        while(GPIO.input(self.HALL_PIN)):
            #print(GPIO.input(self.HALL_PIN))
            GPIO.output(self.STEP_PIN, GPIO.HIGH)
            time.sleep(self.delay)
            GPIO.output(self.STEP_PIN, GPIO.LOW)
            time.sleep(self.delay)
            pass

        time.sleep(3*self.delay)
        GPIO.output(self.ENABLE_PIN, GPIO.HIGH)
        pass


    # use strings 'cw' or 'ccw'
    def set_dir(self, dir):
        if(dir == 'cw'):
            self.direction = GPIO.HIGH
        elif(dir == 'ccw'):
            self.direction = GPIO.LOW
        pass


    pass


class Side:

    colors = {'white':'w','yellow':'y','red':'r','blue':'b','orange':'o','green':'g'}

    def __init__(self, col):
        self.color = self.colors[col]
        self.corners = [self.color,self.color,self.color,self.color]
        self.edges = [self.color,self.color,self.color,self.color]

        pass

    def rotate_face_(self):
        cTemp = self.corners[3]
        eTemp = self.edges[3]
        for i in range(3,0,-1):
            self.corners[i] = self.corners[i-1]
            self.edges[i] = self.edges[i-1]
        self.corners[0] = cTemp
        self.edges[0] = eTemp
        pass
    def rotate_face(self):
        solver.rotate_arr(self.corners)
        solver.rotate_arr(self.edges)
        pass

    def check_solved_(self):
        for i in range(4):
            if(self.corners[i] != self.color or self.edges[i] != self.color):
                return False
        return True
    def check_solved(self):
        #return solver.check_solved(self.corners, self.color) > 0 and solver.check_solved(self.edges, self.color)
        return True

    def unsolved(self):
        unsolved = 0
        for i in range(4):
            if(self.corners[i] != self.color):
                unsolved += 1
            if(self.edges[i] != self.color):
                unsolved += 1
        return unsolved

    def unique_colors(self):
        color_count = {'w': 0, 'y': 0, 'r': 0, 'b': 0, 'o': 0, 'g': 0}
        color_count[self.color] += 1
        for i in range(4):
            color_count[self.corners[i]] += 1
            color_count[self.edges[i]] += 1
        unique_count = 0
        for count in color_count.values():
            if(count != 0):
                unique_count += 1
        return unique_count

    def copy_side_(self):
        colors = {'w': 'white', 'y': 'yellow', 'r': 'red', 'b': 'blue', 'o': 'orange', 'g': 'green'}
        new_side = Side(colors[self.color])
        new_side.corners = self.corners[:]
        new_side.edges = self.edges[:]
        return new_side
    def copy_side(self):
        colors = {'w': 'white', 'y': 'yellow', 'r': 'red', 'b': 'blue', 'o': 'orange', 'g': 'green'}
        new_side = Side(colors[self.color])
        new_side.corners = solver.copy_list(self.corners)
        new_side.edges = solver.copy_list(self.edges)
        return new_side

    pass



class Digital_Cube:

    mvs = {'R':0,'L':1,'F':2,'B':3,'D':4}

    def __init__(self):
        self.sides = {
            'D': Side('white'),
            'U': Side('yellow'),
            'F': Side('red'),
            'L': Side('blue'),
            'B': Side('orange'),
            'R': Side('green')
        }
        self.moves_done = []
        self.cache = {}
        self.p4_c_table =[] # np.load("corner_table.npy")
        self.p4_e_table =[] # np.load("edge_table.npy")
        self.p1_edge_table =[] # np.load("p1_edge_table.npy")
        self.p2_table =[] # np.load("p2_table.npy")
        self.p3_edge_table =[] # np.load("p3_edge_table.npy")
        self.p3_corner_table =[] # np.load("p3_corner_table.npy")

        pass

    def load_solve_data(self):
        self.p4_c_table = np.load("corner_table.npy")
        self.p4_e_table = np.load("edge_table.npy")
        self.p1_edge_table = np.load("p1_edge_table.npy")
        self.p2_table = np.load("p2_table.npy")
        self.p3_edge_table = np.load("p3_edge_table.npy")
        self.p3_corner_table = np.load("p3_corner_table.npy")
        self.E_index_table = index_table = {1530: 0, 3546: 1, 3994: 2, 3930: 3, 3946: 4, 3945: 5, 3449: 6, 3197: 7, 3885: 8, 4065: 9, 3825: 10, 3645: 11, 3437: 12, 3533: 13, 3564: 14, 3772: 15, 3828: 16, 4020: 17, 3765: 18, 3509: 19, 3479: 20, 3483: 21, 3513: 22, 3499: 23, 3755: 24, 2990: 25, 3046: 26, 1006: 27, 2542: 28, 2750: 29, 2749: 30, 1725: 31, 1469: 32, 1973: 33, 1913: 34, 893: 35, 2429: 36, 2430: 37, 2878: 38, 1950: 39, 2010: 40, 1914: 41, 1910: 42, 3030: 43, 3034: 44, 3050: 45, 2926: 46, 2909: 47, 2903: 48, 983: 49, 989: 50, 887: 51, 955: 52, 1723: 53, 1771: 54, 2795: 55, 2671: 56, 2415: 57, 2925: 58, 3948: 59, 3900: 60, 3855: 61, 4035: 62, 2019: 63, 999: 64, 1013: 65, 509: 66, 1529: 67, 1525: 68, 2549: 69, 2553: 70, 2556: 71, 2550: 72, 3446: 73, 3443: 74, 3383: 75, 3891: 76, 3987: 77, 2463: 78, 2479: 79, 2535: 80, 3558: 81, 3766: 82, 1726: 83, 3769: 84, 3691: 85, 1998: 86, 2006: 87, 2021: 88, 1511: 89, 1719: 90, 1971: 91, 1779: 92, 1011: 93, 3923: 94, 3954: 95, 3898: 96, 3883: 97, 3939: 98, 3435: 99, 3897: 100, 3867: 101, 4017: 102, 3751: 103, 3757: 104, 2989: 105, 943: 106, 4080: 107, 2805: 108, 2791: 109, 2735: 110, 2287: 111, 1263: 112, 3183: 113, 1487: 114, 1695: 115, 2623: 116, 4042: 117, 4056: 118, 4052: 119, 2036: 120, 2033: 121, 1455: 122, 3471: 123, 3407: 124, 495: 125, 751: 126, 766: 127, 2302: 128, 2554: 129, 3542: 130, 3798: 131, 3742: 132, 3646: 133, 3390: 134, 3135: 135, 2239: 136, 3279: 137, 3231: 138, 3167: 139, 3422: 140, 3918: 141, 2895: 142, 2940: 143, 3064: 144, 3832: 145, 3826: 146, 4066: 147, 4049: 148, 1499: 149, 2025: 150, 1005: 151, 2009: 152, 3539: 153, 3569: 154, 2523: 155, 3033: 156, 3036: 157, 3052: 158, 2998: 159, 3004: 160, 3049: 161, 3043: 162, 1847: 163, 3699: 164, 3795: 165, 3027: 166, 3057: 167, 3060: 168, 2877: 169, 2875: 170, 3643: 171, 3763: 172, 2806: 173, 3790: 174, 3019: 175, 3960: 176, 2685: 177, 2679: 178, 2743: 179, 3507: 180, 1977: 181, 2997: 182, 1974: 183, 1978: 184, 703: 185, 3735: 186, 3990: 187, 3996: 188, 3932: 189, 4038: 190, 3359: 191, 3663: 192, 765: 193, 3677: 194, 3929: 195, 3419: 196, 3415: 197, 1655: 198, 3191: 199, 2423: 200, 1399: 201, 1909: 202, 1405: 203, 3485: 204, 3421: 205, 3869: 206, 3727: 207, 2959: 208, 1935: 209, 1995: 210, 1947: 211, 1851: 212, 1907: 213, 3452: 214, 1916: 215, 1871: 216, 879: 217, 1902: 218, 1406: 219, 1391: 220, 3431: 221, 3510: 222, 3811: 223, 3555: 224, 1965: 225, 1949: 226, 3545: 227, 2003: 228, 3783: 229, 1743: 230, 1751: 231, 3293: 232, 2301: 233, 2271: 234, 1151: 235, 1515: 236, 3813: 237, 3045: 238, 1467: 239, 1403: 240, 3953: 241, 3058: 242, 4018: 243, 4003: 244, 3495: 245, 1959: 246, 1943: 247, 1883: 248, 2995: 249, 2547: 250, 3318: 251, 1788: 252, 3708: 253, 2934: 254, 3002: 255, 3863: 256, 3671: 257, 1823: 258, 1631: 259, 1755: 260, 1647: 261, 1599: 262, 3195: 263, 2299: 264, 2803: 265, 3702: 266, 3942: 267, 2526: 268, 2541: 269, 3309: 270, 1773: 271, 2028: 272, 3787: 273, 3001: 274, 447: 275, 1470: 276, 1523: 277, 3486: 278, 510: 279, 479: 280, 2797: 281, 3693: 282, 990: 283, 1785: 284, 3389: 285, 1659: 286, 3705: 287, 3675: 288, 3631: 289, 3247: 290, 4009: 291, 3817: 292, 3820: 293, 3802: 294, 3534: 295, 3789: 296, 4044: 297, 3450: 298, 2175: 299, 3701: 300, 2863: 301, 3615: 302, 2026: 303, 3021: 304, 3022: 305, 1899: 306, 958: 307, 1014: 308, 927: 309, 2967: 310, 2983: 311, 2719: 312, 2767: 313, 2367: 314, 3570: 315, 2034: 316, 1854: 317, 2022: 318, 1782: 319, 2399: 320, 1885: 321, 3687: 322, 3445: 323, 3317: 324, 3198: 325, 3322: 326, 3291: 327, 3294: 328, 3303: 329, 2847: 330, 3911: 331, 3956: 332, 383: 333, 503: 334, 1271: 335, 3527: 336, 1767: 337, 1980: 338, 2040: 339, 2919: 340, 3438: 341, 1277: 342, 1275: 343, 3514: 344, 3818: 345, 3678: 346, 3694: 347, 2798: 348, 4006: 349, 2295: 350, 2494: 351, 1526: 352, 831: 353, 3287: 354, 3262: 355, 3259: 356, 3307: 357, 2539: 358, 3562: 359, 735: 360, 2655: 361, 3915: 362, 3979: 363, 4010: 364, 3770: 365, 3516: 366, 3261: 367, 3501: 368, 1502: 369, 1518: 370, 1003: 371, 3324: 372, 1781: 373, 3255: 374, 2427: 375, 2971: 376, 3814: 377, 1774: 378, 2511: 379, 1532: 380, 3548: 381, 3541: 382, 3917: 383, 1375: 384, 3925: 385, 3989: 386, 863: 387, 3561: 388, 1966: 389, 1963: 390, 2781: 391, 4005: 392, 3941: 393, 1439: 394, 3894: 395, 1517: 396, 1215: 397, 3739: 398, 507: 399, 1278: 400, 1018: 401, 3926: 402, 1886: 403, 987: 404, 2987: 405, 2519: 406, 3993: 407, 3315: 408, 3893: 409, 3576: 410, 763: 411, 957: 412, 894: 413, 891: 414, 2809: 415, 2938: 416, 3706: 417, 4037: 418, 3797: 419, 1247: 420, 2923: 421, 759: 422, 639: 423, 2491: 424, 1463: 425, 3387: 426, 3531: 427, 1895: 428, 951: 429, 1839: 430, 1711: 431, 1495: 432, 2871: 433, 1879: 434, 3015: 435, 2775: 436, 3801: 437, 3639: 438, 2686: 439, 3321: 440, 2779: 441, 1786: 442, 2487: 443, 1757: 444, 1991: 445, 2973: 446, 3741: 447, 1501: 448, 975: 449, 1997: 450, 2493: 451, 2910: 452, 2974: 453, 3502: 454, 2812: 455, 1853: 456, 4024: 457, 2005: 458, 1901: 459, 2525: 460, 3557: 461, 4041: 462, 2907: 463, 3804: 464, 1017: 465, 3981: 466, 2683: 467, 4050: 468, 3310: 469, 3982: 470, 2937: 471, 2810: 472, 3975: 473, 3879: 474, 4012: 475, 3029: 476, 2933: 477, 3758: 478, 2012: 479, 3375: 480, 4068: 481, 3572: 482, 3886: 483, 1662: 484, 1758: 485, 2782: 486, 2747: 487, 1343: 488, 1661: 489, 1020: 490, 4072: 491, 3870: 492, 2931: 493, 255: 494}
#        with open("p3_edge_table.pkl", "wb") as f:
#            pickle.dump(self.p3_edge_table, f)
#        with open("p3_corner_table.pkl", "wb") as f:
#            pickle.dump(self.p3_corner_table, f)
#        pass

    def R(self):
        self.sides['R'].rotate_face()
        layer = [self.sides['F'],self.sides['U'],self.sides['B'],self.sides['D']]
        cL1Temp = layer[3].corners[1]
        cL2Temp = layer[3].corners[2]
        eLTemp = layer[3].edges[1]
        for i in range(3,0,-1):
            layer[i].corners[1] = layer[i-1].corners[1]
            layer[i].corners[2] = layer[i-1].corners[2]
            layer[i].edges[1] = layer[i-1].edges[1]
        layer[0].corners[1] = cL1Temp
        layer[0].corners[2] = cL2Temp
        layer[0].edges[1] = eLTemp
        pass

    def L(self):
        self.sides['L'].rotate_face()
        layer = [self.sides['F'],self.sides['D'],self.sides['B'],self.sides['U']]
        cL1Temp = layer[3].corners[0]
        cL2Temp = layer[3].corners[3]
        eLTemp = layer[3].edges[3]
        for i in range(3,0,-1):
            layer[i].corners[0] = layer[i-1].corners[0]
            layer[i].corners[3] = layer[i-1].corners[3]
            layer[i].edges[3] = layer[i-1].edges[3]
        layer[0].corners[0] = cL1Temp
        layer[0].corners[3] = cL2Temp
        layer[0].edges[3] = eLTemp
        pass

    def F(self):
        self.sides['F'].rotate_face()
        c1 = self.sides['U'].corners[3]
        c2 = self.sides['U'].corners[2]
        e = self.sides['U'].edges[2]
        self.sides['U'].corners[3] = self.sides['L'].corners[2]
        self.sides['U'].corners[2] = self.sides['L'].corners[1]
        self.sides['U'].edges[2] = self.sides['L'].edges[1]
        self.sides['L'].corners[2] = self.sides['D'].corners[1]
        self.sides['L'].corners[1] = self.sides['D'].corners[0]
        self.sides['L'].edges[1] = self.sides['D'].edges[0]
        self.sides['D'].corners[0] = self.sides['R'].corners[3]
        self.sides['D'].corners[1] = self.sides['R'].corners[0]
        self.sides['D'].edges[0] = self.sides['R'].edges[3]
        self.sides['R'].corners[3] = c2
        self.sides['R'].corners[0] = c1
        self.sides['R'].edges[3] = e
        pass

    def B(self):
        self.sides['B'].rotate_face()
        c1 = self.sides['U'].corners[0]
        c2 = self.sides['U'].corners[1]
        e = self.sides['U'].edges[0]
        self.sides['U'].corners[0] = self.sides['R'].corners[1]
        self.sides['U'].corners[1] = self.sides['R'].corners[2]
        self.sides['U'].edges[0] = self.sides['R'].edges[1]
        self.sides['R'].corners[1] = self.sides['D'].corners[2]
        self.sides['R'].corners[2] = self.sides['D'].corners[3]
        self.sides['R'].edges[1] = self.sides['D'].edges[2]
        self.sides['D'].corners[2] = self.sides['L'].corners[3]
        self.sides['D'].corners[3] = self.sides['L'].corners[0]
        self.sides['D'].edges[2] = self.sides['L'].edges[3]
        self.sides['L'].corners[3] = c1
        self.sides['L'].corners[0] = c2
        self.sides['L'].edges[3] = e
        pass

    def U(self):
        self.sides['U'].rotate_face()
        c1 = self.sides['F'].corners[0]
        c2 = self.sides['F'].corners[1]
        e = self.sides['F'].edges[0]
        self.sides['F'].corners[0] = self.sides['R'].corners[0]
        self.sides['F'].corners[1] = self.sides['R'].corners[1]
        self.sides['F'].edges[0] = self.sides['R'].edges[0]
        self.sides['R'].corners[0] = self.sides['B'].corners[2]
        self.sides['R'].corners[1] = self.sides['B'].corners[3]
        self.sides['R'].edges[0] = self.sides['B'].edges[2]
        self.sides['B'].corners[2] = self.sides['L'].corners[0]
        self.sides['B'].corners[3] = self.sides['L'].corners[1]
        self.sides['B'].edges[2] = self.sides['L'].edges[0]
        self.sides['L'].corners[0] = c1
        self.sides['L'].corners[1] = c2
        self.sides['L'].edges[0] = e
        pass

    def D(self):
        self.sides['D'].rotate_face()
        c1 = self.sides['F'].corners[3]
        c2 = self.sides['F'].corners[2]
        e = self.sides['F'].edges[2]
        self.sides['F'].corners[3] = self.sides['L'].corners[3]
        self.sides['F'].corners[2] = self.sides['L'].corners[2]
        self.sides['F'].edges[2] = self.sides['L'].edges[2]
        self.sides['L'].corners[3] = self.sides['B'].corners[1]
        self.sides['L'].corners[2] = self.sides['B'].corners[0]
        self.sides['L'].edges[2] = self.sides['B'].edges[0]
        self.sides['B'].corners[1] = self.sides['R'].corners[3]
        self.sides['B'].corners[0] = self.sides['R'].corners[2]
        self.sides['B'].edges[0] = self.sides['R'].edges[2]
        self.sides['R'].corners[3] = c1
        self.sides['R'].corners[2] = c2
        self.sides['R'].edges[2] = e
        pass

    def do_moves(self, moves):
        cube_moves = {'U':self.U,'D':self.D,'F':self.F,'B':self.B,'R':self.R,'L':self.L}
        for move in moves:
            self.moves_done.append(move)
            if(len(move)==1):
                cube_moves[move]()
            elif(move[1]=="'"):
                for _ in range(3):
                    cube_moves[move[0]]()
            elif(move[1]=='2'):
                for _ in range(2):
                    cube_moves[move[0]]();
        pass

    def print_cube(self):
        output = ""
        sds=['D','U','F','L','B','R']
        for s in sds:
            sn = 'side'+s
            output += s
            output += ': '
            for p in range(4):
                output += self.sides[s].corners[p]
                output += ' '
                output += self.sides[s].edges[p]
                output += ' '
            output += '\n'
        print(output)
        pass

    def clear_moves(self):
        self.moves_done = []
        pass

    def copy_cube(self):
        cube_copy = Digital_Cube()
        sides = ['F','B','U','D','R','L']
        for side in sides:
            cube_copy.sides[side].corners[0] = self.sides[side].corners[0]
            cube_copy.sides[side].corners[1] = self.sides[side].corners[1]
            cube_copy.sides[side].corners[2] = self.sides[side].corners[2]
            cube_copy.sides[side].corners[3] = self.sides[side].corners[3]
            cube_copy.sides[side].edges[0] = self.sides[side].edges[0]
            cube_copy.sides[side].edges[1] = self.sides[side].edges[1]
            cube_copy.sides[side].edges[2] = self.sides[side].edges[2]
            cube_copy.sides[side].edges[3] = self.sides[side].edges[3]
            pass
        return cube_copy

    def is_valid_cube(self):
        counts = [0,0,0,0,0,0]
        indices = {'r':1,'o':2,'g':3,'b':4,'y':0,'w':5}
        for side in self.sides.values():
            for i in range(4):
                counts[indices[side.corners[i]]] += 1
                counts[indices[side.edges[i]]] += 1
        for val in counts:
            if(val != 8):
                return False
        return True

    def generate_scramble(self, possible_moves=["U","U'","U2","D","D'","D2","F","F'","F2","B","B'","B2","R","R'","R2","L","L'","L2"], num_moves=20):
        available_moves = possible_moves[:]
        moves = []
        for _ in range(num_moves):
            move = available_moves[random.randint(0,len(available_moves)-1)]
            moves.append(move)
            available_moves = self.moves_left(possible_moves, move)
        return moves

    def moves_left(self, moves, last_move):
        mvs_left = []
        for move in moves:
            if(move[0] != last_move[0]):
                mvs_left.append(move)
        return mvs_left

    def equals(self, other):
        for side in self.sides:
            for i in range(4):
                if(self.sides[side].corners[i] != other.sides[side].corners[i] or self.sides[side].edges[i] != other.sides[side].edges[i]):
                    return False
        return True

    def copy_sides_(self):
        new_sides = {
            'D': self.sides['D'].copy_side(),
            'U': self.sides['U'].copy_side(),
            'F': self.sides['F'].copy_side(),
            'L': self.sides['L'].copy_side(),
            'B': self.sides['B'].copy_side(),
            'R': self.sides['R'].copy_side(),
        }
        return new_sides
    def copy_sides(self):
        return solver.copy_sides(self.sides)

    def find_solution(self, starting_moves=[]):

        #G0 (scrambled) --> G1
        print("PHASE 1")
#        self.p1_edge_table = np.load("p1_edge_table.npy")
        p1_moves = ["U","U'","U2","D","D'","D2","F","F'","F2","B","B'","B2","L","L'","L2","R","R'","R2"]
        path_p1 = []
        self.cache = {}
        print(self.estimated_remaining_cost_p1())
        for i in range(0,20):
            max_cost = self.estimated_remaining_cost_p1()
            path_p1 = self.IDA(self.f_p1, max_cost+i, self.check_edge_orientation, p1_moves)
            print(path_p1)
            if(len(path_p1) > 0 or self.check_edge_orientation()):
                break
        if(not self.check_edge_orientation()):
            #print('FAILED')
            return 'FAILED'
        path_p1 = starting_moves + path_p1
        #print(path_p1)
       # self.p1_edge_table = []



        #G1 --> G2
        print("PHASE 2")
#        self.p2_table = np.load("p2_table.npy")
#        self.p2_corner_table = np.load("p2_corner_table.npy")
#        self.p2_edge_table = np.load("p2_edge_table.npy")
        p2_moves = ["U","U'","U2","D","D'","D2","F2","B2","L","L'","L2","R","R'","R2"]
        path_p2 = []
        #extra_moves = []
        self.cache = {}
        max_cost = self.estimated_remaining_cost_p2()
        print(max_cost)
        r = 2
        if(max_cost > 8):
            r = 1
#        r = 100
#        a = 0
#        extra_moves = []
        for i in range(0,r):

            path_p2 = self.IDA(self.f_p2, self.estimated_remaining_cost_p2()+i, self.check_E_slice, p2_moves)
            #path_p2 = self.IDA(self.f_p2, self.estimated_remaining_cost_p2(), self.check_E_slice, p2_moves)
            print(path_p2)
            if(len(path_p2) > 0 or self.check_E_slice()):
                break
#            if(i-a >= 2 or self.estimated_remaining_cost_p2()+i-a >= 10):
#                self.do_moves(self.reverse_moves(extra_moves))
#                extra_moves = self.generate_scramble(possible_moves=p2_moves, num_moves=5)
#                self.do_moves(extra_moves)
#                #i = -1
#                a = i
#                print("REDO")
#                print(self.estimated_remaining_cost_p2())
        if(not self.check_E_slice()):
            #print('FAILED')
            self.do_moves(self.reverse_moves(path_p1))
            scramble = self.generate_scramble(possible_moves=self.moves_left(p1_moves,'U'), num_moves=3)
            self.do_moves(scramble)
            return self.find_solution(starting_moves=scramble)
            return 'FAILED'
#        path_p2 = extra_moves + path_p2
        #print(path_p2)
       # self.p2_table = []


        #G2 --> G3
        print("PHASE 3")
#        self.p3_edge_table = np.load("p3_edge_table.npy")
#        self.p3_corner_table = np.load("p3_corner_table.npy")
        p3_moves = ["U","U'","U2","D","D'","D2","F2","B2","L2","R2"]
        path_p3 = []
        self.cache = {}
        extra_moves = []
        max_cost = self.estimated_remaining_cost_p3()
        print(max_cost)
        a = 0
#        r = 0
        for i in range(0,100):
            print(i-a)
            if(self.estimated_remaining_cost_p3()+i-a <= 10):
                path_p3 = self.IDA(self.f_p3, self.estimated_remaining_cost_p3()+i-a, self.check_half_turn_reduction, p3_moves)
            #path_p3 = self.IDA(self.f_p3, 5+i, self.check_half_turn_reduction, p3_moves)
            print(path_p3)
            #path_p3 = self.IDA(self.f_p3, self.estimated_remaining_cost_p3(), self.check_half_turn_reduction, p3_moves)

            if(len(path_p3) > 0 or self.check_half_turn_reduction()):
                break
            if(i-a >= 4 or self.estimated_remaining_cost_p3()+i-a >= 8):
                self.do_moves(self.reverse_moves(extra_moves))
                extra_moves = self.generate_scramble(possible_moves=self.moves_left(p3_moves,"U"), num_moves=3)
                self.do_moves(extra_moves)
                #i = -1
#                r += 1
                a = i
                print("REDO")
                print(self.estimated_remaining_cost_p3())
        if(not self.check_half_turn_reduction()):
            #print('FAILED')
            #self.do_moves(self.reverse_moves(path_p1 + path_p2))
            #scramble = self.generate_scramble(possible_moves=p1_moves, num_moves=3)
            #self.do_moves(scramble)
            #return self.find_solution(starting_moves=(scramble+starting_moves))
            return 'FAILED'
        path_p3 = extra_moves + path_p3
        #print(path_p3)
        #self.p3_edge_table = []
        #self.p3_corner_table = []

#        self.p4_c_table = np.load("corner_table.npy")
#        self.p4_e_table = np.load("edge_table.npy")
        #G3 --> G4 (solved)
        print("PHASE 4")
        p4_moves = ["U2","R2","L2","B2","F2","D2"]
        path_p4 = []
        self.cache = {}
        a = 0
        extra_p4 = []
        print(self.estimated_remaining_cost_p4())
        r = 0
        for i in range(0,100):
            print(i-a)
            path_p4 = self.IDA(self.f_p4, self.estimated_remaining_cost_p4()+i-a, self.check_solved, p4_moves)
            #path_p4 = self.IDA(self.f_p4, 8+i, self.check_solved, p4_moves)
            print(path_p4)
            if(len(path_p4) > 0 or self.check_solved()):
                break
            if(self.estimated_remaining_cost_p4()+i-a >= 12):
                self.do_moves(self.reverse_moves(extra_p4))
                extra_p4 = self.generate_scramble(possible_moves=['R2','L2','F2','B2','D2'], num_moves=2)
                self.do_moves(extra_p4)
                #i = -1
                r += 0
                a = i - 0.5*r
                print("REDO")
                print(self.estimated_remaining_cost_p4())
        if(not self.check_solved()):
            #print('FAILED')
            return 'FAILED'
        #self.p4_c_table = []
        #self.p4_e_table = []
        path_p4 = extra_p4 + path_p4
        #print(path_p4)
        #print('\n')
        return path_p1 + path_p2 + path_p3 + path_p4

    def IDA(self, heuristic_function, max_cost, check_target, phase_moves):
        starting_moves = phase_moves[1:]
        path = [(phase_moves[0], self.moves_left(phase_moves[1:],phase_moves[0]))]
#        path = [(phase_moves[0], self.moves_left(phase_moves[1:],phase_moves[0]), self.copy_sides())]
        self.do_moves([phase_moves[0]])
        target_reached = False
        while(True):

            #return path if target found 
            if(check_target()):
                #print("SOLVED")
                return self.clean_path(path)

            #empty path
            if(len(path) == 0):

                #break if no more starting moves 
                if(len(starting_moves) == 0):
                    break

                #take next move from starting moves
                next_move = starting_moves.pop()
                path.append((next_move, self.moves_left(starting_moves, next_move)))
#                path.append((next_move, self.moves_left(starting_moves, next_move), self.copy_sides()))
                self.do_moves([next_move])

            #empty follow up move case
            if(len(path[len(path)-1][1]) == 0):

                #else pop and reverse last move
                failed_move = path.pop()
                self.do_moves(self.reverse_moves([failed_move[0]]))
#                self.sides = failed_move[2]

            #follow up moves left
            else:
                #estimated cost WITHIN maximum 
                if(heuristic_function(len(path)) <= max_cost):
                    #pop next move from follow up move array, do move, add to path w/ phase moves - next move
                    next_move = path[len(path)-1][1].pop()
                    path.append((next_move, self.moves_left(phase_moves, next_move)))
#                    path.append((next_move, self.moves_left(phase_moves, next_move), self.copy_sides()))
                    self.do_moves([next_move])

                #estimated cost OVER maximum
                else:
                    #pop and reverse last move
                    failed_move = path.pop()
                    self.do_moves(self.reverse_moves([failed_move[0]]))
#                    self.sides = failed_move[2]

            pass
        return []


    def clean_path(self, path):
        clean_path = []
        for element in path:
            clean_path.append(element[0])
        return clean_path


    def reverse_moves(self, moves):
        reversed_moves = []
        reversed_modifiers = {"'":str(),"2":"2"}
        for i in range(len(moves)-1,-1,-1):
            mv = moves[i][0]
            if(len(moves[i]) != 1): mv += reversed_modifiers[moves[i][1]]
            else: mv += "'"
            reversed_moves.append(mv)
        return reversed_moves

    def moves_left_(self, moves, last_move):
        mvs_left = []
        for move in moves:
            if(move[0] != last_move[0]):
                mvs_left.append(move)
            pass
        return mvs_left
    def moves_left(self, moves, last_move):
        return solver.moves_left(moves, last_move)


    def f_p4(self, current_cost):
        return current_cost + self.estimated_remaining_cost_p4()

    def f_p3(self, current_cost):
        return current_cost + self.estimated_remaining_cost_p3()

    def f_p2(self, current_cost):
        return current_cost + self.estimated_remaining_cost_p2()


    def f_p1(self, current_cost):
        return current_cost + self.estimated_remaining_cost_p1()

    def lookup(self, arr, index):
        return arr[index]


    def estimated_remaining_cost_p4(self):
        cube_hash = self.hash_cube()
        if(cube_hash in self.cache):
            return self.cache[cube_hash]
#        cost = max(self.p4_c_table[self.index_permutation(self.corner_permutation())], self.p4_e_table[self.index_permutation(self.edge_permutation())])
        cost = max(self.lookup(self.p4_c_table, self.index_permutation(self.corner_permutation())), self.lookup(self.p4_e_table, self.index_permutation(self.edge_permutation())))
        self.cache[cube_hash] = cost
        return cost
        return cost_table[h]

    def estimated_remaining_cost_p3(self):
        cube_hash = self.hash_cube()
        if(cube_hash in self.cache):
            return self.cache[cube_hash]
        cost = max(self.p3_edge_table[self.index_permutation(self.UD_edge_permutation())], self.p3_corner_table[self.index_permutation(self.corner_permutation())])
        self.cache[cube_hash] = cost
        return cost
        return cost_table[h]

    def estimated_remaining_cost_p2(self):
        cube_hash = self.hash_cube()
        if(cube_hash in self.cache):
            return self.cache[cube_hash]
        cost = self.p2_table[self.filter_E_index(self.binary_index(self.E_edge_locations()))*2187 + self.corner_orientation_index(self.corner_orientation())]
        self.cache[cube_hash] = cost
        return cost

    def estimated_remaining_cost_p1(self):
        return self.p1_edge_table[self.binary_index(self.edge_orientation())]


    def hash_cube_(self):
        colors = []
        for side in self.sides.values():
            colors += side.corners + side.edges
        return hash(tuple(colors))
    def hash_cube(self):
        return solver.hash_cube(self.sides)

    def corner_orientations(self):
        corner_arr = []
        opposite_colors = {'y':'w','w':'y','b':'g','g':'b','r':'o','o':'r'}
        sides = [self.sides['U'], self.sides['D']]
        for side in sides:
            for i in range(4):
                if(not (side.corners[i] == side.color or side.corners[i] == opposite_colors[side.color])):
                    corner_arr.append(1)
                else:
                    corner_arr.append(0)
        return corner_arr

    def E_edges(self):
        edge_arr = []
        edge_data = {
            'FL': (self.sides['F'].edges[3], self.sides['L'].edges[1]),
            'FR': (self.sides['F'].edges[1], self.sides['R'].edges[3]),
            'BL': (self.sides['B'].edges[3], self.sides['L'].edges[3]),
            'BR': (self.sides['B'].edges[1], self.sides['R'].edges[1])
        }
        for edge in edge_data:
            if(solver.is_E_slice_edge(edge_data[edge])):
                edge_arr.append(0)
            else:
                edge_arr.append(1)
        return edge_arr

    def check_solved_(self):
        sds = ['R','L','U','D','F','B']
        for side in sds:
            if(not self.sides[side].check_solved()):
                return False
        return True
    def check_solved(self):
        return solver.cube_solved(self.sides) == 1


    #G1 state
    def check_edge_orientation(self):
        for i in range(4):
            if(self.sides['L'].edges[i] == 'y' or self.sides['L'].edges[i] == 'w'):
                return False
            if(self.sides['R'].edges[i] == 'y' or self.sides['R'].edges[i] == 'w'):
                return False
        if(self.sides['F'].edges[0] == 'y' or self.sides['F'].edges[0] == 'w'):
            return False
        if(self.sides['F'].edges[2] == 'y' or self.sides['F'].edges[2] == 'w'):
            return False
        if(self.sides['B'].edges[0] == 'y' or self.sides['B'].edges[0] == 'w'):
            return False
        if(self.sides['B'].edges[2] == 'y' or self.sides['B'].edges[2] == 'w'):
            return False
        E_slice_edges = {
            'FL': (self.sides['F'].edges[3], self.sides['L'].edges[1]),
            'FR': (self.sides['F'].edges[1], self.sides['R'].edges[3]),
            'BL': (self.sides['B'].edges[3], self.sides['L'].edges[3]),
            'BR': (self.sides['B'].edges[1], self.sides['R'].edges[1])
        }
        face_colors = {'F':'r','B':'o','L':'b','R':'g'}
        opposite_colors = {'y':'w','w':'y','b':'g','g':'b','r':'o','o':'r'}
        for edge in E_slice_edges:
            if(solver.is_E_slice_edge(list(E_slice_edges[edge]))):
                for i in range(2):
                    if(not (E_slice_edges[edge][i] == face_colors[edge[i]] or E_slice_edges[edge][i] == opposite_colors[face_colors[edge[i]]])):
                        return False
        return True

    def is_E_slice_edge(self, edge):
        if(edge[0] == 'y' or edge[1] == 'y' or edge[0] == 'w' or edge[1] == 'w'):
            return False
        return True


    #G2 state
    def check_E_slice(self):
        opposite_colors = {'y':'w','w':'y','b':'g','g':'b','r':'o','o':'r'}
        side_arr = [self.sides['F'],self.sides['R'],self.sides['B'],self.sides['L']]
        for side in side_arr:
            if(not (side.edges[1] == side.color or side.edges[1] == opposite_colors[side.color])):
                return False
            if(not (side.edges[3] == side.color or side.edges[3] == opposite_colors[side.color])):
                return False
        return self.check_corner_orientation()

    def check_corner_orientation(self):
        opposite_colors = {'y':'w','w':'y','b':'g','g':'b','r':'o','o':'r'}
        sides = [self.sides['U'], self.sides['D']]
        for side in sides:
            for i in range(4):
                if(not (side.corners[i] == side.color or side.corners[i] == opposite_colors[side.color])):
                    return False
        return True

    #G3 state
    def check_half_turn_reduction(self):
        opposite_colors = {'y':'w','w':'y','b':'g','g':'b','r':'o','o':'r'}
        for side in self.sides.values():
            for i in range(4):
                if(not (side.edges[i] == side.color or side.edges[i] == opposite_colors[side.color])):
                    return False
                if(not (side.corners[i] == side.color or side.corners[i] == opposite_colors[side.color])):
                    return False
        return self.check_even_parity()

    def check_even_parity(self):
        edge_data = {
            'FL': (self.sides['F'].edges[3], self.sides['L'].edges[1]),
            'FR': (self.sides['F'].edges[1], self.sides['R'].edges[3]),
            'BL': (self.sides['B'].edges[3], self.sides['L'].edges[3]),
            'BR': (self.sides['B'].edges[1], self.sides['R'].edges[1]),
            'FU': (self.sides['F'].edges[0], self.sides['U'].edges[2]),
            'BU': (self.sides['B'].edges[2], self.sides['U'].edges[0]),
            'FD': (self.sides['F'].edges[2], self.sides['D'].edges[0]),
            'BD': (self.sides['B'].edges[0], self.sides['D'].edges[2]),
            'LU': (self.sides['L'].edges[0], self.sides['U'].edges[3]),
            'RU': (self.sides['R'].edges[0], self.sides['U'].edges[1]),
            'LD': (self.sides['L'].edges[2], self.sides['D'].edges[3]),
            'RD': (self.sides['R'].edges[2], self.sides['D'].edges[1]),
        }

        swaps = 0
        edges = {}
        for edge in edge_data:
            edges[edge] = self.classify_edge(edge_data[edge])
        edges_left = list(edges.keys())
        cycles = []

        while(len(edges_left) > 0):
            last_used = edges_left.pop()
            cycles.append([last_used])
            while(edges[last_used] != last_used):
                last_used = edges[last_used]
                if(last_used in edges_left):
                    edges_left.remove(last_used)
                else:
                    break
                cycles[len(cycles)-1].append(last_used)
            #print(cycles)
        #print(cycles)
        for cycle in cycles:
            swaps += (len(cycle) - 1)
        return swaps % 2 == 0


    def copy_path(self, path):
        path_copy = []
        for element in path:
            new_sides = {
                'D': element[2]['D'].copy_side(),
                'U': element[2]['U'].copy_side(),
                'F': element[2]['F'].copy_side(),
                'L': element[2]['L'].copy_side(),
                'B': element[2]['B'].copy_side(),
                'R': element[2]['R'].copy_side(),
            }
            path_copy.append((element[0], element[1].copy(), new_sides))

        return path_copy

    def classify_edge(self, edge):
        color_sides = {'w': 'D', 'y': 'U', 'r': 'F', 'o': 'B', 'b': 'L', 'g': 'R'}
        priority = {'F': 1, 'B': 1, 'R': 2, 'L': 2, 'U': 3, 'D': 3}
        classification = ""
        sides = (color_sides[edge[0]], color_sides[edge[1]])
        if(priority[sides[0]] < priority[sides[1]]):
            classification = sides[0] + sides[1]
        else:
            classification = sides[1] + sides[0]
        return classification





    def classify_piece_(self, colors):
        priority = {'r': 1, 'o': 1, 'g': 2, 'b': 2, 'y': 3, 'w': 3}
        for i in range(len(colors)-1, 0, -1):
            for j in range(i-1, -1, -1):
                if(priority[colors[i]] < priority[colors[j]]):
                    temp = colors[i]
                    colors[i] = colors[j]
                    colors[j] = temp
        return tuple(colors)
    def classify_piece(self, colors):
        return solver.classify_piece(colors)

    def edge_permutation(self):
        edges = []
        edge_data = {
            'FU': self.classify_piece([self.sides['F'].edges[0], self.sides['U'].edges[2]]),
            'LU': self.classify_piece([self.sides['L'].edges[0], self.sides['U'].edges[3]]),
            'BU': self.classify_piece([self.sides['B'].edges[2], self.sides['U'].edges[0]]),
            'RU': self.classify_piece([self.sides['R'].edges[0], self.sides['U'].edges[1]]),
            'FD': self.classify_piece([self.sides['F'].edges[2], self.sides['D'].edges[0]]),
            'LD': self.classify_piece([self.sides['L'].edges[2], self.sides['D'].edges[3]]),
            'BD': self.classify_piece([self.sides['B'].edges[0], self.sides['D'].edges[2]]),
            'RD': self.classify_piece([self.sides['R'].edges[2], self.sides['D'].edges[1]]),

            'FL': self.classify_piece([self.sides['F'].edges[3], self.sides['L'].edges[1]]),
            'BL': self.classify_piece([self.sides['B'].edges[3], self.sides['L'].edges[3]]),
            'BR': self.classify_piece([self.sides['B'].edges[1], self.sides['R'].edges[1]]),
            'FR': self.classify_piece([self.sides['F'].edges[1], self.sides['R'].edges[3]]),
        }
        edge_indices = {
            ('r','y'):0,
            ('b','y'):1,
            ('o','y'):2,
            ('g','y'):3,
            ('r','w'):4,
            ('b','w'):5,
            ('o','w'):6,
            ('g','w'):7,

            ('r','b'):8,
            ('o','b'):9,
            ('o','g'):10,
            ('r','g'):11,
        }
        for e in edge_data.values():
            edges.append(edge_indices[e])
        return edges

    def UD_edge_permutation(self):
        edges = []
        edge_data = {
            'FU': self.classify_piece([self.sides['F'].edges[0], self.sides['U'].edges[2]]),
            'LU': self.classify_piece([self.sides['L'].edges[0], self.sides['U'].edges[3]]),
            'BU': self.classify_piece([self.sides['B'].edges[2], self.sides['U'].edges[0]]),
            'RU': self.classify_piece([self.sides['R'].edges[0], self.sides['U'].edges[1]]),
            'FD': self.classify_piece([self.sides['F'].edges[2], self.sides['D'].edges[0]]),
            'LD': self.classify_piece([self.sides['L'].edges[2], self.sides['D'].edges[3]]),
            'BD': self.classify_piece([self.sides['B'].edges[0], self.sides['D'].edges[2]]),
            'RD': self.classify_piece([self.sides['R'].edges[2], self.sides['D'].edges[1]]),
        }
        edge_indices = {
            ('r','y'):0,
            ('b','y'):1,
            ('o','y'):2,
            ('g','y'):3,
            ('r','w'):4,
            ('b','w'):5,
            ('o','w'):6,
            ('g','w'):7,
        }
        for e in edge_data.values():
            edges.append(edge_indices[e])
        return edges

    def corner_permutation(self):
        corners = []
        corner_data = {
            'FLU': self.classify_piece([self.sides['F'].corners[0], self.sides['L'].corners[1], self.sides['U'].corners[3]]),
            'BLU': self.classify_piece([self.sides['B'].corners[3], self.sides['L'].corners[0], self.sides['U'].corners[0]]),
            'BRU': self.classify_piece([self.sides['B'].corners[2], self.sides['R'].corners[1], self.sides['U'].corners[1]]),
            'FRU': self.classify_piece([self.sides['F'].corners[1], self.sides['R'].corners[0], self.sides['U'].corners[2]]),
            'FLD': self.classify_piece([self.sides['F'].corners[3], self.sides['L'].corners[2], self.sides['D'].corners[0]]),
            'BLD': self.classify_piece([self.sides['B'].corners[0], self.sides['L'].corners[3], self.sides['D'].corners[3]]),
            'BRD': self.classify_piece([self.sides['B'].corners[1], self.sides['R'].corners[2], self.sides['D'].corners[2]]),
            'FRD': self.classify_piece([self.sides['F'].corners[2], self.sides['R'].corners[3], self.sides['D'].corners[1]]),
        }
        corner_indices = {
            ('r','b','y'):0,
            ('o','b','y'):1,
            ('o','g','y'):2,
            ('r','g','y'):3,
            ('r','b','w'):4,
            ('o','b','w'):5,
            ('o','g','w'):6,
            ('r','g','w'):7
        }
        for c in corner_data.values():
            corners.append(corner_indices[c])
        return corners



    def edge_orientation(self):
        edges = []
        edge_data = {
            'FU': [self.sides['F'].edges[0], self.sides['U'].edges[2]],
            'LU': [self.sides['L'].edges[0], self.sides['U'].edges[3]],
            'BU': [self.sides['B'].edges[2], self.sides['U'].edges[0]],
            'RU': [self.sides['R'].edges[0], self.sides['U'].edges[1]],
            'FD': [self.sides['F'].edges[2], self.sides['D'].edges[0]],
            'LD': [self.sides['L'].edges[2], self.sides['D'].edges[3]],
            'BD': [self.sides['B'].edges[0], self.sides['D'].edges[2]],
            'RD': [self.sides['R'].edges[2], self.sides['D'].edges[1]],
            'LF': [self.sides['L'].edges[1], self.sides['F'].edges[3]],
            'LB': [self.sides['L'].edges[3], self.sides['B'].edges[3]],
            'RB': [self.sides['R'].edges[1], self.sides['B'].edges[1]],
            'RF': [self.sides['R'].edges[3], self.sides['F'].edges[1]],
        }
        opposites = {'r':'o','o':'r','g':'b','b':'g','w':'y','y':'w'}
        side_colors = {'F':'r','L':'b','R':'g','B':'o'}
        for edge in edge_data:
            if(solver.is_E_slice_edge(edge_data[edge])):
                if(edge[1] == 'U' or edge[1] == 'D'):
                    edges.append(0)
                else:
                    if(edge_data[edge][0] == side_colors[edge[0]] or edge_data[edge][0] == opposites[side_colors[edge[0]]]):
                        edges.append(0)
                    else:
                        edges.append(1)
            else:
                if(edge_data[edge][1] == 'y' or edge_data[edge][1] == 'w'):
                    edges.append(0)
                else:
                    edges.append(1)

        return edges

    def corner_orientation(self):
        corners = []
        corner_data = {
            'FLU': [self.sides['F'].corners[0], self.sides['L'].corners[1], self.sides['U'].corners[3]],
            'BLU': [self.sides['B'].corners[3], self.sides['L'].corners[0], self.sides['U'].corners[0]],
            'BRU': [self.sides['B'].corners[2], self.sides['R'].corners[1], self.sides['U'].corners[1]],
            'FRU': [self.sides['F'].corners[1], self.sides['R'].corners[0], self.sides['U'].corners[2]],
            'FLD': [self.sides['F'].corners[3], self.sides['L'].corners[2], self.sides['D'].corners[0]],
            'BLD': [self.sides['B'].corners[0], self.sides['L'].corners[3], self.sides['D'].corners[3]],
            'BRD': [self.sides['B'].corners[1], self.sides['R'].corners[2], self.sides['D'].corners[2]],
      #      'FRD': [self.sides['sideF'].corners[2], self.sides['sideR'].corners[3], self.sides['sideD'].corners[1]],
        }
        for c in corner_data.values():
            if(c[0] == 'y' or c[0] == 'w'):
                corners.append(1)
            elif(c[1] == 'y' or c[1] == 'w'):
                corners.append(2)
            elif(c[2] == 'y' or c[2] == 'w'):
                corners.append(0)
        return corners

    def E_edge_locations(self):
        edge_arr = []
        edge_data = {
            'FL': (self.sides['F'].edges[3], self.sides['L'].edges[1]),
            'FR': (self.sides['F'].edges[1], self.sides['R'].edges[3]),
            'BL': (self.sides['B'].edges[3], self.sides['L'].edges[3]),
            'BR': (self.sides['B'].edges[1], self.sides['R'].edges[1]),
            'FU': (self.sides['F'].edges[0], self.sides['U'].edges[2]),
            'BU': (self.sides['B'].edges[2], self.sides['U'].edges[0]),
            'FD': (self.sides['F'].edges[2], self.sides['D'].edges[0]),
            'BD': (self.sides['B'].edges[0], self.sides['D'].edges[2]),
            'LU': (self.sides['L'].edges[0], self.sides['U'].edges[3]),
            'RU': (self.sides['R'].edges[0], self.sides['U'].edges[1]),
            'LD': (self.sides['L'].edges[2], self.sides['D'].edges[3]),
            'RD': (self.sides['R'].edges[2], self.sides['D'].edges[1]),
        }
        for edge in edge_data:
            if(solver.is_E_slice_edge(list(edge_data[edge]))):
                edge_arr.append(0)
            else:
                edge_arr.append(1)
        return edge_arr


    def index_permutation_(self, p):
        index = 0
        N = len(p)
        for i in range(N):
            count = 0
            for j in range(i+1,N):
                if(p[j] < p[i]):
                    count += 1
            index += count * math.factorial(N - i - 1)
        return index
    def index_permutation(self, p):
        return solver.index_permutation(np.array(p))

    def binary_index_(self, l):
        index = 0
        for bit in l:
            index = (index << 1) | bit
        return index
    def binary_index(self, l):
        return solver.binary_index(np.array(l))

    def corner_orientation_index_(self, c):
        index = 0
        for num in c:
            index = index * 3 + num
        return index
    def corner_orientation_index(self, c):
        return solver.corner_orientation_index(np.array(c))
#    self.E_index_table = index_table = {1530: 0, 3546: 1, 3994: 2, 3930: 3, 3946: 4, 3945: 5, 3449: 6, 3197: 7, 3885: 8, 4065: 9, 3825: 10, 3645: 11, 3437: 12, 3533: 13, 3564: 14, 3772: 15, 3828: 16, 4020: 17, 3765: 18, 3509: 19, 3479: 20, 3483: 21, 3513: 22, 3499: 23, 3755: 24, 2990: 25, 3046: 26, 1006: 27, 2542: 28, 2750: 29, 2749: 30, 1725: 31, 1469: 32, 1973: 33, 1913: 34, 893: 35, 2429: 36, 2430: 37, 2878: 38, 1950: 39, 2010: 40, 1914: 41, 1910: 42, 3030: 43, 3034: 44, 3050: 45, 2926: 46, 2909: 47, 2903: 48, 983: 49, 989: 50, 887: 51, 955: 52, 1723: 53, 1771: 54, 2795: 55, 2671: 56, 2415: 57, 2925: 58, 3948: 59, 3900: 60, 3855: 61, 4035: 62, 2019: 63, 999: 64, 1013: 65, 509: 66, 1529: 67, 1525: 68, 2549: 69, 2553: 70, 2556: 71, 2550: 72, 3446: 73, 3443: 74, 3383: 75, 3891: 76, 3987: 77, 2463: 78, 2479: 79, 2535: 80, 3558: 81, 3766: 82, 1726: 83, 3769: 84, 3691: 85, 1998: 86, 2006: 87, 2021: 88, 1511: 89, 1719: 90, 1971: 91, 1779: 92, 1011: 93, 3923: 94, 3954: 95, 3898: 96, 3883: 97, 3939: 98, 3435: 99, 3897: 100, 3867: 101, 4017: 102, 3751: 103, 3757: 104, 2989: 105, 943: 106, 4080: 107, 2805: 108, 2791: 109, 2735: 110, 2287: 111, 1263: 112, 3183: 113, 1487: 114, 1695: 115, 2623: 116, 4042: 117, 4056: 118, 4052: 119, 2036: 120, 2033: 121, 1455: 122, 3471: 123, 3407: 124, 495: 125, 751: 126, 766: 127, 2302: 128, 2554: 129, 3542: 130, 3798: 131, 3742: 132, 3646: 133, 3390: 134, 3135: 135, 2239: 136, 3279: 137, 3231: 138, 3167: 139, 3422: 140, 3918: 141, 2895: 142, 2940: 143, 3064: 144, 3832: 145, 3826: 146, 4066: 147, 4049: 148, 1499: 149, 2025: 150, 1005: 151, 2009: 152, 3539: 153, 3569: 154, 2523: 155, 3033: 156, 3036: 157, 3052: 158, 2998: 159, 3004: 160, 3049: 161, 3043: 162, 1847: 163, 3699: 164, 3795: 165, 3027: 166, 3057: 167, 3060: 168, 2877: 169, 2875: 170, 3643: 171, 3763: 172, 2806: 173, 3790: 174, 3019: 175, 3960: 176, 2685: 177, 2679: 178, 2743: 179, 3507: 180, 1977: 181, 2997: 182, 1974: 183, 1978: 184, 703: 185, 3735: 186, 3990: 187, 3996: 188, 3932: 189, 4038: 190, 3359: 191, 3663: 192, 765: 193, 3677: 194, 3929: 195, 3419: 196, 3415: 197, 1655: 198, 3191: 199, 2423: 200, 1399: 201, 1909: 202, 1405: 203, 3485: 204, 3421: 205, 3869: 206, 3727: 207, 2959: 208, 1935: 209, 1995: 210, 1947: 211, 1851: 212, 1907: 213, 3452: 214, 1916: 215, 1871: 216, 879: 217, 1902: 218, 1406: 219, 1391: 220, 3431: 221, 3510: 222, 3811: 223, 3555: 224, 1965: 225, 1949: 226, 3545: 227, 2003: 228, 3783: 229, 1743: 230, 1751: 231, 3293: 232, 2301: 233, 2271: 234, 1151: 235, 1515: 236, 3813: 237, 3045: 238, 1467: 239, 1403: 240, 3953: 241, 3058: 242, 4018: 243, 4003: 244, 3495: 245, 1959: 246, 1943: 247, 1883: 248, 2995: 249, 2547: 250, 3318: 251, 1788: 252, 3708: 253, 2934: 254, 3002: 255, 3863: 256, 3671: 257, 1823: 258, 1631: 259, 1755: 260, 1647: 261, 1599: 262, 3195: 263, 2299: 264, 2803: 265, 3702: 266, 3942: 267, 2526: 268, 2541: 269, 3309: 270, 1773: 271, 2028: 272, 3787: 273, 3001: 274, 447: 275, 1470: 276, 1523: 277, 3486: 278, 510: 279, 479: 280, 2797: 281, 3693: 282, 990: 283, 1785: 284, 3389: 285, 1659: 286, 3705: 287, 3675: 288, 3631: 289, 3247: 290, 4009: 291, 3817: 292, 3820: 293, 3802: 294, 3534: 295, 3789: 296, 4044: 297, 3450: 298, 2175: 299, 3701: 300, 2863: 301, 3615: 302, 2026: 303, 3021: 304, 3022: 305, 1899: 306, 958: 307, 1014: 308, 927: 309, 2967: 310, 2983: 311, 2719: 312, 2767: 313, 2367: 314, 3570: 315, 2034: 316, 1854: 317, 2022: 318, 1782: 319, 2399: 320, 1885: 321, 3687: 322, 3445: 323, 3317: 324, 3198: 325, 3322: 326, 3291: 327, 3294: 328, 3303: 329, 2847: 330, 3911: 331, 3956: 332, 383: 333, 503: 334, 1271: 335, 3527: 336, 1767: 337, 1980: 338, 2040: 339, 2919: 340, 3438: 341, 1277: 342, 1275: 343, 3514: 344, 3818: 345, 3678: 346, 3694: 347, 2798: 348, 4006: 349, 2295: 350, 2494: 351, 1526: 352, 831: 353, 3287: 354, 3262: 355, 3259: 356, 3307: 357, 2539: 358, 3562: 359, 735: 360, 2655: 361, 3915: 362, 3979: 363, 4010: 364, 3770: 365, 3516: 366, 3261: 367, 3501: 368, 1502: 369, 1518: 370, 1003: 371, 3324: 372, 1781: 373, 3255: 374, 2427: 375, 2971: 376, 3814: 377, 1774: 378, 2511: 379, 1532: 380, 3548: 381, 3541: 382, 3917: 383, 1375: 384, 3925: 385, 3989: 386, 863: 387, 3561: 388, 1966: 389, 1963: 390, 2781: 391, 4005: 392, 3941: 393, 1439: 394, 3894: 395, 1517: 396, 1215: 397, 3739: 398, 507: 399, 1278: 400, 1018: 401, 3926: 402, 1886: 403, 987: 404, 2987: 405, 2519: 406, 3993: 407, 3315: 408, 3893: 409, 3576: 410, 763: 411, 957: 412, 894: 413, 891: 414, 2809: 415, 2938: 416, 3706: 417, 4037: 418, 3797: 419, 1247: 420, 2923: 421, 759: 422, 639: 423, 2491: 424, 1463: 425, 3387: 426, 3531: 427, 1895: 428, 951: 429, 1839: 430, 1711: 431, 1495: 432, 2871: 433, 1879: 434, 3015: 435, 2775: 436, 3801: 437, 3639: 438, 2686: 439, 3321: 440, 2779: 441, 1786: 442, 2487: 443, 1757: 444, 1991: 445, 2973: 446, 3741: 447, 1501: 448, 975: 449, 1997: 450, 2493: 451, 2910: 452, 2974: 453, 3502: 454, 2812: 455, 1853: 456, 4024: 457, 2005: 458, 1901: 459, 2525: 460, 3557: 461, 4041: 462, 2907: 463, 3804: 464, 1017: 465, 3981: 466, 2683: 467, 4050: 468, 3310: 469, 3982: 470, 2937: 471, 2810: 472, 3975: 473, 3879: 474, 4012: 475, 3029: 476, 2933: 477, 3758: 478, 2012: 479, 3375: 480, 4068: 481, 3572: 482, 3886: 483, 1662: 484, 1758: 485, 2782: 486, 2747: 487, 1343: 488, 1661: 489, 1020: 490, 4072: 491, 3870: 492, 2931: 493, 255: 494}

#    self.E_index_table = index_table = {1530: 0, 3546: 1, 3994: 2, 3930: 3, 3946: 4, 3945: 5, 3449: 6, 3197: 7, 3885: 8, 4065: 9, 3825: 10, 3645: 11, 3437: 12, 3533: 13, 3564: 14, 3772: 15, 3828: 16, 4020: 17, 3765: 18, 3509: 19, 3479: 20, 3483: 21, 3513$
    def filter_E_index(self, index):
#        index_table = {1530: 0, 3546: 1, 3994: 2, 3930: 3, 3946: 4, 3945: 5, 3449: 6, 3197: 7, 3885: 8, 4065: 9, 3825: 10, 3645: 11, 3437: 12, 3533: 13, 3564: 14, 3772: 15, 3828: 16, 4020: 17, 3765: 18, 3509: 19, 3479: 20, 3483: 21, 3513: 22, 3499: 23, 3755: 24, 2990: 25, 3046: 26, 1006: 27, 2542: 28, 2750: 29, 2749: 30, 1725: 31, 1469: 32, 1973: 33, 1913: 34, 893: 35, 2429: 36, 2430: 37, 2878: 38, 1950: 39, 2010: 40, 1914: 41, 1910: 42, 3030: 43, 3034: 44, 3050: 45, 2926: 46, 2909: 47, 2903: 48, 983: 49, 989: 50, 887: 51, 955: 52, 1723: 53, 1771: 54, 2795: 55, 2671: 56, 2415: 57, 2925: 58, 3948: 59, 3900: 60, 3855: 61, 4035: 62, 2019: 63, 999: 64, 1013: 65, 509: 66, 1529: 67, 1525: 68, 2549: 69, 2553: 70, 2556: 71, 2550: 72, 3446: 73, 3443: 74, 3383: 75, 3891: 76, 3987: 77, 2463: 78, 2479: 79, 2535: 80, 3558: 81, 3766: 82, 1726: 83, 3769: 84, 3691: 85, 1998: 86, 2006: 87, 2021: 88, 1511: 89, 1719: 90, 1971: 91, 1779: 92, 1011: 93, 3923: 94, 3954: 95, 3898: 96, 3883: 97, 3939: 98, 3435: 99, 3897: 100, 3867: 101, 4017: 102, 3751: 103, 3757: 104, 2989: 105, 943: 106, 4080: 107, 2805: 108, 2791: 109, 2735: 110, 2287: 111, 1263: 112, 3183: 113, 1487: 114, 1695: 115, 2623: 116, 4042: 117, 4056: 118, 4052: 119, 2036: 120, 2033: 121, 1455: 122, 3471: 123, 3407: 124, 495: 125, 751: 126, 766: 127, 2302: 128, 2554: 129, 3542: 130, 3798: 131, 3742: 132, 3646: 133, 3390: 134, 3135: 135, 2239: 136, 3279: 137, 3231: 138, 3167: 139, 3422: 140, 3918: 141, 2895: 142, 2940: 143, 3064: 144, 3832: 145, 3826: 146, 4066: 147, 4049: 148, 1499: 149, 2025: 150, 1005: 151, 2009: 152, 3539: 153, 3569: 154, 2523: 155, 3033: 156, 3036: 157, 3052: 158, 2998: 159, 3004: 160, 3049: 161, 3043: 162, 1847: 163, 3699: 164, 3795: 165, 3027: 166, 3057: 167, 3060: 168, 2877: 169, 2875: 170, 3643: 171, 3763: 172, 2806: 173, 3790: 174, 3019: 175, 3960: 176, 2685: 177, 2679: 178, 2743: 179, 3507: 180, 1977: 181, 2997: 182, 1974: 183, 1978: 184, 703: 185, 3735: 186, 3990: 187, 3996: 188, 3932: 189, 4038: 190, 3359: 191, 3663: 192, 765: 193, 3677: 194, 3929: 195, 3419: 196, 3415: 197, 1655: 198, 3191: 199, 2423: 200, 1399: 201, 1909: 202, 1405: 203, 3485: 204, 3421: 205, 3869: 206, 3727: 207, 2959: 208, 1935: 209, 1995: 210, 1947: 211, 1851: 212, 1907: 213, 3452: 214, 1916: 215, 1871: 216, 879: 217, 1902: 218, 1406: 219, 1391: 220, 3431: 221, 3510: 222, 3811: 223, 3555: 224, 1965: 225, 1949: 226, 3545: 227, 2003: 228, 3783: 229, 1743: 230, 1751: 231, 3293: 232, 2301: 233, 2271: 234, 1151: 235, 1515: 236, 3813: 237, 3045: 238, 1467: 239, 1403: 240, 3953: 241, 3058: 242, 4018: 243, 4003: 244, 3495: 245, 1959: 246, 1943: 247, 1883: 248, 2995: 249, 2547: 250, 3318: 251, 1788: 252, 3708: 253, 2934: 254, 3002: 255, 3863: 256, 3671: 257, 1823: 258, 1631: 259, 1755: 260, 1647: 261, 1599: 262, 3195: 263, 2299: 264, 2803: 265, 3702: 266, 3942: 267, 2526: 268, 2541: 269, 3309: 270, 1773: 271, 2028: 272, 3787: 273, 3001: 274, 447: 275, 1470: 276, 1523: 277, 3486: 278, 510: 279, 479: 280, 2797: 281, 3693: 282, 990: 283, 1785: 284, 3389: 285, 1659: 286, 3705: 287, 3675: 288, 3631: 289, 3247: 290, 4009: 291, 3817: 292, 3820: 293, 3802: 294, 3534: 295, 3789: 296, 4044: 297, 3450: 298, 2175: 299, 3701: 300, 2863: 301, 3615: 302, 2026: 303, 3021: 304, 3022: 305, 1899: 306, 958: 307, 1014: 308, 927: 309, 2967: 310, 2983: 311, 2719: 312, 2767: 313, 2367: 314, 3570: 315, 2034: 316, 1854: 317, 2022: 318, 1782: 319, 2399: 320, 1885: 321, 3687: 322, 3445: 323, 3317: 324, 3198: 325, 3322: 326, 3291: 327, 3294: 328, 3303: 329, 2847: 330, 3911: 331, 3956: 332, 383: 333, 503: 334, 1271: 335, 3527: 336, 1767: 337, 1980: 338, 2040: 339, 2919: 340, 3438: 341, 1277: 342, 1275: 343, 3514: 344, 3818: 345, 3678: 346, 3694: 347, 2798: 348, 4006: 349, 2295: 350, 2494: 351, 1526: 352, 831: 353, 3287: 354, 3262: 355, 3259: 356, 3307: 357, 2539: 358, 3562: 359, 735: 360, 2655: 361, 3915: 362, 3979: 363, 4010: 364, 3770: 365, 3516: 366, 3261: 367, 3501: 368, 1502: 369, 1518: 370, 1003: 371, 3324: 372, 1781: 373, 3255: 374, 2427: 375, 2971: 376, 3814: 377, 1774: 378, 2511: 379, 1532: 380, 3548: 381, 3541: 382, 3917: 383, 1375: 384, 3925: 385, 3989: 386, 863: 387, 3561: 388, 1966: 389, 1963: 390, 2781: 391, 4005: 392, 3941: 393, 1439: 394, 3894: 395, 1517: 396, 1215: 397, 3739: 398, 507: 399, 1278: 400, 1018: 401, 3926: 402, 1886: 403, 987: 404, 2987: 405, 2519: 406, 3993: 407, 3315: 408, 3893: 409, 3576: 410, 763: 411, 957: 412, 894: 413, 891: 414, 2809: 415, 2938: 416, 3706: 417, 4037: 418, 3797: 419, 1247: 420, 2923: 421, 759: 422, 639: 423, 2491: 424, 1463: 425, 3387: 426, 3531: 427, 1895: 428, 951: 429, 1839: 430, 1711: 431, 1495: 432, 2871: 433, 1879: 434, 3015: 435, 2775: 436, 3801: 437, 3639: 438, 2686: 439, 3321: 440, 2779: 441, 1786: 442, 2487: 443, 1757: 444, 1991: 445, 2973: 446, 3741: 447, 1501: 448, 975: 449, 1997: 450, 2493: 451, 2910: 452, 2974: 453, 3502: 454, 2812: 455, 1853: 456, 4024: 457, 2005: 458, 1901: 459, 2525: 460, 3557: 461, 4041: 462, 2907: 463, 3804: 464, 1017: 465, 3981: 466, 2683: 467, 4050: 468, 3310: 469, 3982: 470, 2937: 471, 2810: 472, 3975: 473, 3879: 474, 4012: 475, 3029: 476, 2933: 477, 3758: 478, 2012: 479, 3375: 480, 4068: 481, 3572: 482, 3886: 483, 1662: 484, 1758: 485, 2782: 486, 2747: 487, 1343: 488, 1661: 489, 1020: 490, 4072: 491, 3870: 492, 2931: 493, 255: 494}
        return self.E_index_table[index]
        return index_table[index]



    pass




class Cube:

    side_idx = {'R': 0, 'L': 1, 'F': 2, 'B': 3, 'D': 4}

    def __init__(self,LED,MTRS):
        self.dig_cube = Digital_Cube()
        self.dig_cube.load_solve_data()
        self.mtrs = MTRS
        self.camera = PiCamera()
        self.camera.resolution = (1920,1080)
        #self.camera.iso = 100
        time.sleep(2)
        #self.camera.shutter_speed = self.camera.exposure_speed
        #g = self.camera.awb_gains
        #self.camera.awb_mode = 'off'
        #self.camera.awb_gains = g
        #self.camera.set_controls({'AeEnable':False})
        self.camera.awb_mode = 'sunlight'
        self.camera.saturation = 20
        self.LED_PIN = LED
        GPIO.setup(self.LED_PIN, GPIO.OUT)
        clr_file = open('colors2.txt','r')
        lines = []
        for line in clr_file: lines.append(line)
        self.color_data = {
            'yellow_m':tuple(float(x) for x in [lines.pop(0).strip(),lines.pop(0).strip(),lines.pop(0).strip()]),
            'yellow_s':tuple(float(x) for x in [lines.pop(0).strip(),lines.pop(0).strip(),lines.pop(0).strip()]),
            'red_m':tuple(float(x) for x in [lines.pop(0).strip(),lines.pop(0).strip(),lines.pop(0).strip()]),
            'red_s':tuple(float(x) for x in [lines.pop(0).strip(),lines.pop(0).strip(),lines.pop(0).strip()]),
            'orange_m':tuple(float(x) for x in [lines.pop(0).strip(),lines.pop(0).strip(),lines.pop(0).strip()]),
            'orange_s':tuple(float(x) for x in [lines.pop(0).strip(),lines.pop(0).strip(),lines.pop(0).strip()]),
            'blue_m':tuple(float(x) for x in [lines.pop(0).strip(),lines.pop(0).strip(),lines.pop(0).strip()]),
            'blue_s':tuple(float(x) for x in [lines.pop(0).strip(),lines.pop(0).strip(),lines.pop(0).strip()]),
            'green_m':tuple(float(x) for x in [lines.pop(0).strip(),lines.pop(0).strip(),lines.pop(0).strip()]),
            'green_s':tuple(float(x) for x in [lines.pop(0).strip(),lines.pop(0).strip(),lines.pop(0).strip()]),
            'white_m':tuple(float(x) for x in [lines.pop(0).strip(),lines.pop(0).strip(),lines.pop(0).strip()]),
            'white_s':tuple(float(x) for x in [lines.pop(0).strip(),lines.pop(0).strip(),lines.pop(0).strip()])
        }

        with open('color_data.json', 'r') as f:
            self.color_data_json = json.load(f)
        #print(self.color_data)
        pass

    def solve(self):
        print("SCANNING CUBE...\n")
        self.scan_cube()
        self.dig_cube.print_cube()
#        print('************************************\n')
        print("FINDING SOLUTION\n")
        solution = self.dig_cube.find_solution()
        self.dig_cube.do_moves(self.dig_cube.reverse_moves(solution))
        solution = self.condense_moves(self.expand_U_moves(solution))
        print("\nSOLUTION: ")
        print(solution)
        print("\nSOLVING CUBE")
        self.do_moves(solution)
        if(not solution[len(solution)-1][0] == 'D'):
            self.do_moves(['D2','D2'])
        print("\nSOLVED")
        pass

    def solve_cube(self):
        solution = self.dig_cube.find_solution()
        self.dig_cube.do_moves(self.dig_cube.reverse_moves(solution))
        print(solution)
        solution = self.condense_moves(solution)
        print(solution)
        self.do_moves(solution)
        self.do_moves(['D2','D2'])
        pass



    def do_moves(self, moves):
        #par_moves = []
#        print(moves)
#        self.dig_cube.do_moves(moves)
        parallel_moves = {'F':'B','B':'F','R':'L','L':'R'}
#        print(moves)
        for i in range(len(moves)):
            move = moves[i]
            if(i > 0 and move[0] != 'U' and move[0] != 'D'):
                prev_move = moves[i-1]
                if(parallel_moves[move[0]] == prev_move[0]):
                    continue
            if(i < len(moves)-1 and move[0] != 'U' and move[0] != 'D'):
                next_move = moves[i+1]
#                print(next_move)
                if(next_move[0] != 'U' and next_move[0] != 'D' and move[0] == parallel_moves[next_move[0]][0]):
                    par_moves = [[next_move]]
#                    print(par_moves)
                    t = threading.Thread(target=self.do_moves, args=(par_moves))
#                    par_moves = [next_move]
                    t.start()
            m = move[0]
            stp = 50*5
            if(len(move) == 2):
                if(move[1] == "'"):
                    stp = 150
                else:
                    stp = 100

            if(m == 'U'):
                a = ""
                if(len(move) == 2):
                    a = move[1]
                self.do_moves(["R","L","F2","B2","R'","L'","D"+a,"R","L","F2","B2","R'","L'"])
#                self.dig_cube.do_moves(self.reverse_moves(["R","L","F2","B2","R'","L'","D"+a,"R","L","F2","B2","R'","L'"]))
            else:
                self.mtrs[self.side_idx[m]].turn(stp)
                self.dig_cube.do_moves([move])
            time.sleep(0.15)
           # t.join()
        pass


    def create_color_data_file(self, file_name):
        colors = ['r','o','b','g','w','y']
        pieces = ['e1','e2','e3','e4','c1','c2','c3','c4']
        data = {
            piece : {
                color : {
                    "sample_size" : 0,
                    "r" : 0,
                    "g" : 0,
                    "b" : 0
                } for color in colors
            } for piece in pieces
        }
        with open(file_name, "w") as f:
            json.dump(data, f, indent=2)
        print("NEW COLOR DATA FILE CREATED")
        pass


    def collect_color_data(self, file_name, scans=10):
        data = None
        try:
            with open(file_name, "r") as f:
                data = json.load(f)
        except:
            self.create_color_data_file(file_name)
            with open(file_name, "r") as f:
                data = json.load(f)
        print("FILE READ")

        rgb = ['r','g','b']
        for scan in range(1,scans+1):
            scramble = self.dig_cube.generate_scramble(num_moves=8)
            self.do_moves(scramble)
            print("SCAN: " + str(scan))
            side = self.get_side_data()
            for piece in side:
                scanned_rgb = side[piece]
                piece_color = None
                if(piece[0] == 'e'):
                    piece_color = self.dig_cube.sides['U'].edges[int(piece[1])-1]
                else:
                    piece_color = self.dig_cube.sides['U'].corners[int(piece[1])-1]
                data[piece][piece_color]["sample_size"] += 1
                for i in range(3):
                    data[piece][piece_color][rgb[i]] = (data[piece][piece_color][rgb[i]] * (data[piece][piece_color]['sample_size']-1) + scanned_rgb[i]) / data[piece][piece_color]['sample_size']

        print("SAVING DATA")
        with open(file_name, 'w') as f:
            json.dump(data, f, indent=2)
        print("DATA SAVED")

        min_sample = 10000
        for pieces in data.values():
            for color in pieces.values():
                if(color['sample_size'] < min_sample):
                    min_sample = color['sample_size']
#                for color in colors.values():
#                    print(color['sample_size'])
#                    if(color['sample_size'] < min_sample):
#                        min_sample = color['sample_size']
        print("MIN SAMPLE: " + str(min_sample))

        self.solve_cube()
        pass




    def get_side_data(self):
        GPIO.output(self.LED_PIN, GPIO.HIGH)
        time.sleep(0.1)
        #print("Capturing")
        self.camera.capture('foo.jpg',resize=(320,320))
        #print("Done")
        time.sleep(0.1)
        GPIO.output(self.LED_PIN, GPIO.LOW)
        img = mpimg.imread('foo.jpg')
        #print(self.avg_RGB(img))
        color_correction = (0,0,0)
        side = {
            'c1':self.avg_RGB(img[270:300,230:280]),
            'c2':self.avg_RGB(img[280:320,10:100]),
            'c3':tuple(x + y for x, y in zip(self.avg_RGB(img[0:45,0:90]), tuple((0,0,0)))),
            'c4':tuple(x + y for x, y in zip(self.avg_RGB(img[0:50,220:300]), tuple((0,0,0)))),
            'e1':self.avg_RGB(img[280:320,120:200]),
            'e2':self.avg_RGB(img[60:240,30:80]),
            'e3':self.avg_RGB(img[0:50,130:200]),
            'e4':tuple(x + y for x, y in zip(self.avg_RGB(img[100:220,220:280]), tuple((0,0,0))))
        }
        return side



    def read_side(self):
        GPIO.output(self.LED_PIN, GPIO.HIGH)
        time.sleep(0.1)
        #print("Capturing")
        self.camera.capture('foo.jpg',resize=(320,320))
        #print("Done")
        time.sleep(0.1)
        GPIO.output(self.LED_PIN, GPIO.LOW)
        img = mpimg.imread('foo.jpg')
        #print(self.avg_RGB(img))
        color_correction = (0,-10,0)
        side = {
            'c1':self.avg_RGB(img[270:300,230:280]),
            'c2':self.avg_RGB(img[280:320,10:100]),
            'c3':tuple(x + y for x, y in zip(self.avg_RGB(img[0:45,0:90]), tuple((0,0,0)))),
            'c4':tuple(x + y for x, y in zip(self.avg_RGB(img[0:50,220:300]), tuple((0,0,0)))),
            'e1':self.avg_RGB(img[280:320,120:200]),
            'e2':self.avg_RGB(img[60:240,30:80]),
            'e3':self.avg_RGB(img[0:50,130:200]),
            'e4':tuple(x + y for x, y in zip(self.avg_RGB(img[100:220,220:280]), tuple((0,0,0))))
        }
        #print(side)
        #self.compare_colors(side['c1'])
#        mpimg.imsave("c1.jpg",img[270:300,230:280])
#        mpimg.imsave("c2.jpg",img[280:320,10:100])
#        mpimg.imsave("c3.jpg",img[0:45,0:90])
#        mpimg.imsave("c4.jpg",img[0:50,220:300])
#        mpimg.imsave("e1.jpg",img[280:320,120:200])
#        mpimg.imsave("e2.jpg",img[60:240,30:80])
#        mpimg.imsave("e3.jpg",img[0:50,130:200])
#        mpimg.imsave("e4.jpg",img[80:220,220:280])
        side = {
            'c1':self.compare_colors(side['c1'],'c1'),
            'c2':self.compare_colors(side['c2'],'c2'),
            'c3':self.compare_colors(side['c3'],'c3'),
            'c4':self.compare_colors(side['c4'],'c4'),
            'e1':self.compare_colors(side['e1'],'e1'),
            'e2':self.compare_colors(side['e2'],'e2'),
            'e3':self.compare_colors(side['e3'],'e3'),
            'e4':self.compare_colors(side['e4'],'e4'),
        }
        #print(side)
        #self.print_side(side)
        return side

    def avg_RGB(self, img):
        RGB = (0,0,0)
        for row in img:
            for pxl in row:
                pxl_tpl = (pxl[0],pxl[1],pxl[2])
                RGB = tuple(x + y for x, y in zip(RGB, pxl_tpl))
        RGB = tuple(x / (len(img)*len(img[0])) for x in RGB)
        return RGB

    def compare_colors_(self, pxl):
        colors = ['yellow','red','orange','blue','green','white']
#        z_scores = []
#        for color in colors:
#            z_scores.append(tuple((x-m)/s for x, m, s in zip(pxl,self.color_data[color+'_m'],self.color_data[color+'_s'])))
        #print(self.color_data['yellow_m'][0])
#        z_avgs = []
#        for z in z_scores:
#            z_avgs.append(((z[0]**2 + z[1]**2 + z[2]**2)/3)**(1/2))
        #print(z_scores)
        #print(z_avgs)
#        color = 0
#        for i in range(1,len(z_avgs)):
#            if(z_avgs[i] < z_avgs[color]):
#                color = i
        #print(colors[color])
#        return colors[color]


        chi_square_stats = []
        for color in colors:
            chi_square_stats.append(tuple(((x-m)**2)/m for x, m in zip(pxl,self.color_data[color+'_m'])))
        for i in range(len(chi_square_stats)):
            chi_square_stats[i] = chi_square_stats[i][0] + chi_square_stats[i][1] + chi_square_stats[i][2]
        color = 0
        for i in range(1,len(chi_square_stats)):
            if(chi_square_stats[i] < chi_square_stats[color]):
               color = i
        return colors[color]

    def compare_colors(self, pxl, piece):
        chi_square_stats = []
        color_names = {'r':'red','o':'orange','w':'white','y':'yellow','b':'blue','g':'green'}
        colors = self.color_data_json[piece].values()
        color_order = list(self.color_data_json[piece].keys())
        for color in colors:
            color_data = (color['r'],color['g'],color['b'])
            chi_square_stats.append(tuple(((x-m)**2)/m for x, m in zip(pxl, color_data)))
        for i in range(len(chi_square_stats)):
            chi_square_stats[i] = chi_square_stats[i][0]+chi_square_stats[i][1]+chi_square_stats[i][2]
        color = 0
        for i in range(1, len(chi_square_stats)):
            if(chi_square_stats[i] < chi_square_stats[color]):
                color = i
        return color_names[color_order[color]]



    def print_side(self, side):
        print(side['c1']+'\t'+side['e1']+'\t'+side['c2']+'\n'+side['e4']+'\tyellow\t'+side['e2']+'\n'+side['c4']+'\t'+side['e3']+'\t'+side['c3'])
        pass

    def calibrate_camera(self):
        colors=['yellow','red','orange','blue','green','white']
        pieces = []
        mean = (0,0,0)
        SD = (0,0,0)
        for color in colors:
            print("COLOR: " + color)
            pass
        pass

    def scan_cube(self):
        for _ in range(4):
            self.set_top_face()
            self.do_moves(['R',"L'","D2","D2"])
        for _ in range(3):
            self.do_moves(['F',"B'","D2","D2"])
            self.set_top_face()
        self.do_moves(['R',"L'","D2","D2"])
        self.set_top_face()
        self.do_moves(['R2','L2',"D2","D2"])
        self.set_top_face()
        self.do_moves(['F',"B'","D2","D2"])
        self.set_top_face()
        self.do_moves(['F2',"B2","D2","D2"])
        self.set_top_face()
        print("VALID CUBE: " + str(self.dig_cube.is_valid_cube()))
        pass

    def set_top_face(self):
        time.sleep(0.25)
        current_side = self.read_side()
        self.dig_cube.sides['U'].corners[0] = current_side['c1'][0]
        self.dig_cube.sides['U'].corners[1] = current_side['c2'][0]
        self.dig_cube.sides['U'].corners[2] = current_side['c3'][0]
        self.dig_cube.sides['U'].corners[3] = current_side['c4'][0]
        self.dig_cube.sides['U'].edges[0] = current_side['e1'][0]
        self.dig_cube.sides['U'].edges[1] = current_side['e2'][0]
        self.dig_cube.sides['U'].edges[2] = current_side['e3'][0]
        self.dig_cube.sides['U'].edges[3] = current_side['e4'][0]
        pass

    def compare_sides(self, side1, side2):
        pieces = ['c1','c2','c3','c4','e1','e2','e3','e4']
        counts = [0,0,0,0,0,0,0,0]
        incorrect_count = 0
        for i in range(len(pieces)):
            if(side1[pieces[i]] != side2[pieces[i]]):
                incorrect_count += 1
                counts[i] = counts[i]+1
        return (incorrect_count, counts)

    def random_moves(self, num_moves):
        moves = ["F","B","D","L","R"]
        modifiers = [str(),"'","2"]
        mv_arr = []
        for _ in range(num_moves):
            layer_index = random.randint(0,len(moves)-1)
            while(len(mv_arr) != 0 and mv_arr[len(mv_arr)-1][0] == moves[layer_index]):
                layer_index = random.randint(0,len(moves)-1)
                pass
            mv_arr.append(moves[layer_index] + modifiers[random.randint(0,len(modifiers)-1)])
        #print(mv_arr)
        return mv_arr

    def reverse_moves(self, moves):
        reversed_modifiers = {"'":str(),"2":"2"}
        reversed_moves = []
        for i in range(len(moves)-1,-1,-1):
            mv = moves[i][0]
            if(len(moves[i]) != 1):
                mv += reversed_modifiers[moves[i][1]]
            else:
                mv += "'"
            reversed_moves.append(mv)
        return reversed_moves

    def condense_moves(self, moves):
        moves = self.group_parallel_moves(moves)
        condensed_moves = []
        i = 0
        while(i < len(moves)):
            if(i == len(moves) - 1):
                condensed_moves.append(moves[i])
                break
            turns = 0
            mv_streak = 0
            for n in range(i,len(moves)):
                if(moves[i][0] != moves[n][0]):
                    break
                mv_streak += 1
                if(len(moves[n]) == 1):
                    turns += 1
                elif(moves[n][1] == "'"):
                    turns -= 1
                else:
                    turns += 2
                pass
            net_turns = turns % 4
            if(net_turns == 1 or net_turns == -3):
                condensed_moves.append(moves[i][0])
            elif(net_turns == -1 or net_turns == 3):
                condensed_moves.append(moves[i][0] + "'")
            elif(net_turns == 2):
                condensed_moves.append(moves[i][0] + "2")
            i += mv_streak
            pass
        #print(moves)
        #print(condensed_moves)
        #print("\n")
        if(len(condensed_moves) < len(moves)):
            return self.condense_moves(condensed_moves)
        return condensed_moves

    def expand_U_moves(self, moves):
        if(not ("U" in moves or "U'" in moves or "U2" in moves)):
            return moves
        expanded_moves = []
        setup_moves = ["R", "L", "F2", "B2", "R'", "L'"]
        for i in range(len(moves)):
            if(moves[i][0] != "U"):
                expanded_moves.append(moves[i])
            else:
                expanded_moves += setup_moves
                if(len(moves[i]) == 1):
                    expanded_moves.append("D")
                else:
                    expanded_moves.append("D" + moves[i][1])
                expanded_moves += setup_moves
        return expanded_moves

    def group_parallel_moves(self, moves):
        parallel_moves = {'U':'D','D':'U','R':'L','L':'R','F':'B','B':'F'}
        new_moves = []
        i = 0
        while(i < len(moves)):
            curr_move = moves[i]
#            print(curr_move)
            mv_stack = [curr_move]
            for j in range(i+1, len(moves)):
                if(curr_move[0] == moves[j][0]):
                    mv_stack.insert(0, moves[j])
                elif(parallel_moves[curr_move[0]] == moves[j][0]):
                    mv_stack.append(moves[j])
                else:
                    break
            new_moves += mv_stack
            i += len(mv_stack)
        return new_moves


    def format_Side(self, Side):
        clrs = {'y':'yellow','w':'white','r':'red','o':'orange','b':'blue','g':'green'}
        side = {
            'c1':clrs[Side.corners[0]],
            'c2':clrs[Side.corners[1]],
            'c3':clrs[Side.corners[2]],
            'c4':clrs[Side.corners[3]],
            'e1':clrs[Side.edges[0]],
            'e2':clrs[Side.edges[1]],
            'e3':clrs[Side.edges[2]],
            'e4':clrs[Side.edges[3]]
        }
        return side

    def TEST_scanner(self, scans = 5, rand_mv_num = 8):
        cube_copy = self.dig_cube.copy_cube()
        incorrect_total = 0
        incorrect_arr = [0,0,0,0,0,0,0,0]
        moves_done = []
        for _ in range(scans):
            moves = self.random_moves(rand_mv_num)
            moves_done.extend(moves)
            self.do_moves(moves)
            self.do_moves(['D2','D2'])
            cube_copy.do_moves(moves)
            scanned_side = self.read_side()
            actual_side = self.format_Side(cube_copy.sides["U"])
            print("\nDETECTED SIDE:")
            self.print_side(scanned_side)
            print("\nACTUAL SIDE:")
            self.print_side(actual_side)
            incorrect_count = self.compare_sides(scanned_side,actual_side)
            incorrect_total += incorrect_count[0]
            for i in range(len(incorrect_count[1])):
                incorrect_arr[i] += incorrect_count[1][i]
            print("\nERRORS: " + str(incorrect_count) + "\n")
            print("\n******************************************\n")
            pass
        pct_correct = round((1-incorrect_total/(scans*8))*100,3)
        print("INCORRECT: " + str(incorrect_total) + "/" + str(8*scans))
        print(incorrect_arr)
        print("SCORE: " + str(pct_correct) + "%")
        #reversed_moves = self.reverse_moves(moves_done)
        #print(moves_done)
        #print(reversed_moves)
        #self.do_moves(self.condense_moves(reversed_moves))
        self.dig_cube.sides = cube_copy.copy_sides()
        solution = self.dig_cube.find_solution()
        self.dig_cube.do_moves(self.dig_cube.reverse_moves(solution))
        self.do_moves(solution)
        pass



    def TEST_scanner_(self, scans=1):
        test_cube = Digital_Cube()
        moves_done = []
        correct_scans = 0
        for scan in range(1, scans+1):
            print("\nSCAN: " + str(scan))
            scramble = test_cube.generate_scramble(num_moves=10)
            moves_done += scramble
            moves_done += ["F'","B","R'","L","F'","B"]
            self.do_moves(scramble)
            test_cube.do_moves(scramble)
            self.scan_cube()
            test_cube.do_moves(["F'","B","R'","L","F'","B"])
            self.dig_cube.print_cube()
            test_cube.print_cube()
            success = self.dig_cube.equals(test_cube)
            valid_cube = self.dig_cube.is_valid_cube()
            if(success): correct_scans += 1
            print("VALID: " + str(valid_cube))
            print("SUCCESS: " + str(success))
        self.do_moves(self.condense_moves(self.reverse_moves(moves_done)))
        print("\nSUCCESS: " + str(correct_scans*100/scans) + "%")
    pass


#*****************************************************

GPIO.setmode(GPIO.BCM)

mtr1 = Stepper(DIR=2,STEP=3,EN=4,HALL=19)
mtr2 = Stepper(DIR=27,STEP=17,EN=22,HALL=21)
mtr3 = Stepper(DIR=11,STEP=9,EN=10,HALL=20)
mtr4 = Stepper(DIR=13,STEP=6,EN=5,HALL=26)
mtr5 = Stepper(DIR=18,STEP=15,EN=14,HALL=16)

mtrs = [mtr4,mtr2,mtr3,mtr1,mtr5]

#mtr1.turn(200)
#mtr2.turn(200)
#mtr3.turn(200)
#mtr4.turn(200)
#mtr5.turn(200)

c = Cube(LED=12,MTRS=mtrs)
#c.read_side()
#dig_cube = Digital_Cube()


while(True):
    x = input("Action: ")
    if(x == "OFF"):
        GPIO.cleanup()
        break
#    for i in range(len(x)):
#        if(x[i] == "B"):
#            mtr1.turn(50)
#        elif(x[i] == "L"):
#            mtr2.turn(50)
#        elif(x[i] == "F"):
#            mtr3.turn(50)
#        elif(x[i] == "R"):
#            mtr4.turn(50)
#        elif(x[i] == "D"):
#            mtr5.turn(50)
#        elif(x[i] == "P"):
#            c.read_side()

    if(x == 'SCAN SIDE'):
        c.read_side()
    elif(x == 'PRINT CUBE'):
        c.dig_cube.print_cube()
    elif(x == 'SCAN CUBE'):
        c.scan_cube()
    elif(x == 'RUN'):
        c.solve()
    elif(x == 'GATHER DATA'):
        s = int(input("SCANS: "))
        c.collect_color_data("color_data.json", scans=s)
    elif(x == "SCRAMBLE"):
        scramble = c.dig_cube.generate_scramble()
        print(scramble)
        c.do_moves(scramble)
    elif(x == "TEST SCANNER"):
        num_scans = int(input("SCANS: "))
        c.TEST_scanner(scans = num_scans)
    elif(x == "SOLVE"):
        c.solve_cube()
    elif(x == "TIME PROFILE"):
        c.dig_cube.do_moves(c.dig_cube.generate_scramble())
        cProfile.run("c.dig_cube.find_solution()")
    elif(x == "FULL TEST"):
        num_solves = int(input("SOLVES: "))
        times = 0
        for i in range(num_solves):
            print("ITERATION: " + str(i+1))
            scramble = c.dig_cube.generate_scramble()
            print(scramble)
            c.do_moves(scramble)
            start = time.time()
            c.solve()
            end = time.time()
            print("\nTIME: " + str(end-start))
            times += (end-start)
        print('\nAVG TIME: ' + str(times/num_solves))
    elif(x == "TEST SOLVE"):
        num_solves = int(input("SOLVES: "))
        times = 0
        for i in range(num_solves):
            print("ITERATION: " + str(i+1))
            scramble = c.dig_cube.generate_scramble()
            c.dig_cube.do_moves(scramble)
            print(scramble)
            t = time.time()
            solution = c.dig_cube.find_solution()
            print(solution)
            times += time.time()-t
            print(time.time()-t)
        print("AVG TIME: " + str(times/num_solves))
    else:
        c.do_moves([x])

    time.sleep(0.25)























