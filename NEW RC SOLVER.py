import math
import time
import numpy as np
import random

class Side:
    colors = {'white': 'w', 'yellow': 'y', 'red': 'r', 'blue': 'b', 'orange': 'o', 'green': 'g'}
    def __init__(self, col):
        self.color = self.colors[col]
        self.corners = [self.color, self.color, self.color, self.color]
        self.edges = [self.color, self.color, self.color, self.color]
        pass
  
    def rotateFace(self):
        cTemp = self.corners[3]
        eTemp = self.edges[3]
        for i in range(3, 0, -1):
            self.corners[i] = self.corners[i - 1]
            self.edges[i] = self.edges[i - 1]
            pass
        self.corners[0] = cTemp
        self.edges[0] = eTemp
        pass
    
    def check_solved(self):
        for i in range(4):
            if(self.corners[i] != self.color or self.edges[i] != self.color):
                return False
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
    
    def copy_side(self):
        colors = {'w': 'white', 'y': 'yellow', 'r': 'red', 'b': 'blue', 'o': 'orange', 'g': 'green'}
        new_side = Side(colors[self.color])
        new_side.corners = self.corners[:]
        new_side.edges = self.edges[:]
        return new_side
    
    pass



class Digital_Cube:
    #mvs = {"R": 0, "L": 1, "F": 2, "B": 3, "D": 4}
    
    def __init__(self):
        self.sides = {
            'sideD': Side('white'),
            'sideU': Side('yellow'),
            'sideF': Side('red'),
            'sideL': Side('blue'),
            'sideB': Side('orange'),
            'sideR': Side('green')
        }
        self.moves_done = []
        self.cache = {}
        pass

    def R(self):
        self.sides['sideR'].rotateFace()
        layer = [self.sides['sideF'], self.sides['sideU'], self.sides['sideB'], self.sides['sideD']]
        cL1Temp = layer[3].corners[1]
        cL2Temp = layer[3].corners[2]
        eLTemp = layer[3].edges[1]
        for i in range(3, 0, -1):
            layer[i].corners[1] = layer[i-1].corners[1]
            layer[i].corners[2] = layer[i-1].corners[2]
            layer[i].edges[1] = layer[i-1].edges[1]
            pass
        layer[0].corners[1] = cL1Temp
        layer[0].corners[2] = cL2Temp
        layer[0].edges[1] = eLTemp
        pass
    
    def L(self):
        self.sides['sideL'].rotateFace()
        layer = [self.sides['sideF'], self.sides['sideD'], self.sides['sideB'], self.sides['sideU']]
        cL1Temp = layer[3].corners[0]
        cL2Temp = layer[3].corners[3]
        eLTemp = layer[3].edges[3]
        for i in range(3, 0, -1):
            layer[i].corners[0] = layer[i-1].corners[0]
            layer[i].corners[3] = layer[i-1].corners[3]
            layer[i].edges[3] = layer[i-1].edges[3]
            pass
        layer[0].corners[0] = cL1Temp
        layer[0].corners[3] = cL2Temp
        layer[0].edges[3] = eLTemp
        pass

    def F(self):
        self.sides['sideF'].rotateFace()
        c1 = self.sides['sideU'].corners[3]
        c2 = self.sides['sideU'].corners[2]
        e = self.sides['sideU'].edges[2]
        self.sides['sideU'].corners[3] = self.sides['sideL'].corners[2]
        self.sides['sideU'].corners[2] = self.sides['sideL'].corners[1]
        self.sides['sideU'].edges[2] = self.sides['sideL'].edges[1]
        self.sides['sideL'].corners[2] = self.sides['sideD'].corners[1]
        self.sides['sideL'].corners[1] = self.sides['sideD'].corners[0]
        self.sides['sideL'].edges[1] = self.sides['sideD'].edges[0]
        self.sides['sideD'].corners[0] = self.sides['sideR'].corners[3]
        self.sides['sideD'].corners[1] = self.sides['sideR'].corners[0]
        self.sides['sideD'].edges[0] = self.sides['sideR'].edges[3]
        self.sides['sideR'].corners[3] = c2
        self.sides['sideR'].corners[0] = c1
        self.sides['sideR'].edges[3] = e
        pass
    
    def B(self):
        self.sides['sideB'].rotateFace()
        c1 = self.sides['sideU'].corners[0]
        c2 = self.sides['sideU'].corners[1]
        e = self.sides['sideU'].edges[0]
        self.sides['sideU'].corners[0] = self.sides['sideR'].corners[1]
        self.sides['sideU'].corners[1] = self.sides['sideR'].corners[2]
        self.sides['sideU'].edges[0] = self.sides['sideR'].edges[1]
        self.sides['sideR'].corners[1] = self.sides['sideD'].corners[2]
        self.sides['sideR'].corners[2] = self.sides['sideD'].corners[3]
        self.sides['sideR'].edges[1] = self.sides['sideD'].edges[2]
        self.sides['sideD'].corners[2] = self.sides['sideL'].corners[3]
        self.sides['sideD'].corners[3] = self.sides['sideL'].corners[0]
        self.sides['sideD'].edges[2] = self.sides['sideL'].edges[3]
        self.sides['sideL'].corners[3] = c1
        self.sides['sideL'].corners[0] = c2
        self.sides['sideL'].edges[3] = e
        pass

    def U(self):
        self.sides['sideU'].rotateFace()
        c1 = self.sides['sideF'].corners[0]
        c2 = self.sides['sideF'].corners[1]
        e = self.sides['sideF'].edges[0]
        self.sides['sideF'].corners[0] = self.sides['sideR'].corners[0]
        self.sides['sideF'].corners[1] = self.sides['sideR'].corners[1]
        self.sides['sideF'].edges[0] = self.sides['sideR'].edges[0]
        self.sides['sideR'].corners[0] = self.sides['sideB'].corners[2]
        self.sides['sideR'].corners[1] = self.sides['sideB'].corners[3]
        self.sides['sideR'].edges[0] = self.sides['sideB'].edges[2]
        self.sides['sideB'].corners[2] = self.sides['sideL'].corners[0]
        self.sides['sideB'].corners[3] = self.sides['sideL'].corners[1]
        self.sides['sideB'].edges[2] = self.sides['sideL'].edges[0]
        self.sides['sideL'].corners[0] = c1
        self.sides['sideL'].corners[1] = c2
        self.sides['sideL'].edges[0] = e
        pass
    
    def D(self):
        self.sides['sideD'].rotateFace()
        c1 = self.sides['sideF'].corners[3]
        c2 = self.sides['sideF'].corners[2]
        e = self.sides['sideF'].edges[2]
        self.sides['sideF'].corners[3] = self.sides['sideL'].corners[3]
        self.sides['sideF'].corners[2] = self.sides['sideL'].corners[2]
        self.sides['sideF'].edges[2] = self.sides['sideL'].edges[2]
        self.sides['sideL'].corners[3] = self.sides['sideB'].corners[1]
        self.sides['sideL'].corners[2] = self.sides['sideB'].corners[0]
        self.sides['sideL'].edges[2] = self.sides['sideB'].edges[0]
        self.sides['sideB'].corners[1] = self.sides['sideR'].corners[3]
        self.sides['sideB'].corners[0] = self.sides['sideR'].corners[2]
        self.sides['sideB'].edges[0] = self.sides['sideR'].edges[2]
        self.sides['sideR'].corners[3] = c1
        self.sides['sideR'].corners[2] = c2
        self.sides['sideR'].edges[2] = e
        pass
    
    def do_moves(self, moves):
        cubeMoves = {'U': self.U, 'D': self.D, 'F': self.F, 'B': self.B, 'R': self.R, 'L': self.L}
        for move in moves:
            #print(len(move))
            if(len(move) == 1):
                cubeMoves[move]()
            elif(move[1] == "'"):
                for _ in range(3):
                    cubeMoves[move[0]]()
            elif(move[1] == "2"):
                for _ in range(2):
                    cubeMoves[move[0]]()
            pass
        pass
    
    def print_cube(self):
        output = ""
        sds = ['D','U','F','L','B','R']
        for s in sds:
            sn = "side" + s
            output += s
            output += ": "
            for p in range(4):
                output += self.sides[sn].corners[p]
                output += " "
                output += self.sides[sn].edges[p]
                output += " "
                pass
            output += "\n"
            pass
        print(output)
        pass
    
    def clear_moves(self):
        self.moves_done = []
        pass
    
    def copy_cube(self):
        cube_copy = Digital_Cube()
        sides = ['sideF','sideB','sideU','sideD','sideR','sideL']
        for side in sides:
            cube_copy.sides[side].corners[0] = self.sides[side].corners[0]
            cube_copy.sides[side].corners[1] = self.sides[side].corners[1]
            cube_copy.sides[side].corners[2] = self.sides[side].corners[2]
            cube_copy.sides[side].corners[3] = self.sides[side].corners[3]
            cube_copy.sides[side].edges[0] = self.sides[side].edges[0]
            cube_copy.sides[side].edges[1] = self.sides[side].edges[1]
            cube_copy.sides[side].edges[2] = self.sides[side].edges[2]
            cube_copy.sides[side].edges[3] = self.sides[side].edges[3]
        return cube_copy
    
    def copy_sides(self):
        new_sides = {
            'sideD': self.sides['sideD'].copy_side(),
            'sideU': self.sides['sideU'].copy_side(),
            'sideF': self.sides['sideF'].copy_side(),
            'sideL': self.sides['sideL'].copy_side(),
            'sideB': self.sides['sideB'].copy_side(),
            'sideR': self.sides['sideR'].copy_side(),
        }
        return new_sides

    def generate_scramble(self, possible_moves=["U","U'","U2","D","D'","D2","F","F'","F2","B","B'","B2","L","L'","L2","R","R'","R2"], num_moves = 25):
        available_moves = possible_moves[:]
        moves = []
        for _ in range(num_moves):
            move = available_moves[random.randint(0,len(available_moves)-1)] 
            moves.append(move)
            available_moves = self.moves_left(possible_moves, move)
            pass
        return moves





    def find_solution(self, starting_moves=[]):        
        
        #G0 (scrambled) --> G1
        #print("PHASE 1")
        self.p1_edge_table = np.load("p1_edge_table.npy")
        p1_moves = ["U","U'","U2","D","D'","D2","F","F'","F2","B","B'","B2","L","L'","L2","R","R'","R2"]
        path_p1 = []
        self.cache = {}
        #print(self.estimated_remaining_cost_p1())
        for i in range(0,20):
            max_cost = self.estimated_remaining_cost_p1()
            path_p1 = self.IDA(self.f_p1, max_cost+i, self.check_edge_orientation, p1_moves)
            #print(path_p1)
            if(len(path_p1) > 0 or self.check_edge_orientation()):
                break
        if(not self.check_edge_orientation()):
            #print('FAILED')
            return 'FAILED'
        path_p1 = starting_moves + path_p1
        #print(path_p1)
        

        
        #G1 --> G2
        #print("PHASE 2")
        self.p2_table = np.load("p2_table.npy")
        self.p2_corner_table = np.load("p2_corner_table.npy")
        self.p2_edge_table = np.load("p2_edge_table.npy")
        p2_moves = ["U","U'","U2","D","D'","D2","F2","B2","L","L'","L2","R","R'","R2"]
        path_p2 = []
        #extra_moves = []
        self.cache = {}
        max_cost = self.estimated_remaining_cost_p2()
        #print(max_cost)
        r = 2
        if(max_cost > 8):
            r = 1
        for i in range(0,r):
            
            path_p2 = self.IDA(self.f_p2, self.estimated_remaining_cost_p2()+i, self.check_E_slice, p2_moves)
            #path_p2 = self.IDA(self.f_p2, self.estimated_remaining_cost_p2(), self.check_E_slice, p2_moves)
            #print(path_p2)
            if(len(path_p2) > 0 or self.check_E_slice()):
                break
        if(not self.check_E_slice()):
            #print('FAILED')
            self.do_moves(self.reverse_moves(path_p1))
            scramble = self.generate_scramble(possible_moves=p1_moves, num_moves=3)
            self.do_moves(scramble)
            return self.find_solution(starting_moves=scramble)
            return 'FAILED'
        #print(path_p2)

        
        #G2 --> G3
        #print("PHASE 3")
        self.p3_edge_table = np.load("p3_edge_table.npy")
        self.p3_corner_table = np.load("p3_corner_table.npy")
        p3_moves = ["U","U'","U2","D","D'","D2","F2","B2","L2","R2"]
        path_p3 = []
        self.cache = {}
        extra_moves = []
        max_cost = self.estimated_remaining_cost_p3()
        #print(max_cost)
        a = 0
        for i in range(0,100):
            
            path_p3 = self.IDA(self.f_p3, self.estimated_remaining_cost_p3()+i-a, self.check_half_turn_reduction, p3_moves)
            #path_p3 = self.IDA(self.f_p3, 5+i, self.check_half_turn_reduction, p3_moves)
            #print(path_p3)
            #path_p3 = self.IDA(self.f_p3, self.estimated_remaining_cost_p3(), self.check_half_turn_reduction, p3_moves)
            
            if(len(path_p3) > 0 or self.check_half_turn_reduction()):
                break
            if(i-a >= 4 or self.estimated_remaining_cost_p3()+i-a >= 8):
                self.do_moves(self.reverse_moves(extra_moves))
                extra_moves = self.generate_scramble(possible_moves=p3_moves, num_moves=5)
                self.do_moves(extra_moves)
                #i = -1
                a = i
                #print("REDO")
                #print(self.estimated_remaining_cost_p3())
        if(not self.check_half_turn_reduction()):
            #print('FAILED')
            #self.do_moves(self.reverse_moves(path_p1 + path_p2))
            #scramble = self.generate_scramble(possible_moves=p1_moves, num_moves=3)
            #self.do_moves(scramble)
            #return self.find_solution(starting_moves=(scramble+starting_moves))
            return 'FAILED'
        path_p3 = extra_moves + path_p3
        #print(path_p3)
        
        
        

        self.p4_c_table = np.load("corner_table.npy")
        self.p4_e_table = np.load("edge_table.npy")
        #G3 --> G4 (solved)
        #print("PHASE 4")
        p4_moves = ["U2","R2","L2","B2","F2","D2"]
        path_p4 = []
        self.cache = {}
        a = 0
        extra_p4 = []
        #print(self.estimated_remaining_cost_p4())
        for i in range(0,100):
            #print(i-a)
            path_p4 = self.IDA(self.f_p4, self.estimated_remaining_cost_p4()+i-a, self.check_solved, p4_moves)
            #path_p4 = self.IDA(self.f_p4, 8+i, self.check_solved, p4_moves)
            #print(path_p4)
            if(len(path_p4) > 0 or self.check_solved()):
                break
            if(self.estimated_remaining_cost_p4()+i-a >= 10):
                self.do_moves(self.reverse_moves(extra_p4))
                extra_p4 = self.generate_scramble(possible_moves=p4_moves, num_moves=5)
                self.do_moves(extra_p4)
                #i = -1
                a = i
                #print("REDO")
                #print(self.estimated_remaining_cost_p4())
        if(not self.check_solved()):
            #print('FAILED')
            return 'FAILED'
        path_p4 = extra_p4 + path_p4
        #print(path_p4)
        #print('\n')
        return path_p1 + path_p2 + path_p3 + path_p4
    

    
    def IDA(self, heuristic_function, max_cost, check_target, phase_moves):
        starting_moves = phase_moves[1:]
