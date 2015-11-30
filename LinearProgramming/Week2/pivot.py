__author__ = 'justme'
from os import path
import numpy as np
import math
import sys

eps = 1.e-4

class Dictionary :
    def __init__(self, basic_indices, non_basic_indices, b_coeff, dict_coeff, obj_value, obj_coeff):
        self._basic_indices = basic_indices
        self._non_basic_indices = non_basic_indices
        self._b_coeff = b_coeff
        self._dict_coeff = dict_coeff
        self._obj_value = obj_value
        self._obj_coeff = obj_coeff

    def pivotBlandRule(self):
        #search first pos. coeff
        entering_idx = len(self._basic_indices) + len(self._non_basic_indices)
        for idx in range(len(self._obj_coeff)):
            if self._obj_coeff[idx] > 0:
                if(entering_idx > len(self._non_basic_indices) - 1) :
                    entering_idx = idx
                elif(self._non_basic_indices[idx] < self._non_basic_indices[entering_idx]) :
                    entering_idx = idx

        if entering_idx < len(self._non_basic_indices):
            min_leaving_coeff = float('inf')
            min_leaving_idx = -1
            for leaving_idx in range(len(self._basic_indices)) :
                coeff = self._dict_coeff[leaving_idx, entering_idx]
                if coeff < 0 :
                    #coeff = coeff / self._b_coeff[leaving_idx]
                    coeff = - self._b_coeff[leaving_idx] / coeff
                    if coeff < min_leaving_coeff :
                        min_leaving_coeff = coeff
                        min_leaving_idx = leaving_idx
                    elif abs(coeff - min_leaving_coeff) <= eps :
                        if self._basic_indices[leaving_idx] < self._basic_indices[min_leaving_idx] :
                            min_leaving_idx = leaving_idx

            if (min_leaving_idx > -1) :
                aij = self._dict_coeff[min_leaving_idx, entering_idx]
                self._dict_coeff[min_leaving_idx, entering_idx] = -1
                self._dict_coeff[min_leaving_idx,] /= -aij
                self._b_coeff[min_leaving_idx] /= -aij

                #update indices
                tmp = self._non_basic_indices[entering_idx]
                self._non_basic_indices[entering_idx] = self._basic_indices[min_leaving_idx]
                self._basic_indices[min_leaving_idx] = tmp

                for basic_idx in range(len(self._basic_indices)):
                    if(basic_idx is not min_leaving_idx) :
                        coeff = self._dict_coeff[basic_idx, entering_idx]
                        self._dict_coeff[basic_idx, entering_idx] = 0
                        self._dict_coeff[basic_idx,] += (coeff*self._dict_coeff[min_leaving_idx,])
                        self._b_coeff[basic_idx] += (coeff * self._b_coeff[min_leaving_idx])

                self._obj_value += (self._obj_coeff[entering_idx]*self._b_coeff[min_leaving_idx])

                coeff = self._obj_coeff[entering_idx]
                self._obj_coeff[entering_idx] = 0
                self._obj_coeff +=  coeff * self._dict_coeff[min_leaving_idx]

                # print(self._dict_coeff)
                # print(self._b_coeff)
                # print(self._obj_value)
                # print(self._obj_coeff)

                return (self._basic_indices[min_leaving_idx] + 1, self._non_basic_indices[entering_idx] + 1, self._obj_value)
            else :
                return None
        else :
            return (-1, -1, self._obj_value)

    def simplex(self):
        init_needed = False
        for b_coef in self._b_coeff:
            if b_coef < 0:
                init_needed = True
                break

        if init_needed:
            orig_obj_coeff = list(self._obj_coeff[:])
            orig_non_basic_ind = list(self._non_basic_indices[:])
            orig_obj_value = self._obj_value

            dual_dict_obj_modif = Dictionary(self._non_basic_indices, self._basic_indices, np.ones(len(self._obj_coeff)),
                               -np.transpose(self._dict_coeff), -self._obj_value, -self._b_coeff)
            is_terminated = False
            while is_terminated is False :
                resultDual = dual_dict_obj_modif.pivotBlandRule()
                if resultDual is None :
                    is_terminated = True
                elif resultDual[0] == -1:
                    is_terminated = True

            if resultDual is not None:
                self._basic_indices  = dual_dict_obj_modif._non_basic_indices
                self._non_basic_indices = dual_dict_obj_modif._basic_indices
                self._b_coeff =  - dual_dict_obj_modif._obj_coeff
                self._obj_coeff = - dual_dict_obj_modif._b_coeff
                self._obj_value = - dual_dict_obj_modif._obj_value
                self._dict_coeff = -np.transpose(dual_dict_obj_modif._dict_coeff)

                self._obj_coeff = np.zeros(len(self._non_basic_indices))
                self._obj_value = 0.
                for idx in  range(0, len(orig_non_basic_ind)):
                    for basic_idx in range(0, len(self._basic_indices)) :
                         if(orig_non_basic_ind[idx] == self._basic_indices[basic_idx]) :
                            self._obj_coeff += orig_obj_coeff[idx]*self._dict_coeff[basic_idx]
                            self._obj_value += orig_obj_coeff[idx]*self._b_coeff[basic_idx]
                            orig_obj_coeff[idx] = 0.
                            break
                    for non_basic_idx in range(0, len(self._non_basic_indices)):
                        if(orig_non_basic_ind[idx] == self._non_basic_indices[non_basic_idx]) :
                            self._obj_coeff[non_basic_idx] += orig_obj_coeff[idx]
                            break

                self._obj_value += orig_obj_value

            else:
                return ('INFEASIBLE', -1)

        is_terminated = False
        while not is_terminated :
            result = self.pivotBlandRule()
            if result is None :
                is_terminated = True
                return ('UNBOUNDED', -1)
            elif result[0] == -1:
                is_terminated = True
                return ('CONVERGED', result[2])

    def plane_cuts_simplex(self):

        orig_basic_var = list(self._basic_indices)
        result = self.simplex()

        if result[0] == 'UNBOUNDED' or result[0] == 'INFEASIBLE' :
            return result

        is_int_sol = False
        while not is_int_sol:

            #check if basic var is integer
            is_int_sol = True
            cutting_row = None
            cutting_bcoeff = None
            min_cutting_idx = sys.maxint
            idx_sel_plane = sys.maxint
            for basic_idx in range(0, len(self._basic_indices)) :
                if abs(self._b_coeff[basic_idx] - math.floor(self._b_coeff[basic_idx] + eps)) > eps :
                    is_int_sol = False
                    #if self._basic_indices[basic_idx] < min_cutting_idx:
                    min_cutting_idx = self._basic_indices[basic_idx]
                    cutting_row = np.array(self._dict_coeff[basic_idx,])
                    cutting_bcoeff = self._b_coeff[basic_idx]
                    idx_sel_plane = basic_idx

                    cut_idx = len(self._basic_indices) + len(self._non_basic_indices)
                    self._basic_indices.resize(len(self._basic_indices) + 1)
                    self._basic_indices[len(self._basic_indices) - 1] = cut_idx
                    self._b_coeff.resize(len(self._b_coeff) + 1)
                    self._b_coeff[len(self._b_coeff) - 1]  = -(self._b_coeff[idx_sel_plane]-math.floor(self._b_coeff[idx_sel_plane]))
                    dict_shape = self._dict_coeff.shape
                    self._dict_coeff.resize((dict_shape[0] + 1, dict_shape[1]))
                    self._dict_coeff[self._dict_coeff.shape[0] -1,] = (-self._dict_coeff[idx_sel_plane,]-np.floor(-self._dict_coeff[idx_sel_plane,]))


            if not is_int_sol :

                # cut_idx = len(self._basic_indices) + len(self._non_basic_indices)
                # self._basic_indices.resize(len(self._basic_indices) + 1)
                # self._basic_indices[len(self._basic_indices) - 1] = cut_idx
                # self._b_coeff.resize(len(self._b_coeff) + 1)
                # self._b_coeff[len(self._b_coeff) - 1]  = -(self._b_coeff[idx_sel_plane]-math.floor(self._b_coeff[idx_sel_plane]))
                # dict_shape = self._dict_coeff.shape
                # self._dict_coeff.resize((dict_shape[0] + 1, dict_shape[1]))
                # self._dict_coeff[self._dict_coeff.shape[0] -1,] = (-self._dict_coeff[idx_sel_plane,]-np.floor(-self._dict_coeff[idx_sel_plane,]))

                dual_dict = Dictionary(self._non_basic_indices, self._basic_indices, -self._obj_coeff,
                                   -np.transpose(self._dict_coeff), -self._obj_value, -self._b_coeff)
                result = dual_dict.simplex()

                if result[0] == 'UNBOUNDED' :
                    return ('INFEASIBLE', -1)
                elif result[0] == 'INFEASIBLE' :
                    return ('UNBOUNDED', -1)

                self._basic_indices  = np.array(dual_dict._non_basic_indices)
                self._non_basic_indices = np.array(dual_dict._basic_indices)
                self._b_coeff = np.array(-dual_dict._obj_coeff)
                self._obj_coeff = np.array(-dual_dict._b_coeff)
                self._obj_value = - dual_dict._obj_value
                self._dict_coeff = np.array(-np.transpose(dual_dict._dict_coeff))

        return ('CONVERGED', self._obj_value)


