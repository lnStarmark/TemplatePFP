# -*- coding: utf-8 -*-
"""
Программа чтения бинарного файла
и расшифровка данных по протоколу
Created on Mon Feb 24 01:36:29 2023

PARSER

@author: ln.starmark@ekatra.io
       : ln.starmark@gmail.com
"""

import sys
import numpy as np
import str_common as str_c

DEBUG = False
DEBUGOUT = False

# --- Шаблоны для парсера -----------------------

# --- byte 1 ---------------------------
bBEGIN = 0x7E

# --- byte 2 ---------------------------
bMODE_EMIT = 0x10
sMODE_EMIT = "EMITTION"

bMODE_LSCAN = 0x20
sMODE_LSCAN = "LSCAN"

bMODE_IND = 0x40
sMODE_IND = "INDICATION"

bMODE_SCAN = 0x60
sMODE_SCAN = "SCAN"

bMODE_AKK = 0x70
sMODE_AKK = "AKK"

bMODE_STACK_IND = 0xF1
sMODE_STACK_IND = "STACK_IND"

bMODE_STACK_SCAN = 0xF2
sMODE_STACK_SCAN = "STACK_SCAN"

mode = 0
quantity_bytes = 0
dctMode = {bMODE_EMIT: sMODE_EMIT,
           bMODE_LSCAN: sMODE_LSCAN,
           bMODE_IND: sMODE_IND,
           bMODE_SCAN: sMODE_SCAN,
           bMODE_AKK: sMODE_AKK,
           bMODE_STACK_IND: sMODE_STACK_IND,
           bMODE_STACK_SCAN: sMODE_STACK_SCAN}

add_val_EMIT = 0
add_val_LSCAN = 0

add_val_IND = 10
add_val_SCAN = 10

add_val_INDAKK = 10
add_val_LAKK = 0
# --------------------------------------

# --- byte 3 ---------------------------
BELL_PASS = 0x00
BELL_FAIL = 0x80
sBELL_PASS = "PASS"
sBELL_FAIL = "FAIL"
bell = 0
dctBell = {BELL_PASS: sBELL_PASS,
           BELL_FAIL: sBELL_FAIL}

fm = 0
FM_270 = 0x00
FM_330 = 0x01
FM_1000 = 0x02
FM_2000 = 0x03
FM_CW = 0x04
FM_NA = 0x05
sFM_NAME = ["270 Hz", "330 Hz", "1 kHz", "2 kHz", "CW", "N/A"]

num_scan = 0
SCAN_1 = 0x01
SCAN_2 = 0x02
SCAN_3 = 0x03
SCAN_4 = 0x04
sSCAN_N = ["SCAN_1", "SCAN_2", "SCAN_3", "SCAN_4"]
# --------------------------------------

# --- byte 4 ---------------------------
# === Первое число со знаком и типом индикации mode INDICATION
val_1 = 0.0
unit_1 = 0
type_ind_1 = 0

IND5 = 0x00  # формат числа  1.234
IND6 = 0x20  # формат числа  12.34
IND7 = 0x40  # формат числа  123.4
sIND = {0x00: "IND5", 0x20: "IND6", 0x40: "IND7", }

UNIT0 = 0x00
UNIT2 = 0x20
UNIT4 = 0x40
UNIT6 = 0x60
UNIT8 = 0x80
sUNIT = ["mW", "", "mkW", "", "nW", "", "dBm", "", "dB"]

timeauto = 0
timeeco = 0

tauto_stat = 0
teco_stat = 0

sTAUTO_STAT_ON = "ON"
sTECO_STAT_ON = "ON"

sTAUTO_STAT_OFF = "OFF"
sTECO_STAT_OFF = "OFF"

sTAUTO_STAT = {0x80: sTAUTO_STAT_ON, 0x00: sTAUTO_STAT_OFF, }
sTECO_STAT = {0x80: sTECO_STAT_ON, 0x00: sTECO_STAT_OFF, }

val2 = 0
len_wave = 0
EmitLenWave = 0