#        path = [(phase_moves[0], self.moves_left(phase_moves[1:],phase_moves[0]))]
        path = [(phase_moves[0], self.moves_left(phase_moves[1:],phase_moves[0]), self.copy_sides())]
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
#                path.append((next_move, self.moves_left(starting_moves, next_move)))
                path.append((next_move, self.moves_left(starting_moves, next_move), self.copy_sides()))
                self.do_moves([next_move])
           
            #empty follow up move case
            if(len(path[len(path)-1][1]) == 0):
                
                #else pop and reverse last move
                failed_move = path.pop()
#                self.do_moves(self.reverse_moves([failed_move[0]]))
                self.sides = failed_move[2]
                
            #follow up moves left
            else:
                #estimated cost WITHIN maximum 
                if(heuristic_function(len(path)) <= max_cost):
                    #pop next move from follow up move array, do move, add to path w/ phase moves - next move
                    next_move = path[len(path)-1][1].pop()
#                    path.append((next_move, self.moves_left(phase_moves, next_move)))
                    path.append((next_move, self.moves_left(phase_moves, next_move), self.copy_sides()))
                    self.do_moves([next_move])
                    
                #estimated cost OVER maximum
                else:
                    #pop and reverse last move
                    failed_move = path.pop()
#                    self.do_moves(self.reverse_moves([failed_move[0]]))
                    self.sides = failed_move[2]
            
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
    
    def moves_left(self, moves, last_move):
        mvs_left = []
        for move in moves:
            if(move[0] != last_move[0]):
                mvs_left.append(move)
            pass
        return mvs_left
    
    
    
    def f_p4(self, current_cost):
        return current_cost + self.estimated_remaining_cost_p4()
    
    def f_p3(self, current_cost):
        return current_cost + self.estimated_remaining_cost_p3()
    
    def f_p2(self, current_cost):
        return current_cost + self.estimated_remaining_cost_p2()
    
    
    def f_p1(self, current_cost):
        return current_cost + self.estimated_remaining_cost_p1()
    
    def estimated_remaining_cost_p4(self):
        cube_hash = self.hash_cube()
        if(cube_hash in self.cache):
            return self.cache[cube_hash]
        cost = max(self.p4_c_table[self.index_permutation(self.corner_permutation())], self.p4_e_table[self.index_permutation(self.edge_permutation())])
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


    def hash_cube(self):
        colors = []
        for side in self.sides.values():
            colors += side.corners + side.edges
        return hash(tuple(colors))
    
    
    
    
    def edge_orientation____(self):
        #0 is oriented, 1 is unoriented 
        edge_arr = []
        for i in range(4):
            if(self.sides['sideL'].edges[i] == 'y' or self.sides['sideL'].edges[i] == 'w'):
                edge_arr.append(1)
            else:
                edge_arr.append(0)
            if(self.sides['sideR'].edges[i] == 'y' or self.sides['sideR'].edges[i] == 'w'):
                edge_arr.append(1)
            else:
                edge_arr.append(0)
        if(self.sides['sideF'].edges[0] == 'y' or self.sides['sideF'].edges[0] == 'w'):
            edge_arr.append(1)
        else:
            edge_arr.append(0)
        if(self.sides['sideF'].edges[2] == 'y' or self.sides['sideF'].edges[2] == 'w'):
            edge_arr.append(1)
        else:
            edge_arr.append(0)
        if(self.sides['sideB'].edges[0] == 'y' or self.sides['sideB'].edges[0] == 'w'):
            edge_arr.append(1)
        else:
            edge_arr.append(0)
        if(self.sides['sideB'].edges[2] == 'y' or self.sides['sideB'].edges[2] == 'w'):
            edge_arr.append(1)
        else:
            edge_arr.append(0)
        E_slice_edges = {
            'FL': (self.sides['sideF'].edges[3], self.sides['sideL'].edges[1]),
            'FR': (self.sides['sideF'].edges[1], self.sides['sideR'].edges[3]),
            'BL': (self.sides['sideB'].edges[3], self.sides['sideL'].edges[3]),
            'BR': (self.sides['sideB'].edges[1], self.sides['sideR'].edges[1])
        }
        face_colors = {'F':'r','B':'o','L':'b','R':'g'}
        opposite_colors = {'y':'w','w':'y','b':'g','g':'b','r':'o','o':'r'}
        for edge in E_slice_edges:
            if(self.is_E_slice_edge(E_slice_edges[edge])):
                for i in range(2):
                    if(not (E_slice_edges[edge][i] == face_colors[edge[i]] or E_slice_edges[edge][i] == opposite_colors[face_colors[edge[i]]])):
                        edge_arr.append(1)
                    else:
                        edge_arr.append(0)
        
        return edge_arr
    
    def corner_orientations(self):
        corner_arr = []
        opposite_colors = {'y':'w','w':'y','b':'g','g':'b','r':'o','o':'r'}
        sides = [self.sides['sideU'], self.sides['sideD']]
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
            'FL': (self.sides['sideF'].edges[3], self.sides['sideL'].edges[1]),
            'FR': (self.sides['sideF'].edges[1], self.sides['sideR'].edges[3]),
            'BL': (self.sides['sideB'].edges[3], self.sides['sideL'].edges[3]),
            'BR': (self.sides['sideB'].edges[1], self.sides['sideR'].edges[1])
        }
        for edge in edge_data:
            if(self.is_E_slice_edge(edge_data[edge])):
                edge_arr.append(0)
            else:
                edge_arr.append(1)
        return edge_arr
    
    
    def E_edges__(self):
        edge_arr = []
        edge_data = {
            'FL': (self.sides['sideF'].edges[3], self.sides['sideL'].edges[1]),
            'FR': (self.sides['sideF'].edges[1], self.sides['sideR'].edges[3]),
            'BL': (self.sides['sideB'].edges[3], self.sides['sideL'].edges[3]),
            'BR': (self.sides['sideB'].edges[1], self.sides['sideR'].edges[1]),
            'FU': (self.sides['sideF'].edges[0], self.sides['sideU'].edges[2]),
            'BU': (self.sides['sideB'].edges[2], self.sides['sideU'].edges[0]),
            'FD': (self.sides['sideF'].edges[2], self.sides['sideD'].edges[0]),
            'BD': (self.sides['sideB'].edges[0], self.sides['sideD'].edges[2]),
            'LU': (self.sides['sideL'].edges[0], self.sides['sideU'].edges[3]),
            'RU': (self.sides['sideR'].edges[0], self.sides['sideU'].edges[1]),
            'LD': (self.sides['sideL'].edges[2], self.sides['sideD'].edges[3]),
            'RD': (self.sides['sideR'].edges[2], self.sides['sideD'].edges[1]),
        }
        for edge in edge_data:
            if(self.is_E_slice_edge(edge_data[edge])):
                edge_arr.append(0)
            else:
                edge_arr.append(1)
        return edge_arr
    
    
    
    #G4 state
    def check_solved(self):
        sds = ['sideR','sideL','sideU','sideD','sideF','sideB']
        for side in sds:
            if(not self.sides[side].check_solved()):
                return False
        return True
    
    
    #G1 state
    def check_edge_orientation(self):                    
        for i in range(4):
            if(self.sides['sideL'].edges[i] == 'y' or self.sides['sideL'].edges[i] == 'w'):
                return False
            if(self.sides['sideR'].edges[i] == 'y' or self.sides['sideR'].edges[i] == 'w'):
                return False
        if(self.sides['sideF'].edges[0] == 'y' or self.sides['sideF'].edges[0] == 'w'):
            return False
        if(self.sides['sideF'].edges[2] == 'y' or self.sides['sideF'].edges[2] == 'w'):
            return False
        if(self.sides['sideB'].edges[0] == 'y' or self.sides['sideB'].edges[0] == 'w'):
            return False
        if(self.sides['sideB'].edges[2] == 'y' or self.sides['sideB'].edges[2] == 'w'):
            return False
        E_slice_edges = {
            'FL': (self.sides['sideF'].edges[3], self.sides['sideL'].edges[1]),
            'FR': (self.sides['sideF'].edges[1], self.sides['sideR'].edges[3]),
            'BL': (self.sides['sideB'].edges[3], self.sides['sideL'].edges[3]),
            'BR': (self.sides['sideB'].edges[1], self.sides['sideR'].edges[1])
        }
        face_colors = {'F':'r','B':'o','L':'b','R':'g'}
        opposite_colors = {'y':'w','w':'y','b':'g','g':'b','r':'o','o':'r'}
        for edge in E_slice_edges:
            if(self.is_E_slice_edge(E_slice_edges[edge])):
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
        side_arr = [self.sides['sideF'],self.sides['sideR'],self.sides['sideB'],self.sides['sideL']]
        for side in side_arr:
            if(not (side.edges[1] == side.color or side.edges[1] == opposite_colors[side.color])):
                return False
            if(not (side.edges[3] == side.color or side.edges[3] == opposite_colors[side.color])):
                return False
        return self.check_corner_orientation()
    
    def check_corner_orientation(self):
        opposite_colors = {'y':'w','w':'y','b':'g','g':'b','r':'o','o':'r'}
        sides = [self.sides['sideU'], self.sides['sideD']]
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
    
    def check_even_parity_____(self):
        E1_slice = {
            'FL': (self.sides['sideF'].edges[3], self.sides['sideL'].edges[1]),
            'FR': (self.sides['sideF'].edges[1], self.sides['sideR'].edges[3]),
            'BL': (self.sides['sideB'].edges[3], self.sides['sideL'].edges[3]),
            'BR': (self.sides['sideB'].edges[1], self.sides['sideR'].edges[1])
        }
        E2_slice = {
            'FU': (self.sides['sideF'].edges[0], self.sides['sideU'].edges[2]),
            'BU': (self.sides['sideB'].edges[2], self.sides['sideU'].edges[0]),
            'FD': (self.sides['sideF'].edges[2], self.sides['sideD'].edges[0]),
            'BD': (self.sides['sideB'].edges[0], self.sides['sideD'].edges[2]),
        }
        E3_slice = {
            'LU': (self.sides['sideL'].edges[0], self.sides['sideU'].edges[3]),
            'RU': (self.sides['sideR'].edges[0], self.sides['sideU'].edges[1]),
            'LD': (self.sides['sideL'].edges[2], self.sides['sideD'].edges[3]),
            'RD': (self.sides['sideR'].edges[2], self.sides['sideD'].edges[1]),
        }
        slices = [E1_slice, E2_slice, E3_slice]
        swaps = 0
        for s in slices:
            edges = {}
            for edge in s:
                edges[edge] = self.classify_edge(s[edge])
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
            print(cycles)
            for cycle in cycles:
                swaps += (len(cycle) - 1)
        return swaps % 2 == 0
    
    
    
    
    
    def check_even_parity(self):
        edge_data = {
            'FL': (self.sides['sideF'].edges[3], self.sides['sideL'].edges[1]),
            'FR': (self.sides['sideF'].edges[1], self.sides['sideR'].edges[3]),
            'BL': (self.sides['sideB'].edges[3], self.sides['sideL'].edges[3]),
            'BR': (self.sides['sideB'].edges[1], self.sides['sideR'].edges[1]),
            'FU': (self.sides['sideF'].edges[0], self.sides['sideU'].edges[2]),
            'BU': (self.sides['sideB'].edges[2], self.sides['sideU'].edges[0]),
            'FD': (self.sides['sideF'].edges[2], self.sides['sideD'].edges[0]),
            'BD': (self.sides['sideB'].edges[0], self.sides['sideD'].edges[2]),
            'LU': (self.sides['sideL'].edges[0], self.sides['sideU'].edges[3]),
            'RU': (self.sides['sideR'].edges[0], self.sides['sideU'].edges[1]),
            'LD': (self.sides['sideL'].edges[2], self.sides['sideD'].edges[3]),
            'RD': (self.sides['sideR'].edges[2], self.sides['sideD'].edges[1]),
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
                'sideD': element[2]['sideD'].copy_side(),
                'sideU': element[2]['sideU'].copy_side(),
                'sideF': element[2]['sideF'].copy_side(),
                'sideL': element[2]['sideL'].copy_side(),
                'sideB': element[2]['sideB'].copy_side(),
                'sideR': element[2]['sideR'].copy_side(),
            }
            path_copy.append((element[0], element[1].copy(), new_sides))
            
        return path_copy
    
    
    
    
    # U/D <-- R/L <-- F/B
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





    def classify_piece(self, colors):
        priority = {'r': 1, 'o': 1, 'g': 2, 'b': 2, 'y': 3, 'w': 3}
        for i in range(len(colors)-1, 0, -1):
            for j in range(i-1, -1, -1):
                if(priority[colors[i]] < priority[colors[j]]):
                    temp = colors[i]
                    colors[i] = colors[j]
                    colors[j] = temp
        return tuple(colors)
    


    def edge_permutation(self):
        edges = []
        edge_data = {
            'FU': self.classify_piece([self.sides['sideF'].edges[0], self.sides['sideU'].edges[2]]),
            'LU': self.classify_piece([self.sides['sideL'].edges[0], self.sides['sideU'].edges[3]]),
            'BU': self.classify_piece([self.sides['sideB'].edges[2], self.sides['sideU'].edges[0]]),
            'RU': self.classify_piece([self.sides['sideR'].edges[0], self.sides['sideU'].edges[1]]),
            'FD': self.classify_piece([self.sides['sideF'].edges[2], self.sides['sideD'].edges[0]]),
            'LD': self.classify_piece([self.sides['sideL'].edges[2], self.sides['sideD'].edges[3]]),
            'BD': self.classify_piece([self.sides['sideB'].edges[0], self.sides['sideD'].edges[2]]),
            'RD': self.classify_piece([self.sides['sideR'].edges[2], self.sides['sideD'].edges[1]]),
            
            'FL': self.classify_piece([self.sides['sideF'].edges[3], self.sides['sideL'].edges[1]]),
            'BL': self.classify_piece([self.sides['sideB'].edges[3], self.sides['sideL'].edges[3]]),
            'BR': self.classify_piece([self.sides['sideB'].edges[1], self.sides['sideR'].edges[1]]),
            'FR': self.classify_piece([self.sides['sideF'].edges[1], self.sides['sideR'].edges[3]]),
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
            'FU': self.classify_piece([self.sides['sideF'].edges[0], self.sides['sideU'].edges[2]]),
            'LU': self.classify_piece([self.sides['sideL'].edges[0], self.sides['sideU'].edges[3]]),
            'BU': self.classify_piece([self.sides['sideB'].edges[2], self.sides['sideU'].edges[0]]),
            'RU': self.classify_piece([self.sides['sideR'].edges[0], self.sides['sideU'].edges[1]]),
            'FD': self.classify_piece([self.sides['sideF'].edges[2], self.sides['sideD'].edges[0]]),
            'LD': self.classify_piece([self.sides['sideL'].edges[2], self.sides['sideD'].edges[3]]),
            'BD': self.classify_piece([self.sides['sideB'].edges[0], self.sides['sideD'].edges[2]]),
            'RD': self.classify_piece([self.sides['sideR'].edges[2], self.sides['sideD'].edges[1]]),
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
            'FLU': self.classify_piece([self.sides['sideF'].corners[0], self.sides['sideL'].corners[1], self.sides['sideU'].corners[3]]),
            'BLU': self.classify_piece([self.sides['sideB'].corners[3], self.sides['sideL'].corners[0], self.sides['sideU'].corners[0]]),
            'BRU': self.classify_piece([self.sides['sideB'].corners[2], self.sides['sideR'].corners[1], self.sides['sideU'].corners[1]]),
            'FRU': self.classify_piece([self.sides['sideF'].corners[1], self.sides['sideR'].corners[0], self.sides['sideU'].corners[2]]),
            'FLD': self.classify_piece([self.sides['sideF'].corners[3], self.sides['sideL'].corners[2], self.sides['sideD'].corners[0]]),
            'BLD': self.classify_piece([self.sides['sideB'].corners[0], self.sides['sideL'].corners[3], self.sides['sideD'].corners[3]]),
            'BRD': self.classify_piece([self.sides['sideB'].corners[1], self.sides['sideR'].corners[2], self.sides['sideD'].corners[2]]),
            'FRD': self.classify_piece([self.sides['sideF'].corners[2], self.sides['sideR'].corners[3], self.sides['sideD'].corners[1]]),
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
            'FU': [self.sides['sideF'].edges[0], self.sides['sideU'].edges[2]],
            'LU': [self.sides['sideL'].edges[0], self.sides['sideU'].edges[3]],
            'BU': [self.sides['sideB'].edges[2], self.sides['sideU'].edges[0]],
            'RU': [self.sides['sideR'].edges[0], self.sides['sideU'].edges[1]],
            'FD': [self.sides['sideF'].edges[2], self.sides['sideD'].edges[0]],
            'LD': [self.sides['sideL'].edges[2], self.sides['sideD'].edges[3]],
            'BD': [self.sides['sideB'].edges[0], self.sides['sideD'].edges[2]],
            'RD': [self.sides['sideR'].edges[2], self.sides['sideD'].edges[1]],
            
            'LF': [self.sides['sideL'].edges[1], self.sides['sideF'].edges[3]],
            'LB': [self.sides['sideL'].edges[3], self.sides['sideB'].edges[3]],
            'RB': [self.sides['sideR'].edges[1], self.sides['sideB'].edges[1]],
            'RF': [self.sides['sideR'].edges[3], self.sides['sideF'].edges[1]],
        }
        opposites = {'r':'o','o':'r','g':'b','b':'g','w':'y','y':'w'}
        side_colors = {'F':'r','L':'b','R':'g','B':'o'}
        for edge in edge_data:
            if(self.is_E_slice_edge(edge_data[edge])):
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
            'FLU': [self.sides['sideF'].corners[0], self.sides['sideL'].corners[1], self.sides['sideU'].corners[3]],
            'BLU': [self.sides['sideB'].corners[3], self.sides['sideL'].corners[0], self.sides['sideU'].corners[0]],
            'BRU': [self.sides['sideB'].corners[2], self.sides['sideR'].corners[1], self.sides['sideU'].corners[1]],
            'FRU': [self.sides['sideF'].corners[1], self.sides['sideR'].corners[0], self.sides['sideU'].corners[2]],
            'FLD': [self.sides['sideF'].corners[3], self.sides['sideL'].corners[2], self.sides['sideD'].corners[0]],
            'BLD': [self.sides['sideB'].corners[0], self.sides['sideL'].corners[3], self.sides['sideD'].corners[3]],
            'BRD': [self.sides['sideB'].corners[1], self.sides['sideR'].corners[2], self.sides['sideD'].corners[2]],
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
            'FL': (self.sides['sideF'].edges[3], self.sides['sideL'].edges[1]),
            'FR': (self.sides['sideF'].edges[1], self.sides['sideR'].edges[3]),
            'BL': (self.sides['sideB'].edges[3], self.sides['sideL'].edges[3]),
            'BR': (self.sides['sideB'].edges[1], self.sides['sideR'].edges[1]),
            'FU': (self.sides['sideF'].edges[0], self.sides['sideU'].edges[2]),
            'BU': (self.sides['sideB'].edges[2], self.sides['sideU'].edges[0]),
            'FD': (self.sides['sideF'].edges[2], self.sides['sideD'].edges[0]),
            'BD': (self.sides['sideB'].edges[0], self.sides['sideD'].edges[2]),
            'LU': (self.sides['sideL'].edges[0], self.sides['sideU'].edges[3]),
            'RU': (self.sides['sideR'].edges[0], self.sides['sideU'].edges[1]),
            'LD': (self.sides['sideL'].edges[2], self.sides['sideD'].edges[3]),
            'RD': (self.sides['sideR'].edges[2], self.sides['sideD'].edges[1]),
        }
        for edge in edge_data:
            if(self.is_E_slice_edge(edge_data[edge])):
                edge_arr.append(0)
            else:
                edge_arr.append(1)
        return edge_arr
    

    def index_permutation(self, p):
        index = 0
        N = len(p)
        for i in range(N):
            count = 0
            for j in range(i+1,N):
                if(p[j] < p[i]):
                    count += 1
            index += count * math.factorial(N - i - 1)
        return index

    def binary_index(self, l):
        index = 0
        for bit in l:
            index = (index << 1) | bit
        return index

    def corner_orientation_index(self, c):
        index = 0
        for num in c:
            index = index * 3 + num
        return index

    def filter_E_index(self, index):
        index_table = {1530: 0, 3546: 1, 3994: 2, 3930: 3, 3946: 4, 3945: 5, 3449: 6, 3197: 7, 3885: 8, 4065: 9, 3825: 10, 3645: 11, 3437: 12, 3533: 13, 3564: 14, 3772: 15, 3828: 16, 4020: 17, 3765: 18, 3509: 19, 3479: 20, 3483: 21, 3513: 22, 3499: 23, 3755: 24, 2990: 25, 3046: 26, 1006: 27, 2542: 28, 2750: 29, 2749: 30, 1725: 31, 1469: 32, 1973: 33, 1913: 34, 893: 35, 2429: 36, 2430: 37, 2878: 38, 1950: 39, 2010: 40, 1914: 41, 1910: 42, 3030: 43, 3034: 44, 3050: 45, 2926: 46, 2909: 47, 2903: 48, 983: 49, 989: 50, 887: 51, 955: 52, 1723: 53, 1771: 54, 2795: 55, 2671: 56, 2415: 57, 2925: 58, 3948: 59, 3900: 60, 3855: 61, 4035: 62, 2019: 63, 999: 64, 1013: 65, 509: 66, 1529: 67, 1525: 68, 2549: 69, 2553: 70, 2556: 71, 2550: 72, 3446: 73, 3443: 74, 3383: 75, 3891: 76, 3987: 77, 2463: 78, 2479: 79, 2535: 80, 3558: 81, 3766: 82, 1726: 83, 3769: 84, 3691: 85, 1998: 86, 2006: 87, 2021: 88, 1511: 89, 1719: 90, 1971: 91, 1779: 92, 1011: 93, 3923: 94, 3954: 95, 3898: 96, 3883: 97, 3939: 98, 3435: 99, 3897: 100, 3867: 101, 4017: 102, 3751: 103, 3757: 104, 2989: 105, 943: 106, 4080: 107, 2805: 108, 2791: 109, 2735: 110, 2287: 111, 1263: 112, 3183: 113, 1487: 114, 1695: 115, 2623: 116, 4042: 117, 4056: 118, 4052: 119, 2036: 120, 2033: 121, 1455: 122, 3471: 123, 3407: 124, 495: 125, 751: 126, 766: 127, 2302: 128, 2554: 129, 3542: 130, 3798: 131, 3742: 132, 3646: 133, 3390: 134, 3135: 135, 2239: 136, 3279: 137, 3231: 138, 3167: 139, 3422: 140, 3918: 141, 2895: 142, 2940: 143, 3064: 144, 3832: 145, 3826: 146, 4066: 147, 4049: 148, 1499: 149, 2025: 150, 1005: 151, 2009: 152, 3539: 153, 3569: 154, 2523: 155, 3033: 156, 3036: 157, 3052: 158, 2998: 159, 3004: 160, 3049: 161, 3043: 162, 1847: 163, 3699: 164, 3795: 165, 3027: 166, 3057: 167, 3060: 168, 2877: 169, 2875: 170, 3643: 171, 3763: 172, 2806: 173, 3790: 174, 3019: 175, 3960: 176, 2685: 177, 2679: 178, 2743: 179, 3507: 180, 1977: 181, 2997: 182, 1974: 183, 1978: 184, 703: 185, 3735: 186, 3990: 187, 3996: 188, 3932: 189, 4038: 190, 3359: 191, 3663: 192, 765: 193, 3677: 194, 3929: 195, 3419: 196, 3415: 197, 1655: 198, 3191: 199, 2423: 200, 1399: 201, 1909: 202, 1405: 203, 3485: 204, 3421: 205, 3869: 206, 3727: 207, 2959: 208, 1935: 209, 1995: 210, 1947: 211, 1851: 212, 1907: 213, 3452: 214, 1916: 215, 1871: 216, 879: 217, 1902: 218, 1406: 219, 1391: 220, 3431: 221, 3510: 222, 3811: 223, 3555: 224, 1965: 225, 1949: 226, 3545: 227, 2003: 228, 3783: 229, 1743: 230, 1751: 231, 3293: 232, 2301: 233, 2271: 234, 1151: 235, 1515: 236, 3813: 237, 3045: 238, 1467: 239, 1403: 240, 3953: 241, 3058: 242, 4018: 243, 4003: 244, 3495: 245, 1959: 246, 1943: 247, 1883: 248, 2995: 249, 2547: 250, 3318: 251, 1788: 252, 3708: 253, 2934: 254, 3002: 255, 3863: 256, 3671: 257, 1823: 258, 1631: 259, 1755: 260, 1647: 261, 1599: 262, 3195: 263, 2299: 264, 2803: 265, 3702: 266, 3942: 267, 2526: 268, 2541: 269, 3309: 270, 1773: 271, 2028: 272, 3787: 273, 3001: 274, 447: 275, 1470: 276, 1523: 277, 3486: 278, 510: 279, 479: 280, 2797: 281, 3693: 282, 990: 283, 1785: 284, 3389: 285, 1659: 286, 3705: 287, 3675: 288, 3631: 289, 3247: 290, 4009: 291, 3817: 292, 3820: 293, 3802: 294, 3534: 295, 3789: 296, 4044: 297, 3450: 298, 2175: 299, 3701: 300, 2863: 301, 3615: 302, 2026: 303, 3021: 304, 3022: 305, 1899: 306, 958: 307, 1014: 308, 927: 309, 2967: 310, 2983: 311, 2719: 312, 2767: 313, 2367: 314, 3570: 315, 2034: 316, 1854: 317, 2022: 318, 1782: 319, 2399: 320, 1885: 321, 3687: 322, 3445: 323, 3317: 324, 3198: 325, 3322: 326, 3291: 327, 3294: 328, 3303: 329, 2847: 330, 3911: 331, 3956: 332, 383: 333, 503: 334, 1271: 335, 3527: 336, 1767: 337, 1980: 338, 2040: 339, 2919: 340, 3438: 341, 1277: 342, 1275: 343, 3514: 344, 3818: 345, 3678: 346, 3694: 347, 2798: 348, 4006: 349, 2295: 350, 2494: 351, 1526: 352, 831: 353, 3287: 354, 3262: 355, 3259: 356, 3307: 357, 2539: 358, 3562: 359, 735: 360, 2655: 361, 3915: 362, 3979: 363, 4010: 364, 3770: 365, 3516: 366, 3261: 367, 3501: 368, 1502: 369, 1518: 370, 1003: 371, 3324: 372, 1781: 373, 3255: 374, 2427: 375, 2971: 376, 3814: 377, 1774: 378, 2511: 379, 1532: 380, 3548: 381, 3541: 382, 3917: 383, 1375: 384, 3925: 385, 3989: 386, 863: 387, 3561: 388, 1966: 389, 1963: 390, 2781: 391, 4005: 392, 3941: 393, 1439: 394, 3894: 395, 1517: 396, 1215: 397, 3739: 398, 507: 399, 1278: 400, 1018: 401, 3926: 402, 1886: 403, 987: 404, 2987: 405, 2519: 406, 3993: 407, 3315: 408, 3893: 409, 3576: 410, 763: 411, 957: 412, 894: 413, 891: 414, 2809: 415, 2938: 416, 3706: 417, 4037: 418, 3797: 419, 1247: 420, 2923: 421, 759: 422, 639: 423, 2491: 424, 1463: 425, 3387: 426, 3531: 427, 1895: 428, 951: 429, 1839: 430, 1711: 431, 1495: 432, 2871: 433, 1879: 434, 3015: 435, 2775: 436, 3801: 437, 3639: 438, 2686: 439, 3321: 440, 2779: 441, 1786: 442, 2487: 443, 1757: 444, 1991: 445, 2973: 446, 3741: 447, 1501: 448, 975: 449, 1997: 450, 2493: 451, 2910: 452, 2974: 453, 3502: 454, 2812: 455, 1853: 456, 4024: 457, 2005: 458, 1901: 459, 2525: 460, 3557: 461, 4041: 462, 2907: 463, 3804: 464, 1017: 465, 3981: 466, 2683: 467, 4050: 468, 3310: 469, 3982: 470, 2937: 471, 2810: 472, 3975: 473, 3879: 474, 4012: 475, 3029: 476, 2933: 477, 3758: 478, 2012: 479, 3375: 480, 4068: 481, 3572: 482, 3886: 483, 1662: 484, 1758: 485, 2782: 486, 2747: 487, 1343: 488, 1661: 489, 1020: 490, 4072: 491, 3870: 492, 2931: 493, 255: 494}
        return index_table[index]
        
    pass



