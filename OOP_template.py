# -*- coding: utf-8 -*-
"""
Created on Wed Apr  5 11:36:03 2023

@program: Template Frames system

@author:  LN Starmark
@e-mail1: ln.starmark@ekatra.io
@e-mail2: ln.starmark@gmail.com

"""

import sys
import os

import usb
import usb.core
import usb.util
import win32api

import serial
from serial.tools import list_ports

from threading import Thread, Event
from collections import deque

import configparser as cfprs

import numpy as np
import math as mt
import pandas as pd

from threading import Thread, Event
from collections import deque

import tkinter as tk
from tkinter import ttk
from tkinter import font

from tkinter import messagebox
from tkinter.messagebox import showerror, showwarning, showinfo
import warnings

import time
import timeit
from time import sleep
import datetime
from datetime import date

from PIL import Image, ImageTk

import PFP_parser as prs
import str_common as str_c

###============================================================================
DEBUG = False

PATH_CONFIG = 'config\\Config_OOP_template.ini'
PATH_XLSX = "xlsx\\OOP_template"

PRG_NAME = "Template Frames system"
MAIN_ICON = "img\\dali.png"
MAIN_TITLE = PRG_NAME

PADDING = 5
BAZE_X = 1500
BAZE_Y = 1000
SHFT_X = 0
SHFT_Y = 0

GUI_RESIZABLE_X = False
GUI_RESIZABLE_Y = False

COMMON_LABEL = True
ALL_LABEL = True

BAUDRATE = 19200

POINTS = 25

LARGE_FONT = 8
MON_FONTSIZE = 10
NOTEBOOK_FONTSIZE = 9

COLOR_LAB = {"bg": "azure4", "fg": "antiquewhite1", }
COLOR_FRM = {"bg": "dimgray", "fg": "bisque", }
COLOR_STAT = {"bg": "darkolivegreen", "fg": "antiquewhite1", }
COLOR_TEXT_COMM = {"bg": "darkslategray", "fg": "antiquewhite1", }

COLOR_EVEN_BG = 'DarkSeaGreen1'
COLOR_EVEN_FG = 'navy'
COLOR_ODD_BG = 'lightyellow'
COLOR_ODD_FG = 'brown'

# --- передает данные от потока добывающего данные из порта в поток, заполняющий таблицу в GUI
q = deque()
SEMAPHORE = 0

q2 = deque()
SEMAPHORE_XLSX = 0
XLSX_CAPACITY = 25

# --- для тестирования TreeView
dt = date.today().strftime("%d-%m-%Y")
tm = datetime.datetime.now().strftime("%H:%M:%S")
colwidth = (35, 70, 55, 40, 40, 45, 35, 40, 35, 40, 40, 40, 40,)
colnamesEN = ("NN", "Date", "Time", "Mod", "Wave", "Val", "Unit", "Rep", "Unit", "Res",
              "A_v", "B_v", "C_v",)
measurements = [
    (0, dt, tm, "", 0, 0.0, "dBm", 0, "dBm", "Pass", 0.0, 0.0, 0.0),
    (0, dt, tm, "", 0, 0.0, "dBm", 0, "dBm", "Pass", 0.0, 0.0, 0.0),
]

###--- Factory config -----------------------------------------------------------------
prm = {"MAIN_ICON": MAIN_ICON, "MAIN_TITLE": MAIN_TITLE,
       "BAZE_X": BAZE_X, "BAZE_X": BAZE_Y,
       "SHFT_X": SHFT_X, "SHFT_Y": SHFT_Y,
       "PADDING": PADDING,
       "GUI_RESIZABLE_X": False, "GUI_RESIZABLE_Y": False,
       "COMMON_LABEL": False, "ALL_LABEL": False,
       "MenY": 40,
       "mova": "EN",
       "BAUDRATE": BAUDRATE,
       "points": POINTS,
       }