# --- Мощность из оперативной ячейки памяти mode INDICATION
val_2 = 0.0
unit_2 = 0
type_ind_2 = 0

# --- Первое число со знаком и типом индикации mode SCAN
val_3 = 0.0
unit_3 = 0
type_ind_3 = 0

# --- Мощность принятая по оптическому каналу  mode SCAN
val_4 = 0.0
unit_4 = 0
type_ind_4 = 0

# val3 = 0.0

# --- Для работы с AKK --------------------
type_AKK = 0  ###--- 0 для IND; 1 для EMIT
MAME_AKK = ["AKK_B", "AKK_A", "AKK_C"]

# --- хранить в списке
mvolts = []
# --- хранить в списке
emit_volts = []

form_emit = 0
val_emit = 0
type_ind_emit = 0
unit_emit = 0

num_emit = 0
val_scan = 0
type_ind_scan = 0
unit_scan = 0

full_status = 0
bit_SCAN = 0x80
bit_USB = 0x20
bit_SIMMETR = 0x04
bit_AKKDATA = 0x01

# --- Сохрвнять в список
sStatus = []
sON_SCAN = "SCAN ON"
sON_USB = "USB ON"
sON_SIMMETR = "SIMMETR ON"
sON_AKKDATA = "DATA READY"

sOFF_SCAN = "SCAN OFF"
sOFF_USB = "USB OFF"
sOFF_SIMMETR = "SIMMETR OFF"
sOFF_AKKDATA = "DATA NOT READY"

# --- Global variables --------------------------
PORT = ''

dict_res_to_GUI = {}


###==========================================================================
###--- Функции
###==========================================================================