def filter_times(arr, min_time):
    new_arr = []
    for val in arr:
        if(val >= min_time):
            new_arr.append(val)
    return new_arr


p1_moves = ["U","U'","U2","D","D'","D2","F","F'","F2","B","B'","B2","L","L'","L2","R","R'","R2"]
p2_moves = ["U","U'","U2","D","D'","D2","F2","B2","L","L'","L2","R","R'","R2"]
p3_moves = ["U","U'","U2","D","D'","D2","F2","B2","L2","R2"]
p4_moves = ["U2","D2","F2","B2","L2","R2"]


#import cProfile
#c = Digital_Cube()
#scramble = c.generate_scramble()
#c.do_moves(scramble)
#cProfile.run('c.find_solution()')

solve_times = []
failed = 0
move_count = 0
iterations = 1000
iterations = 3
for i in range(0, iterations):
    cube = Digital_Cube()
    print("Iteration: " + str(i+1))
    scramble = cube.generate_scramble(possible_moves=p1_moves)
    cube.do_moves(scramble)
    print(scramble)
    start = time.time()
    solution = cube.find_solution()
    print(solution)
    if(solution == "FAILED"):
        failed += 1
    total_time = time.time() - start
    solve_times.append(round(total_time, 3))
    mc = len(solution)
    move_count += mc
    print("MOVE COUNT: " + str(mc))
    print("Time: " + str(total_time))
    print('\n')