# --- config ---------------------------------------------------------------------------
class Cfg():
    def __init__(self, path, dct):
        self.path = path
        self.dct = dict(dct)

    ###--- Загрузить config
    def loadConfig(self):
        cfg = cfprs.ConfigParser()  # создаём объекта парсера
        cfg.read(self.path)  # читаем конфиг
        self.dct["MAIN_ICON"] = cfg["Main"]["MAIN_ICON"]
        self.dct["MAIN_TITLE"] = cfg["Main"]["MAIN_TITLE"]
        self.dct["mova"] = cfg["Main"]["mova"]
        self.dct["BAZE_X"] = int(cfg["Main"]["BAZE_X"])
        self.dct["BAZE_Y"] = int(cfg["Main"]["BAZE_Y"])
        self.dct["SHFT_X"] = int(cfg["Main"]["SHFT_X"])
        self.dct["SHFT_Y"] = int(cfg["Main"]["SHFT_Y"])
        self.dct["PADDING"] = int(cfg["Main"]["PADDING"])
        self.dct["GUI_RESIZABLE_X"] = cfg["Main"]["GUI_RESIZABLE_X"]
        self.dct["GUI_RESIZABLE_Y"] = cfg["Main"]["GUI_RESIZABLE_Y"]
        self.dct["COMMON_LABEL"] = cfg["Main"]["COMMON_LABEL"]
        self.dct["ALL_LABEL"] = cfg["Main"]["ALL_LABEL"]
        self.dct["MenY"] = int(cfg["Main"]["MenY"])
        self.dct["BAUDRATE"] = int(cfg["Main"]["BAUDRATE"])
        self.dct["points"] = int(cfg["Main"]["points"])
        # print(self.dct)
        return self.dct

    ###--- Сохранить config
    def saveConfig(self):
        cfg = cfprs.ConfigParser()
        cfg['Main'] = {'MAIN_ICON': self.dct["MAIN_ICON"],
                       'MAIN_TITLE': self.dct["MAIN_TITLE"],
                       'mova': self.dct["mova"],
                       'BAZE_X': self.dct["BAZE_X"],
                       'BAZE_Y': self.dct["BAZE_Y"],
                       'SHFT_X': self.dct["SHFT_X"],
                       'SHFT_Y': self.dct["SHFT_Y"],
                       'PADDING': self.dct["PADDING"],
                       'GUI_RESIZABLE_X': self.dct["GUI_RESIZABLE_X"],
                       'GUI_RESIZABLE_Y': self.dct["GUI_RESIZABLE_Y"],
                       'COMMON_LABEL': self.dct["COMMON_LABEL"],
                       'ALL_LABEL': self.dct["ALL_LABEL"],
                       'MenY': self.dct["MenY"],
                       'BAUDRATE': self.dct["BAUDRATE"],
                       'points': self.dct["points"], }
        with open(self.path, 'w') as configfile:
            cfg.write(configfile)

    def OutConfig(self):
        print("\nCurrent configuration\n")
        print("MAIN_ICON: %s" % self.dct["MAIN_ICON"])
        print("MAIN_TITLE: %s" % self.dct["MAIN_TITLE"])
        print("mova: %s" % self.dct["mova"])
        print("BAZE_X: %d" % self.dct["BAZE_X"])
        print("BAZE_Y: %d" % self.dct["BAZE_Y"])
        print("SHFT_X: %d" % self.dct["SHFT_X"])
        print("SHFT_Y: %d" % self.dct["SHFT_Y"])
        print("PADDING: %d" % self.dct["PADDING"])
        print("GUI_RESIZABLE_X: %s" % str(self.dct["GUI_RESIZABLE_X"]))
        print("GUI_RESIZABLE_Y: %s" % str(self.dct["GUI_RESIZABLE_Y"]))
        print("COMMON_LABEL: %s" % str(self.dct["COMMON_LABEL"]))
        print("ALL_LABEL: %s" % str(self.dct["ALL_LABEL"]))
        print("MenY: %d" % self.dct["MenY"])
        print("BAUDRATE: %d" % self.dct["BAUDRATE"])
        print("points: %d" % self.dct["points"])

    def Get_sWIN(self):
        sWIN = str(self.dct["BAZE_X"]) + "x" + str(self.dct["BAZE_Y"])
        sWIN += "+" + str(self.dct["SHFT_X"]) + "+" + str(self.dct["SHFT_Y"])
        return sWIN

    def Get_Title(self):
        return self.dct["MAIN_TITLE"]

    def Get_GUI_RESIZABLE_X(self):
        return self.dct["GUI_RESIZABLE_X"]

    def Get_GUI_RESIZABLE_Y(self):
        return self.dct["GUI_RESIZABLE_Y"]

    def Get_BAZE_X(self):
        return self.dct["BAZE_X"]

    def Get_BAZE_Y(self):
        return self.dct["BAZE_Y"]

    def Get_PADDING(self):
        return self.dct["PADDING"]

    def Get_Baud(self):
        return self.dct["BAUDRATE"]

    def Get_Points(self):
        return self.dct["points"]

    def Get_Icon(self):
        return self.dct["MAIN_ICON"]

    def Get_COMMON_LABEL(self):
        return self.dct["COMMON_LABEL"]

    def Get_ALL_LABEL(self):
        return self.dct["ALL_LABEL"]

    # --- MetaVariables --------------------------------------------------------------------


class MetaVariables():
    def __init__(self):
        self.statPortText = tk.StringVar()
        self.statPortText.set("Port closed                 ")
        self.InfoAddText = tk.StringVar()
        self.InfoAddText.set("Device not present. Press 'Open' key menu")

        self.NameDevText = tk.StringVar()
        self.NameDevText.set("Factory name")

    def Set_statPortText(self, s):
        self.statPortText.set(s)

    def Set_InfoAddText(self, s):
        self.InfoAddText.set(s)

    def Set_NameDevText(self, s):
        self.NameDevText.set(s)

    def Get_statPortText(self):
        return self.statPortText.get()

    def Get_InfoAddText(self):
        return self.InfoAddText.get()

    def Get_NameDevText(self):
        return self.NameDevText.get()

    # --- Menu -----------------------------------------------------------------------------