def Parser(lst):
    np_array = np.asarray(lst)

    if (DEBUG == True):
        str_c.zagolovok('Парсинг данных:')
        print("1\tИсходные данные из порта подготавливаем к обработке: ")

    CRC_Control(np_array)

    mode, quantity_bytes, type_AKK = Get_ModeQuantity(np_array, 1)

    if (DEBUG == True):
        print("\n3\tРежим и количество байт:", end='  ')
        Out_ModeQuantity(mode, quantity_bytes)
        print()

    if (mode == bMODE_IND):
        fm, bell = Get_FmBell(np_array, 2)
        val_1, type_ind_1, unit_1 = Get_FloatFormat(np_array, 3, mode)
        tauto_stat, timeauto = Get_AutoStat(np_array, 6)
        teco_stat, timeeco = Get_EcoStat(np_array, 7)
        len_wave = Get_LenWave(np_array, 8)
        val_2, type_ind_2, unit_2 = Get_FloatFormat(np_array, 11, mode)

        if (DEBUG == True):
            OutAll_by_ModeIND(fm, bell,
                              val_1, type_ind_1, unit_1,
                              tauto_stat, timeauto,
                              teco_stat, timeeco,
                              len_wave,
                              val_2, type_ind_2, unit_2)

        # --- Для вывода в GUI Tkinter --------------------------------
        dict_res_to_GUI.clear()
        Create_dictResModeIND(dict_res_to_GUI, mode,
                              fm, bell,
                              val_1, type_ind_1, unit_1,
                              tauto_stat, timeauto,
                              teco_stat, timeeco,
                              len_wave,
                              val_2, type_ind_2, unit_2)
        if (DEBUGOUT == True):
            Out_dictRes(dict_res_to_GUI)
            # -------------------------------------------------------------

    elif (mode == bMODE_SCAN):
        fm, num_scan = Get_FmNumscan(np_array, 2)
        val_3, type_ind_3, unit_3 = Get_FloatFormat(np_array, 3, mode)
        len_wave = Get_LenWave(np_array, 6)
        val_4, type_ind_4, unit_4 = Get_FloatFormat(np_array, 9, mode)

        if (DEBUG == True):
            OutAll_by_MODE_AKK(fm, num_scan,
                               val_3, type_ind_3, unit_3,
                               len_wave,
                               val_4, type_ind_4, unit_4)

            # --- Для вывода в GUI Tkinter --------------------------------
        dict_res_to_GUI.clear()
        Create_dictResModeSCAN(dict_res_to_GUI, mode,
                               fm, num_scan,
                               val_3, type_ind_3, unit_3,
                               len_wave,
                               val_4, type_ind_4, unit_4)
        if (DEBUGOUT == True):
            Out_dictRes(dict_res_to_GUI)
            # -------------------------------------------------------------

    elif (mode == bMODE_AKK):
        if (type_AKK == 0):
            mvolts = Get_AkkVolts(np_array, 2)
        elif (type_AKK == 1):
            mvolts = Get_AkkVolts(np_array, 2)
        full_status, sStatus = Get_FullStatus(np_array, 8)

        if (DEBUG == True):
            OutAll_by_MODE_AKK(mvolts, sStatus)

            # --- Для вывода в GUI Tkinter --------------------------------
        dict_res_to_GUI.clear()
        Create_dictResModeAKK(dict_res_to_GUI, mode,
                              mvolts,
                              full_status, sStatus)
        if (DEBUGOUT == True):
            Out_dictRes(dict_res_to_GUI)
            # -------------------------------------------------------------

    elif (mode == bMODE_EMIT):
        fm, form_emit = Get_FmEmit(np_array, 2)
        val_emit, type_ind_emit, unit_emit = Get_PowerEmit(np_array, 5)

        if (DEBUG == True):
            OutAll_by_MODE_EMIT(fm, form_emit,
                                val_emit, type_ind_emit, unit_emit)

        # --- Для вывода в GUI Tkinter --------------------------------
        dict_res_to_GUI.clear()
        Create_dictResModeEMIT(dict_res_to_GUI, mode,
                               fm, form_emit,
                               val_emit, type_ind_emit, unit_emit)
        if (DEBUGOUT == True):
            Out_dictRes(dict_res_to_GUI)
            # -------------------------------------------------------------


    elif (mode == bMODE_LSCAN):
        fm, num_scan = Get_EmitFmNumscan(np_array, 2)
        num_emit = Get_NumEmit(np_array, 4)
        EmitLenWave = Get_EmitLenWave(np_array, 6)
        val_scan, type_ind_scan, unit_scan = Get_PowerEmit(np_array, 7)

        if (DEBUG == True):
            OutAll_by_MODE_LSCAN(fm, num_scan,
                                 num_emit,
                                 EmitLenWave,
                                 val_scan, type_ind_scan, unit_scan)

    if (DEBUG == True):
        str_c.zagolovok('Конец  парсинга')

    return dict_res_to_GUI


###==========================================================================

def Create_dictResModeIND(dict_res, mode,
                          fm, bell,
                          val_1, type_ind_1, unit_1,
                          tauto_stat, timeauto,
                          teco_stat, timeeco,
                          len_wave,
                          val_2, type_ind_2, unit_2):
    dict_res["sMode"] = dctMode[mode]
    dict_res["sFM_NAME"] = sFM_NAME[fm]
    dict_res["sBell"] = dctBell[bell]
    dict_res["Val_1"] = val_1
    dict_res["type_ind_1"] = sIND[type_ind_1]
    dict_res["unit_1"] = sUNIT[unit_1]
    dict_res["sTAUTO_STAT"] = sTAUTO_STAT[tauto_stat]
    dict_res["tauto_stat"] = tauto_stat
    dict_res["sTECO_STAT"] = sTECO_STAT[teco_stat]
    dict_res["teco_stat"] = teco_stat
    dict_res["len_wave"] = len_wave
    dict_res["Val_2"] = val_2
    dict_res["type_ind_2"] = sIND[type_ind_2]
    dict_res["unit_2"] = sUNIT[unit_2]