#print("AVG TIME: " + str(sum(solve_times)/len(solve_times)))
#print("AVG MOVES: " + str(move_count/len(solve_times)))
#print("FAILED: " + str(failed))
#print(filter_times(solve_times, 10))


#PHASE 4 *****************************************************************

#c_table = np.full(math.factorial(8), 255, dtype=np.uint8)
#e_table = np.full(math.factorial(12), 255, dtype=np.uint8)

#c_table = np.load("corner_table.npy")
#e_table = np.load("edge_table.npy")


scrambles = 1000000
scrambles = 0
for _ in range(scrambles):
    c = Digital_Cube()
    scramble = c.generate_scramble(possible_moves=p4_moves, num_moves=15)
    for i in range(len(scramble)):
        c.do_moves([scramble[i]])
        #c_index = c.index_permutation(c.corner_permutation())
        e_index = c.index_permutation(c.edge_permutation())
        #if(i+1 < c_table[c_index]):
        #    c_table[c_index] = i+1
        #    #last_edit = time.time()
        #    print("CORNER")
        if(i+1 < e_table[e_index]):
            e_table[e_index] = i+1
            #last_edit = time.time()
            print("EDGE")


#print(c_table[0:100])

#print("DONE")
#np.save("corner_table.npy", c_table)
#np.save("edge_table.npy", e_table)