def load_dictionary(file_name) :
    file_path = path.relpath(file_name)

    with open(file_path, 'rt') as f :
        f.seek(0)
        line = f.readline().split()
        basic_count = int(line[0])
        non_basic_count = int(line[1])

        basic_indices = np.int32(f.readline().split()) - 1
        non_basic_indices = np.int32(f.readline().split()) - 1
        b_coeff = np.float64(f.readline().split())

        dict_coeff = np.zeros((basic_count, non_basic_count), dtype=np.float64)

        for idx in range(basic_count) :
            dict_coeff[idx,:] = np.float64(f.readline().split())

        line = f.readline().split()

        obj_value = np.float64(line[0])
        obj_coeff = np.float64(line[1:])

    f.close()


    simplex_dict = Dictionary(basic_indices, non_basic_indices, b_coeff, dict_coeff, obj_value, obj_coeff)
    return simplex_dict


def writeOutputStep1(result, file_name, is_test) :
    file_path = path.relpath(file_name)
    if(is_test) :
        file_path_test_ref = file_path + '.output'
        with open(file_path_test_ref, 'rt') as test_ref:
            line = test_ref.readline()

            if(line.startswith('UNBOUNDED') ) :
                assert(result is None)
            else:
                entering_ref = int(line)
                assert(entering_ref == result[0])
                leaving_ref = int(test_ref.readline())
                assert(leaving_ref == result[1])
                obj_value = np.float64(test_ref.readline())
                assert(abs(obj_value - result[2]) < 0.001)
        test_ref.close()

    file_path_out = file_path + '.result'

    with open(file_path_out, 'w') as f:
        if result is None:
            f.write('UNBOUNDED\n')
        else:
            f.write(repr(result[0])+'\n')
            f.write(repr(result[1])+'\n')
            f.write(repr(result[2])+'\n')
    f.close()