def Create_dictResModeSCAN(dict_res, mode,
                           fm, num_scan,
                           val_3, type_ind_3, unit_3,
                           len_wave,
                           val_4, type_ind_4, unit_4):
    dict_res["sMode"] = dctMode[mode]
    dict_res["sFM_NAME"] = sFM_NAME[fm]
    dict_res["sSCAN_N"] = sSCAN_N[num_scan - 1]
    dict_res["Val_3"] = val_3
    dict_res["type_ind_3"] = sIND[type_ind_3]
    dict_res["unit_3"] = sUNIT[unit_3]
    dict_res["len_wave"] = len_wave
    dict_res["Val_4"] = val_4
    dict_res["type_ind_4"] = sIND[type_ind_4]
    dict_res["unit_4"] = sUNIT[unit_4]


def Create_dictResModeAKK(dict_res, mode,
                          mvolts,
                          full_status, sStatus):
    dict_res["sMode"] = dctMode[mode]
    dict_res["mvolts[]"] = mvolts
    dict_res["full_status"] = full_status
    dict_res["sStatus"] = sStatus


def Create_dictResModeEMIT(dict_res, mode,
                           fm, form_emit,
                           val_emit, type_ind_emit, unit_emit):
    dict_res["sMode"] = dctMode[mode]
    dict_res["fm"] = fm
    dict_res["sFM_NAME"] = sFM_NAME[form_emit]
    dict_res["val_emit"] = val_emit
    dict_res["type_ind_emit"] = sIND[type_ind_emit]
    dict_res["unit_emit"] = sUNIT[unit_emit]


def Out_dictRes(dict_res):
    print()
    print(dict_res)
    print()


def OutAll_by_ModeIND(fm, bell,
                      val_1, type_ind_1, unit_1,
                      tauto_stat, timeauto,
                      teco_stat, timeeco,
                      len_wave,
                      val_2, type_ind_2, unit_2):
    print("\n4\tЧастота и прозвонка:", end='\t')
    Out_FmBell(fm, bell)
    print("\n5\tПервое число со знаком и типом индикации:", end='\t')
    Out_FloatFormat(val_1, type_ind_1, unit_1)
    print("\n6\tЗнач. уст. времени  до  АВТОВЫКЛЮЧЕНИЯ:", end='\t')
    Out_AutoStat(tauto_stat, timeauto)
    print("\n7\tЗнач. време. до перех. в режим ЭКОНОМ:", end='\t')
    Out_EcoStat(teco_stat, timeeco)
    print("\n8\tВторое число индикации Длина волны:\t\t", end='\t')
    Out_LenWave(len_wave)
    print("\n9\tМощность из оперативной ячейки памяти:\t", end='\t')
    Out_FloatFormat(val_2, type_ind_2, unit_2)


def OutAll_by_MODE_SCAN(fm, num_scan,
                        val_3, type_ind_3, unit_3,
                        len_wave,
                        val_4, type_ind_4, unit_4):
    print("4\tЧастота и номер SCAN:", end='\t')
    Out_FmNumscan(fm, num_scan)
    print("\n5\tПервое число со знаком и типом индикации:", end='\t')
    Out_FloatFormat(val_3, type_ind_3, unit_3)
    print("\n6\tВторое число индикации Длина волны:\t\t", end='\t')
    Out_LenWave(len_wave)
    print("\n7\tМощность принятая по оптическому каналу:", end='\t')
    Out_FloatFormat(val_4, type_ind_4, unit_4)


def OutAll_by_MODE_AKK(mvolts, sStatus):
    print("4   Напряжение на %s :\tMode{%s}" % (dctMode.get(mode), hex(mode)))
    if (type_AKK == 0):
        Out_AkkVolts(mvolts)
    elif (type_AKK == 1):
        Out_AkkVolts(mvolts)
    print("5   Состояние контроллера: ", end='\t')
    Out_FullStatus(sStatus)


def OutAll_by_MODE_EMIT(fm, form_emit,
                        val_emit, type_ind_emit, unit_emit):
    print("4\tЧастота FM:", end='\t')
    Out_FmEmit(fm, form_emit)
    print("\n5\tВыходная мощность излучения:", end='\t')
    Out_PowerEmit(val_emit, type_ind_emit, unit_emit)