#ct = np.full(math.factorial(8), 255, dtype=np.uint8)
#et = np.full(math.factorial(12), 255, dtype=np.uint8)

#for i in range(len(c_table)):
#    ct[i] = c_table[i]
#np.save("corner_table1.npy", ct)


#c = Digital_Cube()
#num_moves = 1000
#start = time.time()
#for _ in range(num_moves):
#    c.do_moves(["U2"])
#print((time.time()-start)/num_moves)

#c = Digital_Cube()
#scramble = c.generate_scramble(possible_moves=p4_moves,num_moves=8)
#print(c.estimated_remaining_cost_p4())
#for move in scramble:
#    c.do_moves([move])
#    print(c.estimated_remaining_cost_p4())


#c = Digital_Cube()
#num = 0

#start = time.time()
#for _ in range(num):
#    c.hash_cube()
#print(time.time() - start)

#start = time.time()
#for _ in range(num):
#    c.estimated_remaining_cost_p4()
#print(time.time() - start)


#PHASE 1 *****************************************************************

#e_table = np.full(math.factorial(8), 255, dtype=np.uint8)

#e_table = np.load("p1_edge_table.npy")

scrambles = 100000
scrambles = 0
for _ in range(scrambles):
    c = Digital_Cube()
    c.do_moves(c.generate_scramble(possible_moves=p2_moves))
    scramble = c.generate_scramble(possible_moves=p1_moves, num_moves=15)
    for i in range(len(scramble)):
        c.do_moves([scramble[i]])
        e_index = c.binary_index(c.edge_orientation())
        if(i+1 < e_table[e_index]):
            e_table[e_index] = i+1
            #last_edit = time.time()
            print("EDGE")