class MyMenu():
    def __init__(self, master, com):
        self.com = com

    def create_menu(self):
        file_menu = tk.Menu(tearoff=0)
        file_menu.add_command(label="Open port", command=self.open_click)
        file_menu.add_command(label="Close port", command=self.close_click)
        file_menu.add_command(label="Save XLS", command=self.save_click)
        file_menu.add_command(label="Load Config", command=self.load_config)
        file_menu.add_command(label="Save Config", command=self.save_config)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_click)

        edit_menu = tk.Menu(tearoff=0)
        edit_menu.add_command(label="EditParams", command=self.editParams_click)
        edit_menu.add_command(label="Editconfig", command=self.editConfig_click)

        view_menu = tk.Menu(tearoff=0)
        view_menu.add_command(label="ViewStart", command=self.viewStart_click)

        about_menu = tk.Menu(tearoff=0)
        about_menu.add_command(label="Rules", command=self.rules_click)
        about_menu.add_command(label="Owner", command=self.owner_click)
        about_menu.add_separator()
        about_menu.add_command(label="Author", command=self.author_click)

        # Создано и передано как параметр main_menu
        main_menu = tk.Menu(tearoff=0)
        main_menu.configure(bg="gray")
        main_menu.add_cascade(label="File", menu=file_menu)
        main_menu.add_cascade(label="Edit", menu=edit_menu)
        main_menu.add_cascade(label="View", menu=view_menu)
        main_menu.add_cascade(label="About", menu=about_menu)
        # master.config(menu=main_menu)
        return main_menu

    def finish(self):
        self.com.Port_Close()
        root.destroy()  # ручное закрытие окна и всего приложения
        print("Закрытие приложения")

    def exit_click(self):
        self.finish()

    def open_click(self):
        self.com.Port_Open()

    def close_click(self):
        self.com.Port_Close()

    def save_click(self):
        s = "Save all after working program\n"
        showinfo(title="Save all panel:", message=s)

    def load_config(self):
        self.pem = self.cfg.loadConfig
        # self.cfgedit = self.create_ConfigEditor(self.pem)

    def save_config(self):
        self.cfg.saveConfig()

    def editParams_click(self):
        s = "Fragment program\n"
        s += "Edit parameters program"
        showinfo(title="Editor parameters panel:", message=s)

    def editConfig_click(self):
        s = "Fragment program\n"
        s += "Edit config panel"
        showinfo(title="Editor config panel:", message=s)

    def viewStart_click(self):
        pass

    def author_click(self):
        s = "Programmer\n"
        s += "Starmark LN\n"
        s += "e-mail: ln.starmark@ekatra.io\n"
        s += "e-mail: ln.starmark@gmail.com\n"
        s += "tel: +380 66 9805661"
        showinfo(title="About author:", message=s)

    def owner_click(self):
        s = "STARMARK DESIGN\n"
        s += "help center\n"
        s += "{v 1.01}\n"
        showinfo(title="Owner:", message=s)

    def rules_click(self):
        s = "The program is designed for quick deployment"
        s += "\nof a certain class of window applications"
        s += "\nfor practicing control of remote devices"
        s += "\nvia channels: RS-485, Wi-Fi, nRF24,..."
        showinfo(title="Forewarning:", message=s)

    # --- USB and Comm ---------------------------------------------------------------------


class InfoUSB():
    def __init__(self, master):

        # --- для работы с USB и COM портом
        self.VENDOR_ID = 0x1A86  # vendor ID
        self.PRODUCT_ID = 0x7523  # Device product name
        self.Device_ID = ""
        self.Serial_N = ""
        self.full_name_dev = ""

    def USB_GetID(self, venId, prodId):
        tell1 = "USB\\VID_"
        tell2 = "&PID_"
        tell3 = "\\"
        tellVID = ""
        tellPID = ""
        tellSerialNumber = ""

        print("venId: %s  prodId: %s" % (hex(venId), hex(prodId)))

        win32api.Beep(500, 500)
        # find our device
        dev = usb.core.find(idVendor=venId, idProduct=prodId)
        # was it found?
        if dev is None:
            raise ValueError('***Device not found')
            sys.exit()
        else:
            stdev = str(dev)
            lst_dev = stdev.split("\n")
            sl_dev = lst_dev[:15]
            for el in sl_dev:
                print(el)
                ind = el.find("idVendor", 0)
                if (ind > -1):
                    el.strip()
                    tellVID = el[-6:]
                ind = el.find("idProduct", 0)
                if (ind > -1):
                    el.strip()
                    tellPID = el[-6:]
                ind = el.find("iSerialNumber", 0)
                if (ind > -1):
                    el.strip()
                    ind2 = el.find("0x", 0)
                    if (ind2 > -1):
                        tellSerialNumber = el[ind2:]

        path_to_instance_device = []
        path_to_instance_device.append(tell1)
        path_to_instance_device.append(tellVID)
        path_to_instance_device.append(tell2)
        path_to_instance_device.append(tellPID)
        path_to_instance_device.append(tell3)
        path_to_instance_device.append(tellSerialNumber)

        Dev_ID = path_to_instance_device[0] + \
                 path_to_instance_device[1] + \
                 path_to_instance_device[2] + \
                 path_to_instance_device[3]
        Ser_N = path_to_instance_device[5]

        return Dev_ID, Ser_N

    def Echo_to_USB(self):
        Device_ID, Serial_N = self.USB_GetID(self.VENDOR_ID, self.PRODUCT_ID)
        self.Device_ID = Device_ID
        print("***Device_ID: %s" % Device_ID)
        self.full_name_dev = Device_ID + "\\" + Serial_N
        return Device_ID, Serial_N

    def Out_Full_Names(self):
        print("Fullname USB device: %s" % self.full_name_dev)
        print("Get_DEVID: %s" % self.Get_DEVID())

    def Get_DEVID(self):
        return self.Device_ID