def OutAll_by_MODE_LSCAN(fm, num_scan,
                         num_emit,
                         EmitLenWave,
                         val_scan, type_ind_scan, unit_scan):
    print("\n4\tЧастота FM и номер LSCAN:", end='\t')
    Out_EmitFmNumscan(fm, num_scan)
    print("\n5\tПорядковый номер емиттера:", end='\t')
    Out_NumEmit(num_emit)
    print("\n6\tДлина волны емиттера:", end='\t\t\t')
    Out_EmitLenWave(EmitLenWave)
    print("\n7\tВыходная мощность излучения:", end='\t')
    Out_PowerEmit(val_scan, type_ind_scan, unit_scan)


# ============================================================================

def CRC_Control(nparray):
    ln = len(nparray)

    if (ln == 0):
        print("\t\t--- Read error ---")
        sys.exit()

    else:
        last_crc = nparray[ln - 1]
        sm_crc = (sum(nparray) - last_crc) & 0x00FF

        sMode = dctMode.get(nparray[1] & 0xF0)

        if (DEBUG == True):
            print("\n2\tПроверка CRC mode{%s}: " % (sMode), end=' ')
            if (sm_crc == last_crc):
                print("\tCRC: 0x%x == lastCRC: 0x%x " % (sm_crc, last_crc))
            else:
                print("\t\t--- CRC error ---")
                return 1


###--------------------------------------------------------------------------

def Get_Quantity(arg):
    if (arg & 0xF0 == bMODE_AKK):
        if (arg & 0x0F == 0):
            quant = (arg & 0x0F) + add_val_INDAKK
        else:
            quant = (arg & 0x0F) + add_val_LAKK
    elif (arg & 0xF0 == bMODE_IND):
        quant = (arg & 0x0F) + add_val_IND
    elif (arg & 0xF0 == bMODE_SCAN):
        quant = (arg & 0x0F) + add_val_SCAN
    elif (arg & 0xF0 == bMODE_EMIT):
        quant = (arg & 0x0F) + add_val_EMIT
    elif (arg & 0xF0 == bMODE_LSCAN):
        quant = (arg & 0x0F) + add_val_LSCAN

    return quant


###--------------------------------------------------------------------------

def Get_ModeQuantity(nparray, index):
    type_AKK = -1
    mode = nparray[index] & 0xF0

    if (mode == bMODE_IND):
        quantity_bytes = (nparray[index] & 0x0F) + add_val_IND
    elif (mode == bMODE_SCAN):
        quantity_bytes = (nparray[index] & 0x0F) + add_val_SCAN
    elif (mode == bMODE_AKK):
        if (nparray[index] & 0x0F == 0):
            quantity_bytes = (nparray[index] & 0x0F) + add_val_INDAKK
            type_AKK = 0
        else:
            quantity_bytes = (nparray[index] & 0x0F) + add_val_LAKK
            type_AKK = 1
    elif (mode == bMODE_STACK_IND):
        quantity_bytes = 0
    elif (mode == bMODE_STACK_SCAN):
        quantity_bytes = 0

    elif (mode == bMODE_EMIT):
        quantity_bytes = (nparray[index] & 0x0F) + add_val_EMIT
    elif (mode == bMODE_LSCAN):
        quantity_bytes = (nparray[index] & 0x0F) + add_val_LSCAN

    else:
        print("\tMode = 0x%x --- Mode error ---" % mode)
        sys.exit()

    return mode, quantity_bytes, type_AKK


def Out_ModeQuantity(mode, quantity_bytes):
    print("Mode:{0x%x}\t" % mode, end='')
    print("%s\t" % dctMode.get(mode), end='')
    if ((mode == bMODE_EMIT) or
            (mode == bMODE_SCAN) or
            (mode == bMODE_IND) or
            (mode == bMODE_SCAN) or
            (mode == bMODE_AKK)):
        print("Quantity bytes: %d" % quantity_bytes)