#print(c_table[0:100])

#np.save("p1_edge_table.npy", e_table)


#PHASE 2 *****************************************************************

#c_table = np.full(3**8, 255, dtype=np.uint8)
#e_table = np.full(2**12, 255, dtype=np.uint8)

#c_table = np.load("p2_corner_table.npy")
#e_table = np.load("p2_edge_table.npy")

scrambles = 100000
scrambles = 1000
scrambles = 0
for _ in range(scrambles):
    c = Digital_Cube()
    c.do_moves(c.generate_scramble(possible_moves=p3_moves))
    scramble = c.generate_scramble(possible_moves=p2_moves, num_moves=16)
    for i in range(len(scramble)):
        c.do_moves([scramble[i]])
        c_index = c.corner_orientation_index(c.corner_orientation())
        e_index = c.binary_index(c.E_edge_locations())
        if(i+1 < c_table[c_index]):
            c_table[c_index] = i+1
            #last_edit = time.time()
#            print("CORNER")
        if(i+1 < e_table[e_index]):
            e_table[e_index] = i+1
            #last_edit = time.time()
#            print("EDGE")


#print(c_table[0:100])

#np.save("p2_corner_table.npy", c_table)
#np.save("p2_edge_table.npy", e_table)

id_table = {1530: 0, 3546: 1, 3994: 2, 3930: 3, 3946: 4, 3945: 5, 3449: 6, 3197: 7, 3885: 8, 4065: 9, 3825: 10, 3645: 11, 3437: 12, 3533: 13, 3564: 14, 3772: 15, 3828: 16, 4020: 17, 3765: 18, 3509: 19, 3479: 20, 3483: 21, 3513: 22, 3499: 23, 3755: 24, 2990: 25, 3046: 26, 1006: 27, 2542: 28, 2750: 29, 2749: 30, 1725: 31, 1469: 32, 1973: 33, 1913: 34, 893: 35, 2429: 36, 2430: 37, 2878: 38, 1950: 39, 2010: 40, 1914: 41, 1910: 42, 3030: 43, 3034: 44, 3050: 45, 2926: 46, 2909: 47, 2903: 48, 983: 49, 989: 50, 887: 51, 955: 52, 1723: 53, 1771: 54, 2795: 55, 2671: 56, 2415: 57, 2925: 58, 3948: 59, 3900: 60, 3855: 61, 4035: 62, 2019: 63, 999: 64, 1013: 65, 509: 66, 1529: 67, 1525: 68, 2549: 69, 2553: 70, 2556: 71, 2550: 72, 3446: 73, 3443: 74, 3383: 75, 3891: 76, 3987: 77, 2463: 78, 2479: 79, 2535: 80, 3558: 81, 3766: 82, 1726: 83, 3769: 84, 3691: 85, 1998: 86, 2006: 87, 2021: 88, 1511: 89, 1719: 90, 1971: 91, 1779: 92, 1011: 93, 3923: 94, 3954: 95, 3898: 96, 3883: 97, 3939: 98, 3435: 99, 3897: 100, 3867: 101, 4017: 102, 3751: 103, 3757: 104, 2989: 105, 943: 106, 4080: 107, 2805: 108, 2791: 109, 2735: 110, 2287: 111, 1263: 112, 3183: 113, 1487: 114, 1695: 115, 2623: 116, 4042: 117, 4056: 118, 4052: 119, 2036: 120, 2033: 121, 1455: 122, 3471: 123, 3407: 124, 495: 125, 751: 126, 766: 127, 2302: 128, 2554: 129, 3542: 130, 3798: 131, 3742: 132, 3646: 133, 3390: 134, 3135: 135, 2239: 136, 3279: 137, 3231: 138, 3167: 139, 3422: 140, 3918: 141, 2895: 142, 2940: 143, 3064: 144, 3832: 145, 3826: 146, 4066: 147, 4049: 148, 1499: 149, 2025: 150, 1005: 151, 2009: 152, 3539: 153, 3569: 154, 2523: 155, 3033: 156, 3036: 157, 3052: 158, 2998: 159, 3004: 160, 3049: 161, 3043: 162, 1847: 163, 3699: 164, 3795: 165, 3027: 166, 3057: 167, 3060: 168, 2877: 169, 2875: 170, 3643: 171, 3763: 172, 2806: 173, 3790: 174, 3019: 175, 3960: 176, 2685: 177, 2679: 178, 2743: 179, 3507: 180, 1977: 181, 2997: 182, 1974: 183, 1978: 184, 703: 185, 3735: 186, 3990: 187, 3996: 188, 3932: 189, 4038: 190, 3359: 191, 3663: 192, 765: 193, 3677: 194, 3929: 195, 3419: 196, 3415: 197, 1655: 198, 3191: 199, 2423: 200, 1399: 201, 1909: 202, 1405: 203, 3485: 204, 3421: 205, 3869: 206, 3727: 207, 2959: 208, 1935: 209, 1995: 210, 1947: 211, 1851: 212, 1907: 213, 3452: 214, 1916: 215, 1871: 216, 879: 217, 1902: 218, 1406: 219, 1391: 220, 3431: 221, 3510: 222, 3811: 223, 3555: 224, 1965: 225, 1949: 226, 3545: 227, 2003: 228, 3783: 229, 1743: 230, 1751: 231, 3293: 232, 2301: 233, 2271: 234, 1151: 235, 1515: 236, 3813: 237, 3045: 238, 1467: 239, 1403: 240, 3953: 241, 3058: 242, 4018: 243, 4003: 244, 3495: 245, 1959: 246, 1943: 247, 1883: 248, 2995: 249, 2547: 250, 3318: 251, 1788: 252, 3708: 253, 2934: 254, 3002: 255, 3863: 256, 3671: 257, 1823: 258, 1631: 259, 1755: 260, 1647: 261, 1599: 262, 3195: 263, 2299: 264, 2803: 265, 3702: 266, 3942: 267, 2526: 268, 2541: 269, 3309: 270, 1773: 271, 2028: 272, 3787: 273, 3001: 274, 447: 275, 1470: 276, 1523: 277, 3486: 278, 510: 279, 479: 280, 2797: 281, 3693: 282, 990: 283, 1785: 284, 3389: 285, 1659: 286, 3705: 287, 3675: 288, 3631: 289, 3247: 290, 4009: 291, 3817: 292, 3820: 293, 3802: 294, 3534: 295, 3789: 296, 4044: 297, 3450: 298, 2175: 299, 3701: 300, 2863: 301, 3615: 302, 2026: 303, 3021: 304, 3022: 305, 1899: 306, 958: 307, 1014: 308, 927: 309, 2967: 310, 2983: 311, 2719: 312, 2767: 313, 2367: 314, 3570: 315, 2034: 316, 1854: 317, 2022: 318, 1782: 319, 2399: 320, 1885: 321, 3687: 322, 3445: 323, 3317: 324, 3198: 325, 3322: 326, 3291: 327, 3294: 328, 3303: 329, 2847: 330, 3911: 331, 3956: 332, 383: 333, 503: 334, 1271: 335, 3527: 336, 1767: 337, 1980: 338, 2040: 339, 2919: 340, 3438: 341, 1277: 342, 1275: 343, 3514: 344, 3818: 345, 3678: 346, 3694: 347, 2798: 348, 4006: 349, 2295: 350, 2494: 351, 1526: 352, 831: 353, 3287: 354, 3262: 355, 3259: 356, 3307: 357, 2539: 358, 3562: 359, 735: 360, 2655: 361, 3915: 362, 3979: 363, 4010: 364, 3770: 365, 3516: 366, 3261: 367, 3501: 368, 1502: 369, 1518: 370, 1003: 371, 3324: 372, 1781: 373, 3255: 374, 2427: 375, 2971: 376, 3814: 377, 1774: 378, 2511: 379, 1532: 380, 3548: 381, 3541: 382, 3917: 383, 1375: 384, 3925: 385, 3989: 386, 863: 387, 3561: 388, 1966: 389, 1963: 390, 2781: 391, 4005: 392, 3941: 393, 1439: 394, 3894: 395, 1517: 396, 1215: 397, 3739: 398, 507: 399, 1278: 400, 1018: 401, 3926: 402, 1886: 403, 987: 404, 2987: 405, 2519: 406, 3993: 407, 3315: 408, 3893: 409, 3576: 410, 763: 411, 957: 412, 894: 413, 891: 414, 2809: 415, 2938: 416, 3706: 417, 4037: 418, 3797: 419, 1247: 420, 2923: 421, 759: 422, 639: 423, 2491: 424, 1463: 425, 3387: 426, 3531: 427, 1895: 428, 951: 429, 1839: 430, 1711: 431, 1495: 432, 2871: 433, 1879: 434, 3015: 435, 2775: 436, 3801: 437, 3639: 438, 2686: 439, 3321: 440, 2779: 441, 1786: 442, 2487: 443, 1757: 444, 1991: 445, 2973: 446, 3741: 447, 1501: 448, 975: 449, 1997: 450, 2493: 451, 2910: 452, 2974: 453, 3502: 454, 2812: 455, 1853: 456, 4024: 457, 2005: 458, 1901: 459, 2525: 460, 3557: 461, 4041: 462, 2907: 463, 3804: 464, 1017: 465, 3981: 466, 2683: 467, 4050: 468, 3310: 469, 3982: 470, 2937: 471, 2810: 472, 3975: 473, 3879: 474, 4012: 475, 3029: 476, 2933: 477, 3758: 478, 2012: 479, 3375: 480, 4068: 481, 3572: 482, 3886: 483, 1662: 484, 1758: 485, 2782: 486, 2747: 487, 1343: 488, 1661: 489, 1020: 490, 4072: 491, 3870: 492, 2931: 493, 255: 494}