class Comm():
    def __init__(self, master, baudrate, Device_ID, DEV_ID, metavar, metavar2):
        self.dict_stat_port = {"0": " closed  ", "1": " opened  "}
        self.stat_port = 0  # port OFF
        self.metavar = metavar
        self.metavar2 = metavar2

        self.PORT = ""  # port name
        self.ser = None  # descriptor

        self.full_name_port = ""  # для инф
        self.DEV_ID = DEV_ID

        # --- для работы с USB и COM портом
        self.Device_ID = Device_ID
        self.Serial_N = ""

        self.BAUDRATE = baudrate
        self.TIMEOUT = 0.001
        self.count = 0
        self.item = []

    def change_port(self):
        # --- параметр DEV_ID получим как константу
        str_c.zagolovok('Get port from list:')
        nmport = 0
        my_ports = []

        listports = list_ports.comports()

        for port in listports:
            st_port = str(port)
            full_name = st_port

            st_port = st_port[:st_port.index(' ')]
            my_ports.append(st_port)

            prt = str(port)
            ind_tire = prt.find(" - ")

            ind_beg = ind_tire + 3
            prt1 = prt[ind_beg:]

            ind_scoba = prt1.find(" (")
            prt2 = prt1[:ind_scoba]

            print("Device_ID= %s\t DEV_ID= %s" % (self.Device_ID, self.DEV_ID))

            if (self.Device_ID == self.DEV_ID):
                print(prt2)
                print("%5s -> %d" % (st_port, nmport))
                return st_port, full_name
            else:
                nmport += 1

        return "COM0", "COM0"

    def ComPort_Work(self):
        global q
        global SEMAPHORE

        # --- По приходу bBegin {0x7E} переводим start = 1
        # --- потом ждем 2-й байт с количеством байт в посылке
        start = 0
        fl_stop = 0
        # --- должно быть в приходе
        quantity_bytes = 0
        # --- реально пришлых байт
        cnt_bytes = 0

        # --- Сбрасываем буфер приема
        self.ser.flushInput()

        # --- Цикл вычитывания посылки и ее обработка
        while fl_stop == 0:

            # --- буфер для прихода
            lst = []

            # --- Забрать данные из буфера порта, как только появятся
            if (self.ser.in_waiting > 0):
                lin = self.ser.read(self.ser.in_waiting)

                for el in lin:
                    if (el == prs.bBEGIN and start == 0):
                        # --- Наконец встречен стартовый символ. Старт!!!
                        lst.append(el)
                        # --- наращивая количество принятых реально байт
                        cnt_bytes += 1
                        # --- Взвод флажка и переход к ловле блох
                        start = 1
                    else:
                        # --- Запомнить оглашенное в посылке к-во бвйт
                        if (cnt_bytes == 1):
                            quantity_bytes = prs.Get_Quantity(el)
                            # --- и продолжить наполнять список
                        lst.append(el)
                        # --- наращивая количество принятых реально байт
                        cnt_bytes += 1
                        # --- ставим точки от скуки
                        if (DEBUG == True):
                            print(".", end=" ")

                sleep(0.002)

                if (DEBUG == True):
                    print("cnt_bytes = %d" % cnt_bytes)

                    # --- Обрезаем лишние байты с конца списка
                lst = lst[0:quantity_bytes]
                # --- Показать приход
                if (DEBUG == True):
                    self.Print_Codes(lst)

                # --- Парсерить приход -----------------------------------
                dct = {}
                dct = prs.Parser(lst)
                # --------------------------------------------------------

                if (dct["sMode"] == 'INDICATION'):
                    dt = date.today().strftime("%d-%m-%Y")
                    tm = datetime.datetime.now().strftime("%H:%M:%S")
                    self.item.append(self.count)
                    self.item.append(dt)
                    self.item.append(tm)
                    self.item.append(dct['sFM_NAME'])
                    self.item.append(dct['len_wave'])
                    self.item.append(dct['Val_1'])
                    self.item.append(dct['unit_1'])
                    self.item.append(dct['Val_2'])
                    self.item.append(dct['unit_2'])
                    self.item.append(dct['sBell'])
                    BothReading = 1

                if (dct["sMode"] == 'AKK'):
                    mvlt = dct['mvolts[]']
                    self.item.append(mvlt[0] / 1000.)
                    self.item.append(mvlt[1] / 1000.)
                    self.item.append(mvlt[2] / 1000.)
                    BothReading = 2

                if (BothReading == 2):
                    if ((len(q) == 0) and (SEMAPHORE == False)):
                        q.append(self.item)
                        BothReading = 0
                        sleep(0.005)
                        SEMAPHORE = True
                    self.count += 1
                    # --------------------------------------------------------

                # --- Сбросить переменные и флажки для начала нового цикла
                cnt_bytes = 0
                start = 0
                fl_stop = 0

                self.ser.reset_input_buffer()
                self.ser.flushInput()

    def ComPort_Open(self, Port):
        str_c.zagolovok('Port opening:')

        try:
            ser = serial.Serial(
                port=Port,
                baudrate=self.BAUDRATE,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=self.TIMEOUT,
            )
            print("****************************************", ser.port)

            ser.setDTR(False)
            ser.setRTS(False)

            print('\nСоединение удалось.\n')
            return ser

        except serial.SerialException:
            print('\n--- Error: Соединение не удалось ---')
            print()
            sys.exit()

    def Port_Open(self):
        st, self.full_name_port = self.change_port()
        if (st == "COM0"):
            print("* *Device not found: st=%s\tfull_name_port=%s" % (st, self.full_name_port))
        else:
            self.PORT = st

        self.ser = self.ComPort_Open(self.PORT)
        # --- вывод в statusbar табличку ----
        self.metavar2.set(self.full_name_port)
        # -----------------------------------
        self.stat_port = "1"
        self.changePortText(self.stat_port, self.PORT)

        # === Запуск потока приема из порта =========
        Thread(target=self.ComPort_Work, args=()).start()
        # ===========================================

    def Port_Close(self):
        # --- вывод в statusbar табличку ----
        self.full_name_port = "Device closed.      Press 'Open' key menu"
        self.metavar2.set(self.full_name_port)
        # ----------------------------------=
        if (self.stat_port == "1"):
            self.stat_port = "0"
            self.changePortText(self.stat_port, self.PORT)
            print('\nЗакрываем порт')
            self.ser.close()

    def changePortText(self, stat_port, prt):
        str_comm = "Port " + prt + self.dict_stat_port.get(stat_port)
        self.metavar.set(str_comm)

    def Port_Info(self, stat_port):
        # --- Вначале порт закрыт
        if (stat_port == "0"):
            self.changePortText(stat_port, "COMxx")
        print("stat_port = %s\t{%s}" % (stat_port, self.dict_stat_port.get(stat_port)))

    def Print_Codes(self, lst):
        print("< ", end=' ')
        for el in lst:
            print(hex(el), end=' ')
        print(" >\n")