def Out_Mode_Quantity(mode, quantity_bytes):
    print("Mode:{0x%x}\t" % mode, end='')
    print("%s\t" % dctMode.get(mode), end='')
    print("Quantity bytes: %d" % quantity_bytes)


###--------------------------------------------------------------------------

def Get_FmBell(nparray, index):
    bell = nparray[index] & 0x80
    fm = nparray[index] & 0x0F
    return fm, bell


def Out_FmBell(fm, bell):
    if (bell == BELL_PASS):
        print("\tBell: %s" % sBELL_PASS, end='')
    else:
        print("\tBell: %s" % sBELL_FAIL, end='')
    print("\tFM: %d\t\t%s" % (fm, sFM_NAME[fm]))


###--------------------------------------------------------------------------

def Get_FmNumscan(nparray, index):
    num_scan = nparray[index] & 0x0F
    fm = (nparray[index] & 0xF0) >> 4
    return fm, num_scan


def Out_FmNumscan(fm, num_scan):
    ###print("\n4\tnum_SCAN и FM: ", end=' ' )
    print("\tNumSCAN:{%d}\t\t %s" % (num_scan, sSCAN_N[num_scan - 1]), end='')
    print("\tFM:{%d}\t\t%s" % (fm, sFM_NAME[fm]))


###--------------------------------------------------------------------------

def Get_FmEmit(nparray, index):
    form = nparray[index] & 0x0F
    fm = nparray[index + 1] * 256
    fm = fm | nparray[index + 2]
    return fm, form


def Out_FmEmit(fm, form):
    print("\tFM: %d\t\t%s" % (fm, sFM_NAME[form]))


###--------------------------------------------------------------------------

def Get_FloatFormat(nparray, index, mode):
    sign = nparray[index] & 0x80
    type_ind = nparray[index] & 0x60
    if (mode == bMODE_IND):
        unit = (nparray[index + 1] & 0xF0) >> 4
    elif (mode == bMODE_SCAN):
        unit = UNIT6 >> 4

    val = (nparray[index] & 0x0F) * 1000.0
    val = val + (nparray[index + 1] & 0x0F) * 100.0
    val = val + ((nparray[index + 2] & 0xF0) >> 4) * 10.0
    val = val + (nparray[index + 2] & 0x0F)

    if (type_ind == IND5):
        val = val / 1000.0
    elif (type_ind == IND6):
        val = val / 100.0
    elif (type_ind == IND7):
        val = val / 10.0

    if (sign != 0x80):
        val = val * (-1.0)

    return val, type_ind, unit


def Out_FloatFormat(val, type_ind, unit):
    if (type_ind == IND5):
        print("%4.3f" % val, end=' ')
    elif (type_ind == IND6):
        print("%4.2f" % val, end=' ')
    elif (type_ind == IND7):
        print("%4.1f" % val, end=' ')
    else:
        print("%4.0f" % val, end=' ')

    print("%s" % sUNIT[unit])  # --- переделать на словарь


###--------------------------------------------------------------------------

def Get_EmitFmNumscan(nparray, index):
    fm = (nparray[index] & 0x0F)
    num_scan = nparray[index + 1] & 0x0F
    return fm, num_scan


def Out_EmitFmNumscan(fm, num_scan):
    ###print("\n4\tnum_SCAN и FM: ", end=' ' )
    print("\tNumSCAN:{%d}\t\t %s" % (num_scan, sSCAN_N[num_scan - 1]), end='')
    print("\tFM:{%d}\t\t%s" % (fm, sFM_NAME[fm]))


###--------------------------------------------------------------------------