#p2_table = np.full(495*2187, 255, dtype=np.uint8)

#p2_table = np.load("p2_table.npy")

#t = time.time()

replaced = 0
new = 0
scrambles = 10000000
scrambles = 100000*800
#48 sec * n
scrambles = 0
for _ in range(scrambles):
    c = Digital_Cube()
    #c.do_moves(c.generate_scramble(possible_moves=p3_moves, num_moves=18))
    scramble = c.generate_scramble(possible_moves=p2_moves, num_moves=11)
    for i in range(len(scramble)):
        c.do_moves([scramble[i]])
        index = c.filter_E_index(c.binary_index(c.E_edge_locations()))*2187 + c.corner_orientation_index(c.corner_orientation())
        if(i+1 < p2_table[index]):
            if(p2_table[index] == 255):
                new += 1
            else:
                replaced += 1
            p2_table[index] = i+1
    if(_ % 100000 == 0 and _ != 0):
        print("NEW: " + str(new))
        print("REP: " + str(replaced))
        print()
        new = 0
        replaced = 0
        np.save("p2_table.npy", p2_table)
#print(new)
#np.save("p2_table.npy", p2_table)

#print(time.time() - t)

#table = np.load("p2_table.npy")
#m = 0
#for c in table:
#    if(c > m):
#        m = c
#print(m)


#PHASE 3 *****************************************************************

#c_table = np.full(math.factorial(8), 255, dtype=np.uint8)
#e_table = np.full(math.factorial(8), 255, dtype=np.uint8)

c_table = np.load("p3_corner_table.npy")
e_table = np.load("p3_edge_table.npy")