def writeOutputStep2(obj_value, steps, file_name, is_test) :
    file_path = path.relpath(file_name)
    if(is_test) :
        file_path_test_ref = file_path + '.output'
        with open(file_path_test_ref, 'rt') as test_ref:
            line = test_ref.readline()

            if(line.startswith('UNBOUNDED') ) :
                assert(obj_value is None)
            else:
                obj_value_ref = np.float64(line)
                assert(abs(obj_value - obj_value_ref) < 0.001)
                steps_ref = int(test_ref.readline())
                assert(steps_ref == steps)
        test_ref.close()

    file_path_out = file_path + '.result'

    with open(file_path_out, 'w') as f:
        if obj_value is None:
            f.write('UNBOUNDED\n')
        else:
            f.write(repr(obj_value)+'\n')
            f.write(repr(steps)+'\n')
    f.close()


def writeOutputStep3(obj_value,  file_name, is_test) :
    file_path = path.relpath(file_name)
    if(is_test) :
        file_path_test_ref = file_path[0:-5] + '.output'

        with open(file_path_test_ref, 'rt') as test_ref:
            line = test_ref.readline()

            if(line.startswith('UNBOUNDED') ) :
                assert(obj_value[0] == 'UNBOUNDED')
            elif(line.startswith('INFEASIBLE') ) :
                assert(obj_value[0] == 'INFEASIBLE')
            else:
                obj_value_ref = np.float64(line)
                assert(abs(obj_value[1] - obj_value_ref) < 0.001)

        test_ref.close()

    file_path_out = file_path + '.result'

    with open(file_path_out, 'w') as f:
        if obj_value[0] == 'UNBOUNDED':
            f.write('UNBOUNDED\n')
        elif obj_value[0] == 'INFEASIBLE':
            f.write('INFEASIBLE\n')
        else:
            f.write(repr(obj_value[1])+'\n')
    f.close()


def writeOutputStepIlp(obj_value,  file_name, is_test) :
    file_path = path.relpath(file_name)
    if(is_test) :
        file_path_test_ref = file_path + '.output'

        with open(file_path_test_ref, 'rt') as test_ref:
            line = test_ref.readline()

            if(line.startswith('UNBOUNDED') ) :
                assert(obj_value[0] == 'UNBOUNDED')
            elif(line.startswith('INFEASIBLE') ) :
                assert(obj_value[0] == 'INFEASIBLE')
            else:
                obj_value_ref = np.float64(line)
                assert(abs(obj_value[1] - obj_value_ref) < 0.001)

        test_ref.close()

    file_path_out = file_path + '.result'

    with open(file_path_out, 'w') as f:
        if obj_value[0] == 'UNBOUNDED':
            f.write('UNBOUNDED\n')
        elif obj_value[0] == 'INFEASIBLE':
            f.write('INFEASIBLE\n')
        else:
            f.write(repr(obj_value[1])+'\n')
    f.close()