def Get_PowerEmit(nparray, index):
    sign = nparray[index] & 0x80
    type_ind = IND5  # --- Только этот формат!!!
    unit = UNIT6 >> 4  # --- Только эти ед. изм.

    val = (nparray[index] & 0x7F) * 1000
    val = val + ((nparray[index + 1] & 0xF0) >> 4) * 100
    val = val + (nparray[index + 1] & 0x0F) * 10

    if (type_ind == IND5):
        val = val / 1000.0
    elif (type_ind == IND6):
        val = val / 100.0
    elif (type_ind == IND7):
        val = val / 10.0

    if (sign != 0x80):
        val = val * (-1.0)

    return val, type_ind, unit


def Out_PowerEmit(val, type_ind, unit):
    if (type_ind == IND5):
        print("%4.3f" % val, end=' ')

    print("%s" % sUNIT[unit])


###--------------------------------------------------------------------------

def Get_NumEmit(nparray, index):
    return nparray[index]


def Out_NumEmit(num_emit):
    print("\tNumber emitter:  %d" % num_emit)


###--------------------------------------------------------------------------

def Get_EmitLenWave(nparray, index):
    val = nparray[index] * 256
    val = val + (nparray[index + 1])
    return val


def Out_EmitLenWave(val):
    print("Emit LEN_WAVE:\t %d" % val)


###--------------------------------------------------------------------------

def Get_AutoStat(nparray, index):
    tauto_stat = nparray[index] & 0x80
    timeauto = nparray[index] & 0x0F
    return tauto_stat, timeauto


def Out_AutoStat(tauto_stat, timeauto):
    if (tauto_stat == 0x80):
        print("\tЗаряд: %s" % sTAUTO_STAT_ON, end='\t')
    else:
        print("\tЗаряд: %s" % sTAUTO_STAT_OFF, end='\t')
    print("\tTIME_AUTO: %d" % timeauto)


###--------------------------------------------------------------------------

def Get_EcoStat(nparray, index):
    teco_stat = nparray[index] & 0x80
    timeeco = nparray[index] & 0x0F
    return teco_stat, timeeco


def Out_EcoStat(teco_stat, timeeco):
    if (teco_stat == 0x80):
        print("\tКанал USB: %s" % sTECO_STAT_ON, end='\t')
    else:
        print("\tКанал USB: %s" % sTECO_STAT_OFF, end='\t')
    print("TIME_ECO: %d" % timeeco)


###--------------------------------------------------------------------------

def Get_LenWave(nparray, index):
    val = nparray[index] * 1000
    val = val + (nparray[index + 1] & 0x0F) * 100
    val = val + (nparray[index + 2] >> 4) * 10
    val += (nparray[index + 2] & 0x0F)
    return val


def Out_LenWave(val):
    print("LEN_WAVE: %d" % val)


###--- AKK {надо заменить на сохранение в список !!!} -----------------------
def Get_AkkVolts(nparray, index):
    lst = []
    val16 = nparray[index] * 256
    val16 += nparray[index + 1]
    lst.append(val16)
    val16 = nparray[index + 2] * 256
    val16 += nparray[index + 3]
    lst.append(val16)
    val16 = nparray[index + 4] * 256
    val16 += nparray[index + 5]
    lst.append(val16)
    return lst


def Out_AkkVolts(mvolts):
    i = 0
    for el in mvolts:
        print("\t\tMvolt[%i]: %4.2f v" % (i, el / 1000.0))
        i += 1


def Get_FullStatus(nparray, index):
    sStatus = []
    stat = nparray[index]
    if (stat & bit_SCAN == bit_SCAN):
        sStatus.append(sON_SCAN)
    else:
        sStatus.append(sOFF_SCAN)
    if (stat & bit_USB == bit_USB):
        sStatus.append(sON_USB)
    else:
        sStatus.append(sOFF_USB)
    if (stat & bit_SIMMETR == bit_SIMMETR):
        sStatus.append(sON_SIMMETR)
    else:
        sStatus.append(sOFF_SIMMETR)
    if (stat & bit_AKKDATA == bit_AKKDATA):
        sStatus.append(sON_AKKDATA)
    else:
        sStatus.append(sOFF_AKKDATA)

    return stat, sStatus


def Out_FullStatus(sStatus):
    print(sStatus)


###==========================================================================