#m = 0
#for val in e_table:
#    if(val != 255 and val > m):
#        m = val
#print(m)


#63 sec * n
#100x per 1.75 hrs

scrambles = 100000*1000
scrambles = 0
new = 0
rep = 0
t = time.time()
for _ in range(scrambles):
    c = Digital_Cube()
    c.do_moves(c.generate_scramble(possible_moves=p4_moves, num_moves=16))
    scramble = c.generate_scramble(possible_moves=p3_moves, num_moves=12)
    if(_ % 100000 == 0):
        print("NEW: " + str(new))
        print("REP: " + str(rep))
        new = 0
        rep = 0
        print("TIME: " + str(time.time() - t))
        print("\n")
        np.save("p3_corner_table.npy", c_table)
        np.save("p3_edge_table.npy", e_table)
    for i in range(len(scramble)):
        c.do_moves([scramble[i]])
        c_index = c.index_permutation(c.corner_permutation())
        e_index = c.index_permutation(c.UD_edge_permutation())
        if(i+1 < c_table[c_index]):
            if(c_table[c_index] == 255):
                #print("NEW")
                new += 1
            else:
                rep += 1
            c_table[c_index] = i+1
            #last_edit = time.time()
            #print("CORNER")
        if(i+1 < e_table[e_index]):
            if(e_table[e_index] == 255):
                #print("NEW")
                new += 1
            else:
                rep += 1
            e_table[e_index] = i+1
            #last_edit = time.time()
            #print("EDGE")


#print(c_table[0:100])


print('\n')
print("DONE")

np.save("p3_corner_table.npy", c_table)
np.save("p3_edge_table.npy", e_table)





#c = Digital_Cube()
#c.do_moves(c.generate_scramble())


#corners = c.corner_orientation()
#print(corners)
#print(c.corner_orientation_index(corners))
#edges = c.E_edge_locations()
#print(edges)
#print(c.binary_index(edges))




index_table = {}
c = Digital_Cube()
scrambles = 0
for _ in range(scrambles):
    scramble = c.generate_scramble()
    for move in scramble:
        c.do_moves([move])
        index = c.binary_index(c.E_edge_locations())
        if(not index in index_table):
            index_table[index] = len(index_table)

#print(len(index_table))
#print(index_table)

def num_empty(table):
    count = 0
    for cost in table:
        if(cost == 255):
            count += 1
    return count



#p2_table = np.full(495*2187, 255, dtype=np.uint8)

p2_table2 = np.load("p2_table.npy")

max_depth = 0

for depth in range(7, max_depth):
    c = Digital_Cube()
    p_moves = p2_moves[:]
    starting_moves = p_moves[:]
    path = []
    rep = 0
    start = time.time()
    print("DEPTH: " + str(depth + 1))
    while(True):

        if(len(path) == 0):
            if(len(starting_moves) == 0):
                break
            next_move = starting_moves.pop()
            path.append((next_move, c.moves_left(starting_moves, next_move), c.copy_sides()))
            c.do_moves([next_move])
            index = c.filter_E_index(c.binary_index(c.E_edge_locations()))*2187 + c.corner_orientation_index(c.corner_orientation())
            if(len(path) < p2_table2[index]):
                p2_table2[index] = len(path)
                rep += 1
            print(starting_moves)
            print("TIME: " + str(time.time() - start))
            #print(time.time() - start)
            np.save("p2_table2.npy", p2_table2)

        if(len(path[len(path)-1][1]) == 0):
           failed_move = path.pop()
           c.sides = failed_move[2]

        else:
            if(len(path) < depth+1):
                next_move = path[len(path)-1][1].pop()
                path.append((next_move, c.moves_left(p_moves, next_move), c.copy_sides()))
                c.do_moves([next_move])
                index = c.filter_E_index(c.binary_index(c.E_edge_locations()))*2187 + c.corner_orientation_index(c.corner_orientation())
                if(len(path) < p2_table2[index]):
                    p2_table2[index] = len(path)
                    rep += 1

            else:
                failed_move = path.pop()
                c.sides = failed_move[2]
    print("REPL: " + str(rep))
    print("TIME: " + str(time.time() - start))
    print("LEFT: " + str(num_empty(p2_table2)))
    print("\n")

np.save("p2_table.npy", p2_table2)







def extend_paths_(c, depth, moves, paths, file_name):
    print("DEPTH: " + str(depth))
    table = np.load(file_name)
    new_paths = []
    rep = 0
    start = time.time()
    for path in paths:
        start_len = len(path)
        added_last = False
        c.sides = path[start_len-1][2]
        c.do_moves([path[start_len-1][0]])
        while(True):
            if(len(path) == start_len):
                if(len(path[start_len-1][1]) == 0):
                    added_last = False
                    break
                next_move = path[start_len-1][1].pop()
                #path.append((next_move, c.moves_left(moves, next_move), c.copy_sides()))
                path.append((next_move, moves[:], c.copy_sides()))
                c.do_moves([next_move])
                added_last = True
                index = c.filter_E_index(c.binary_index(c.E_edge_locations()))*2187 + c.corner_orientation_index(c.corner_orientation())
                if(len(path) < table[index]):
                    table[index] = len(path)
                    rep += 1

            if(len(path[len(path)-1][1]) == 0):
                added_last = False
                failed_move = path.pop()
                c.sides = failed_move[2]
            else:
                if(len(path) < depth):
                    next_move = path[len(path)-1][1].pop()
                    #path.append((next_move, c.moves_left(moves, next_move), c.copy_sides()))
                    path.append((next_move, moves[:], c.copy_sides()))
                    c.do_moves([next_move])
                    added_last = True
                    index = c.filter_E_index(c.binary_index(c.E_edge_locations()))*2187 + c.corner_orientation_index(c.corner_orientation())
                    if(len(path) < table[index]):
                        table[index] = len(path)
                        rep += 1
                else:
                    new_paths.append(c.copy_path(path))
                    failed_move = path.pop()
                    c.sides = failed_move[2]
                    added_last = False
    print("REPL: " + str(rep))
    print("LEFT: " + str(num_empty(table)))
    print("TIME: " + str(time.time() - start))
    print(len(new_paths))
    print("\n")
    return new_paths



cube = Digital_Cube()
phase_moves = p2_moves[:]
file = "p2_table2.npy"
paths = []
#for move in phase_moves:
#    paths.append([(move, cube.moves_left(phase_moves, move), cube.copy_sides())])

max_depth = 0

for depth in range(1, max_depth + 1):
    paths = extend_paths(cube, depth, phase_moves, paths, file)








#scp -P 2222 C:\Users\scott\AppData\Local\Programs\Python\Python39\p3_corner_table.npy pi@192.168.1.105:/home/pi


#C:\Users\scott\AppData\Local\Programs\Python\Python39\p1_edge_table.npy    

#C:\Users\scott\AppData\Local\Programs\Python\Python39\p2_table.npy

#C:\Users\scott\AppData\Local\Programs\Python\Python39\p3_edge_table.npy

#C:\Users\scott\AppData\Local\Programs\Python\Python39\p3_corner_table.npy

#C:\Users\scott\AppData\Local\Programs\Python\Python39\corner_table.npy

#C:\Users\scott\AppData\Local\Programs\Python\Python39\edge_table.npy

class Foo:

    def __init__(self):
        pass

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
            for n in range(i, len(moves)):
                if(moves[i][0] != moves[n][0]):
                   break
                mv_streak += 1
                if(len(moves[n]) ==1):
                    turns += 1
                elif(moves[n][1] == "'"):
                    turns -= 1
                else:
                    turns += 2
            net_turns = turns % 4
            if(net_turns == 1 or net_turns == -3):
                condensed_moves.append(moves[i][0])
            elif(net_turns == -1 or net_turns == 3):
                condensed_moves.append(moves[i][0] + "'")
            elif(net_turns == 2):
                condensed_moves.append(moves[i][0] + "2")
            i += mv_streak
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
                expanded_moves +=(setup_moves)
                if(len(moves[i]) == 1):
                    expanded_moves.append("D")
                else:
                    expanded_moves.append("D" + moves[i][1])
                expanded_moves.append(setup_moves)
        return expanded_moves

    def group_parallel_moves(self, moves):
        parallel_moves = {'U':'D','D':'U','R':'L','L':'R','F':'B','B':'F'}
        new_moves = []
        i = 0
        while(i < len(moves)):
            curr_move = moves[i]
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
                


    pass




#moves = ["R", "R'", "U", "L'", "L2", "R", "R2", "R'", "L'", "R", "L", "L'"]
#test = Foo()

#print(moves)
#print(test.group_parallel_moves(moves))