class To_xlsx():
    # --- Применение --------------------------------------------------------------------
    # --- Save_to_xlsx(create_XLSX_name(), 'Main_data', measurements, colnamesEN)
    # -----------------------------------------------------------------------------------
    def __init__(self, master, basename):
        self.basename = basename

    def create_XLSX_name(self):
        dt = date.today().strftime("%d-%m-%Y")
        tm = datetime.datetime.now().strftime("%H-%M-%S")
        name = self.basename
        name += "_"
        name += dt
        name += "_"
        name += tm
        name += ".xlsx"
        return name

    def Save_to_xlsx(self, path, sheet, datalist, colnames):
        df = pd.DataFrame(datalist, columns=colnames)
        print(df)
        # df.to_excel(r'data.xlsx', sheet_name='Main_data', index=False)
        writer = pd.ExcelWriter(path, engine='xlsxwriter')
        df.to_excel(writer, sheet, index=False)
        writer.save()

    ###===========================================================================


class App(ttk.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.pack()

        self.baud = BAUDRATE

        self.COUNT = 0
        self.BLOCK_TO_XLSX = []
        self.XLSX_ERRCOUNT = 0
        self.XLSX_OKCOUNT = 0

        # --- Meta Variables --------------------------------------------------
        self.metaVar = MetaVariables()
        print(self.metaVar.Get_statPortText())
        print(self.metaVar.Get_NameDevText())
        print(self.metaVar.Get_InfoAddText())

        # --- Поиск своего устройства на шине и создание экземпляра порта -----
        self.Device_ID = ""
        self.Serial_N = ""
        self.infoUSB = InfoUSB(self)
        self.Device_ID, self.Serial_N = self.infoUSB.Echo_to_USB()
        self.infoUSB.Out_Full_Names()

        # --- Читаем конфигурацию ---------------------------------------------
        prm = dict()
        self.cfg = Cfg(PATH_CONFIG, prm)
        prm = self.cfg.loadConfig()
        print(prm)
        self.cfg.OutConfig()
        sWIN = self.cfg.Get_sWIN()
        self.baud = self.cfg.Get_Baud()
        self.points = self.cfg.Get_Points()
        self.COMMON_LABEL = self.cfg.Get_COMMON_LABEL()
        self.ALL_LABEL = self.cfg.Get_ALL_LABEL()
        self.BAZE_X = self.cfg.Get_BAZE_X()
        self.BAZE_Y = self.cfg.Get_BAZE_Y()
        self.PADDING = self.cfg.Get_PADDING()

        # --- Для сохранения в xlsx файл создадим экземпляр писателя ----------
        self.to_xlsx = To_xlsx(self, PATH_XLSX)

        # --- Уствнавливает порт ----------------------------------------------
        self.com = Comm(self, self.baud,
                        self.Device_ID, "USB\\VID_0x1a86&PID_0x7523",
                        self.metaVar.statPortText, self.metaVar.InfoAddText)

        # --- Устанавливаем главное окно --------------------------------------
        master.geometry(sWIN)
        master.resizable(self.cfg.Get_GUI_RESIZABLE_X(), self.cfg.Get_GUI_RESIZABLE_Y())
        master.title(self.cfg.Get_Title())
        self.icon = ImageTk.PhotoImage(file=self.cfg.Get_Icon())
        master.iconphoto(False, self.icon)

        # --- Применим стили --------------------------------------------------
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame",
                        background=COLOR_FRM["bg"],
                        foreground=COLOR_FRM["fg"],
                        )
        style.configure("Treeview.Heading",
                        font=('Verdana', LARGE_FONT),
                        background="gray",
                        foreground="yellow",
                        rowheight=int(LARGE_FONT * 2.5),
                        )
        style.configure("Treeview",
                        font=('Arial', NOTEBOOK_FONTSIZE),
                        background="silver",
                        foreground="navy",
                        rowheight=int(LARGE_FONT * 2.5),
                        fieldbackground="silver",
                        )
        style.map('Treeview', background=[('selected', 'purple')])

        self.font_lab = font.Font(family="Arial",
                                  size=11, weight="bold",
                                  slant="roman",
                                  underline=False, overstrike=False)

        # --- строим paneles --------------------------------------------------
        self.pan0 = master
        if (self.COMMON_LABEL == 'True'):
            self.lab0 = self.Lab(self.pan0, tk.TOP, tk.X, "nw", "main_panel 0")

        # --- сразу установим меню --------------------------------------------
        self.menu = MyMenu(self.pan0, self.com)
        self.main_menu = self.menu.create_menu()
        self.master.config(menu=self.main_menu)

        self.frm_status = self.create_BOTTOM(self.pan0, "nw", self.BAZE_X, self.BAZE_Y)
        self.create_statusbar(self.frm_status, self.metaVar.statPortText, self.metaVar.InfoAddText)

        self.pan01 = self.Pan(self.pan0, tk.LEFT, tk.BOTH, "nw", self.BAZE_X / 3 - 2 * self.PADDING,
                              self.BAZE_Y - 2 * self.PADDING)
        if (self.COMMON_LABEL == 'True' and self.ALL_LABEL == 'True'):
            self.lab01 = self.Lab(self.pan01, tk.TOP, tk.X, "nw", "panel 01")

        self.pan02 = self.Pan(self.pan0, tk.LEFT, tk.BOTH, "nw", 2 * self.BAZE_X / 3 - 2 * self.PADDING,
                              self.BAZE_Y - 2 * self.PADDING)
        if (self.COMMON_LABEL == 'True' and self.ALL_LABEL == 'True'):
            self.lab02 = self.Lab(self.pan02, tk.TOP, tk.X, "nw", "panel 02")

        self.pan011 = self.Pan(self.pan01, tk.TOP, tk.BOTH, "nw", self.BAZE_X / 3 - 2 * self.PADDING,
                               5 * self.BAZE_Y / 8 - 2 * self.PADDING)
        if (self.ALL_LABEL == 'True'):
            self.lab011 = self.Lab(self.pan011, tk.TOP, tk.X, "nw", "panel 011: Text field COMM port")
        self.txtComm = self.create_Text(self.pan011, 40, 40, COLOR_TEXT_COMM["bg"], COLOR_TEXT_COMM["fg"], )
        # --- убрать panel0111, ибо она размерная и служила только подпорой ---
        # self.pan0111 = self.Pan(self.pan011, tk.TOP, tk.BOTH, "nw", self.BAZE_X/3-4*self.PADDING, 5*self.BAZE_Y/8-4*self.PADDING)

        self.pan012 = self.Pan(self.pan01, tk.TOP, tk.BOTH, "nw", self.BAZE_X / 3 - 2 * self.PADDING,
                               3 * self.BAZE_Y / 8 - 2 * self.PADDING)
        if (self.ALL_LABEL == 'True'):
            self.lab012 = self.Lab(self.pan012, tk.TOP, tk.X, "nw", "panel 012")
        self.pan0121 = self.Pan(self.pan012, tk.TOP, tk.BOTH, "nw", self.BAZE_X / 3 - 4 * self.PADDING,
                                3 * self.BAZE_Y / 8 - 4 * self.PADDING)

        self.pan021 = self.Pan(self.pan02, tk.TOP, tk.BOTH, "nw", 2 * self.BAZE_X / 3 - 2 * self.PADDING,
                               self.BAZE_Y / 4 - 2 * self.PADDING)
        if (self.ALL_LABEL == 'True'):
            self.lab021 = self.Lab(self.pan021, tk.TOP, tk.X, "nw", "panel 021")
        self.pan0211 = self.Pan(self.pan021, tk.TOP, tk.BOTH, "nw", 2 * self.BAZE_X / 3 - 4 * self.PADDING,
                                self.BAZE_Y / 4 - 4 * self.PADDING)

        self.pan022 = self.Pan(self.pan02, tk.TOP, tk.BOTH, "nw", 2 * self.BAZE_X / 3 - 2 * self.PADDING,
                               3 * self.BAZE_Y / 4 - 2 * self.PADDING)
        if (self.COMMON_LABEL == 'True'):
            self.lab022 = self.Lab(self.pan022, tk.TOP, tk.X, "nw", "panel 022")
        self.pan0221 = self.Pan(self.pan022, tk.TOP, tk.BOTH, "nw", 2 * self.BAZE_X / 3 - 4 * self.PADDING,
                                3 * self.BAZE_Y / 4 - 4 * self.PADDING)

        self.pan0222 = self.Pan(self.pan0221, tk.LEFT, tk.BOTH, "nw", (2 * self.BAZE_X / 3) / 2 - 4 * self.PADDING,
                                3 * self.BAZE_Y / 4 - 4 * self.PADDING)
        if (self.ALL_LABEL == 'True'):
            self.lab0222 = self.Lab(self.pan0222, tk.TOP, tk.X, "nw", "panel 0222: Table data from COMM")
        self.scrollbar = ttk.Scrollbar(master=self.pan0222, orient="vertical")
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree = ttk.Treeview(master=self.pan0222, show="headings", columns=colnamesEN,
                                 yscrollcommand=self.scrollbar.set, height=36)
        self.scrollbar.config(command=self.tree.yview)
        self.Table_to_tabs(self.tree, measurements, colnamesEN, colwidth, self.scrollbar)
        # --- убрать panel02221, ибо она размерная и служила только подпорой ---
        # self.pan02221 = self.Pan(self.pan0222, tk.TOP, tk.BOTH, "nw", (2*self.BAZE_X/3)/2-8*self.PADDING, 3*self.BAZE_Y/4-8*self.PADDING)

        self.pan0223 = self.Pan(self.pan0221, tk.LEFT, tk.BOTH, "nw", (2 * self.BAZE_X / 3) / 2 - 4 * self.PADDING,
                                3 * self.BAZE_Y / 4 - 4 * self.PADDING)
        if (self.ALL_LABEL == 'True'):
            self.lab0223 = self.Lab(self.pan0223, tk.TOP, tk.X, "nw", "panel 0223")

        self.pan02231 = self.Pan(self.pan0223, tk.LEFT, tk.BOTH, "nw", (2 * self.BAZE_X / 3) / 2 - 8 * self.PADDING,
                                 3 * self.BAZE_Y / 4 - 8 * self.PADDING)

        # ===========================================
        Thread(target=self.Item_to_table, args=()).start()
        # ===========================================

        # ===========================================
        Thread(target=self.Save_to_XLSX, args=()).start()
        # ===========================================

        # Регистрация события закрытия окна и привязка к функции
        root.protocol("WM_DELETE_WINDOW", self.menu.finish)

    def Pan(self, mast, sid, fil, anch, wdth, hght):
        frm = ttk.Frame(master=mast, style='TFrame', width=wdth, height=hght,
                        borderwidth=1, relief=tk.SOLID, padding=[self.PADDING, self.PADDING])
        frm.pack(side=sid, expand=True, fill=fil, anchor=anch)
        frm.pack_propagate()
        return frm

    def Lab(self, mast, sid, fil, anch, name):
        lab = tk.Label(master=mast, text=name, font=self.font_lab,
                       bg=COLOR_LAB["bg"], fg=COLOR_LAB["fg"],
                       bd=1, relief=tk.SUNKEN, anchor="c")
        lab.pack(side=sid, expand=True, fill=fil)
        return lab

    def create_BOTTOM(self, mast, anch, wdth, hght):
        frm = ttk.Frame(master=mast, style='TFrame', width=wdth, height=hght,
                        borderwidth=1, relief=tk.SOLID, padding=[0, 0])
        frm.pack(side=tk.BOTTOM, expand=False, fill=tk.Y, anchor=anch)
        return frm

    def create_statusbar(self, mast, metavar, metavar2):
        self.statusbar = tk.Label(mast, textvariable=metavar,
                                  bg=COLOR_STAT["bg"], fg=COLOR_STAT["fg"],
                                  bd=0, relief=tk.SUNKEN, anchor=tk.SW)
        self.statusbar.pack(side=tk.LEFT, fill=tk.X)

        zazor = tk.Label(mast, text="        ",
                         bg=COLOR_STAT["bg"], fg=COLOR_STAT["fg"],
                         bd=0, relief=tk.SUNKEN, anchor=tk.SW)
        zazor.pack(side=tk.LEFT, fill=tk.X)

        self.statusbar2 = tk.Label(mast, textvariable=metavar2,
                                   bg=COLOR_STAT["bg"], fg=COLOR_STAT["fg"],
                                   bd=0, relief=tk.SUNKEN, anchor=tk.SW)
        self.statusbar2.pack(side=tk.LEFT, fill=tk.X)

        ender = tk.Label(mast, text=" " * 500,
                         bg=COLOR_STAT["bg"], fg=COLOR_STAT["fg"],
                         bd=0, relief=tk.SUNKEN, anchor=tk.SW)
        ender.pack(side=tk.LEFT, fill=tk.X)

    def create_Text(self, mast, w, h, b_g, f_g):
        txt = tk.Text(master=mast, width=w, height=h, bg=b_g, fg=f_g, wrap=tk.WORD)
        txt.pack(side=tk.TOP, fill=tk.X)
        return txt

    def Table_to_tabs(self, trvw, measurements, columns, colwidth, scrollbar):
        trvw.pack(fill=tk.X, expand=1, anchor="se")
        # trvw.tag_configure('lightgreen', background='lightgreen')
        # trvw.tag_configure('lightyellow', background='lightyellow')

        # заголовки размещаем на Treeview
        cnt_name = 0
        for el in columns:
            trvw.heading(el, text=colnamesEN[cnt_name], anchor="c")
            num = "#" + str(cnt_name + 1)
            trvw.column(num, stretch=tk.NO, width=colwidth[cnt_name], anchor="c")
            cnt_name += 1

        # добавляем данные
        trvw.tag_configure("evenrow", background=COLOR_EVEN_BG, foreground=COLOR_EVEN_FG)
        trvw.tag_configure("oddrow", background=COLOR_ODD_BG, foreground=COLOR_ODD_FG)
        cnt_tag = 0
        for meas in measurements:
            if (cnt_tag % 2 == 0):
                trvw.insert("", tk.END, values=meas, tags=('evenrow',))
            elif (cnt_tag % 2 != 0):
                trvw.insert("", tk.END, values=meas, tags=('oddrow',))
            cnt_tag += 1

    '''
    def Item_to_table(self):
        global q
        global SEMAPHORE
        global tree
        global COUNT
        while True:      
           if( (len(q) > 0) and (SEMAPHORE == True) ):                    
               itm = q.popleft() 
               print(itm)

               if(COUNT % 2 == 0):
                   tree.insert("", tk.END, values=itm, tags=('evenrow',)) 
               elif(COUNT % 2 != 0):
                   tree.insert("", tk.END, values=itm, tags=('oddrow',))   
               COUNT += 1 

               sleep(0.001)
               SEMAPHORE = False
               itm.clear()  
    '''

    def Item_to_table(self):
        global q
        global SEMAPHORE
        global SEMAPHORE_XLSX

        while True:
            if ((len(q) > 0) and (SEMAPHORE == True)):
                itm = q.popleft()

                # --- вывод в таблицу ----------------------------------
                if (self.COUNT % 2 == 0):
                    self.tree.insert("", tk.END, values=itm, tags=('evenrow',))
                elif (self.COUNT % 2 != 0):
                    self.tree.insert("", tk.END, values=itm, tags=('oddrow',))
                self.tree.yview_scroll(number=1, what="units")

                # --- вывод в xlsx -------------------------------------
                self.BLOCK_TO_XLSX.append(itm.copy())
                if (self.COUNT % XLSX_CAPACITY == 0):
                    SEMAPHORE_XLSX = True

                self.COUNT += 1

                # --- вывод в текстовое окно ---------------------------
                s = ' '.join(map(str, itm))
                s += "\n"
                self.txtComm.insert(tk.INSERT, s)
                self.txtComm.yview_scroll(number=1, what="units")

                sleep(0.002)
                SEMAPHORE = False
                itm.clear()

                # --- вывод в xlsx -------------------------------------

    def Save_to_XLSX(self):
        global SEMAPHORE_XLSX

        while True:
            if (SEMAPHORE_XLSX == True):
                try:
                    self.to_xlsx.Save_to_xlsx(self.to_xlsx.create_XLSX_name(), 'Data',
                                              self.BLOCK_TO_XLSX, colnamesEN)
                    self.XLSX_OKCOUNT += 1
                    print("*** XLSX saving Ok {%d} ***" % self.XLSX_OKCOUNT)
                except:

                    self.XLSX_ERRCOUNT += 1
                    print("*** Error XLSX saving: {%d} ***" % self.XLSX_ERRCOUNT)
                finally:
                    self.BLOCK_TO_XLSX = []
                    SEMAPHORE_XLSX = False

                ###===========================================================================


str_c.titleprogram("GUI application",
                   "Program template window-application",
                   "LN Starmark", mult=str_c.MULT1)
root = tk.Tk()
app = App(master=root)
root.mainloop()
###===========================================================================