if __name__ == '__main__':

    # for idx in range(1,11):
    #     file_name = 'step1/unitTests/dict' + str(idx)
    #     simplex_dict = load_dictionary(file_name)
    #     result = simplex_dict.pivotBlandRule()
    #     writeOutputStep1(result, file_name, True)
    #
    # for idx in range(1,6):
    #     file_name = 'step1/assignmentParts/part' + str(idx)+  '.dict'
    #     simplex_dict = load_dictionary(file_name)
    #     result = simplex_dict.pivotBlandRule()
    #     writeOutputStep1(result, file_name, False)
    #
    # for idx in range(1,11):
    #     file_name = 'step2/unitTests/dict' + str(idx)
    #     simplex_dict = load_dictionary(file_name)
    #
    #     is_terminated = False
    #     steps = 0
    #     while not is_terminated :
    #         result = simplex_dict.pivotBlandRule()
    #         if result is None :
    #             is_terminated = True
    #             writeOutputStep2(result, -1, file_name, True)
    #         elif result[0] == -1:
    #             is_terminated = True
    #             writeOutputStep2(result[2],steps, file_name, True)
    #         steps += 1
    #
    # for idx in range(0,110):
    #     file_name = 'step2/moreUnitTests/test' + str(idx) +'.dict'
    #     simplex_dict = load_dictionary(file_name)
    #
    #     is_terminated = False
    #     steps = 0
    #     while not is_terminated :
    #         result = simplex_dict.pivotBlandRule()
    #         if result is None :
    #             is_terminated = True
    #             writeOutputStep2(result, -1, file_name, True)
    #         elif result[0] == -1:
    #             is_terminated = True
    #             writeOutputStep2(result[2],steps, file_name, True)
    #         steps += 1
    #
    # for idx in range(0,10):
    #     file_name = 'step2/moreUnitTests/test0' + str(idx) +'.dict'
    #     simplex_dict = load_dictionary(file_name)
    #
    #     is_terminated = False
    #     steps = 0
    #     while not is_terminated :
    #         result = simplex_dict.pivotBlandRule()
    #         if result is None :
    #             is_terminated = True
    #             writeOutputStep2(result, -1, file_name, True)
    #         elif result[0] == -1:
    #             is_terminated = True
    #             writeOutputStep2(result[2],steps, file_name, True)
    #         steps += 1
    #
    # for idx in range(1,6):
    #     file_name = 'step2/assignmentParts/part' + str(idx) +'.dict'
    #     simplex_dict = load_dictionary(file_name)
    #
    #     is_terminated = False
    #     steps = 0
    #     while not is_terminated :
    #         result = simplex_dict.pivotBlandRule()
    #         if result is None :
    #             is_terminated = True
    #             writeOutputStep2(result, -1, file_name, False)
    #         elif result[0] == -1:
    #             is_terminated = True
    #             writeOutputStep2(result[2],steps, file_name, False)
    #         steps += 1
    #
    # for subfolder in ['10','20','50']:
    #     for idx in range(0,100):
    #         file_name = 'step3/unitTests/' + subfolder + '/test' + str(idx) +'.dict'
    #         simplex_dict = load_dictionary(file_name)
    #         result = simplex_dict.simplex()
    #         writeOutputStep3(result, file_name, True)
    #
    # for idx in range(1,11):
    #     file_name = 'step3/assignmentParts/part' + str(idx) +'.dict'
    #     simplex_dict = load_dictionary(file_name)
    #     result = simplex_dict.simplex()
    #     writeOutputStep3(result, file_name, False)


    file_name = 'ilpTests/assignmentTests/part5.dict'
    simplex_dict = load_dictionary(file_name)
    result = simplex_dict.plane_cuts_simplex()
    writeOutputStepIlp(result, file_name, False)

    # for idx in range(1,5):
    #     file_name = 'ilpTests/assignmentTests/part' + str(idx) +'.dict'
    #     simplex_dict = load_dictionary(file_name)
    #     result = simplex_dict.plane_cuts_simplex()
    #     writeOutputStepIlp(result, file_name, False)
    #
    #
    # for idx in range(0,11):
    #     file_name = 'ilpTests/unitTests/ilpTest' + str(idx)
    #     simplex_dict = load_dictionary(file_name)
    #     result = simplex_dict.plane_cuts_simplex()
    #     writeOutputStepIlp(result, file_name, True)


    # for idx in range(0,100):
    #     file_name = 'ilpTests/unitTests/test' + str(idx)
    #     simplex_dict = load_dictionary(file_name)
    #     result = simplex_dict.plane_cuts_simplex()
    #     writeOutputStepIlp(result, file_name, True)