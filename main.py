# -*- coding: utf-8 -*-
"""
Created on Wed Mar  8 11:19:42 2017

@author: labgeo1
"""
from kivy.app import App

# UX
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.graphics import Canvas
from kivy.uix.scrollview import ScrollView
from kivy.uix.checkbox import CheckBox
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.dropdown import DropDown

from kivy.logger import Logger
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.properties import NumericProperty
from kivy.properties import StringProperty

import random
import time
from functools import partial
import json

# from labelscroll_kv import LabelScroll

from assetEE import AssetEE

# EE
import ee


class Principal(BoxLayout):
    def __init__(self, **kwargs):
        """ Este es el contenedor general """
        super(Principal, self).__init__(**kwargs)
        # self.orientation = "vertical"


class Contenedor(BoxLayout):
    def __init__(self, **kwargs):
        """ Este es el contenedor general """
        super(Contenedor, self).__init__(**kwargs)
        # self.orientation = "horizontal"


class Scrolling(ScrollView):
    def __init__(self, **kwargs):
        super(Scrolling, self).__init__(**kwargs)

        self.size_hint = (1, 1)
        # self.size = (Window.width, Window.height)


class PopAuth(Popup):
    def __init__(self, **kwargs):
        super(PopAuth, self).__init__(**kwargs)
        self.title = "Autorizaciones"
        self.size_hint= (None, None)
        self.size = (400, 400)
        # self.auto_dismiss = False

        self.adentro = BoxLayout(orientation="vertical")
        self.email = BoxLayout(orientation="horizontal", size_hint=(1, None),
                               height=30)
        self.email.add_widget(
            Label(text="email: ", size_hint=(None, 1), width=30))
        self.emailText = TextInput()
        self.email.add_widget(self.emailText)

        self.adentro.add_widget(self.email)
        self.content = self.adentro


class Menu(BoxLayout):
    def __init__(self, **kwargs):
        super(Menu, self).__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint = (1, None)
        self.height = 50

        self.borrar = Button(text="BORRAR", size_hint=(0.2, 1))

        # self.activos = self.parent.filas_activas

        def borrar_click(instance):
            activos = self.activos()
            for fila in activos:
                AssetEE.delFolder(fila.path)
                fila.parent.remove_widget(fila)

                # print activos

        self.borrar.bind(on_press=borrar_click)

        self.add_widget(self.borrar)

    def activos(self):
        filas = self.parent.children[:-2]
        filas_activas = []

        for fila in filas:
            check = fila.check
            estado = check.active
            if estado:
                filas_activas.append(fila)

        return filas_activas


class ContenedorAssets(GridLayout):
    cantidad = 0

    def __init__(self, path, **kwargs):
        """ Este es el contenedor de assets """
        super(ContenedorAssets, self).__init__(**kwargs)
        # self.row_force_default = True
        # self.row_default_height = 25
        self.cols = 1
        # self.orientation = "vertical"
        self.size_hint = (1, None)
        self.bind(minimum_height=self.setter('height'))
        self.path = path
        self.lista = path.split("/")
        self.orden = len(self.lista) - 2
        self.anterior = "/".join(self.lista[:-1])

        # cuenta
        ContenedorAssets.cantidad += 1
        self.n = ContenedorAssets.cantidad


class Folder(Button):
    def __init__(self, path, tipo, **kwargs):
        """ Estos son los labels que representan cada asset"""
        super(Folder, self).__init__(**kwargs)
        # self.size_hint = (1, None)

        # del widget        
        self.height = 30
        self.halign = "left"
        self.valign = "middle"
        self.color = (255, 255, 255, 1)
        self.font_size = 20
        self.size_hint = (1, None)
        # self.orientation = "horizontal"

        self.bind(size=self.setter('text_size'))

        # del folder
        self.path = path
        self.tipo = tipo
        self.lista = path.split("/")

        self.orden = len(self.lista) - 2
        self.anterior = "/".join(self.lista[:-1])

        colors = {"red": (1, 0, 0, 1), "green": (0, 1, 0, 1),
                  "blue": (0, 0, 1, 1),
                  "black": (0, 0, 0, 1)}

        self.colores = {"Folder": colors["blue"],
                        "ImageCollection": colors["green"],
                        "Image": colors["red"],
                        "unk": colors["black"]}

        self.color = self.colores.get(self.tipo, "unk")

        self.background_color = self.color
        self.color = (1, 1, 1, 1)

    '''
    def on_release(self):
        #print "boton apretado"
        scroll = Scrolling()
        men = ContenedorAssets()
        completo, nombres = AssetEE.listFolders2(self.path)
        for n, nom in enumerate(nombres):
            lab = Folder(text=nom)
            men.add_widget(lab)                
            
        scroll.add_widget(men)
        self.parent.add_widget(scroll)
    '''


class Filas(BoxLayout):
    def __init__(self, path, tipo, **kwargs):
        super(Filas, self).__init__(**kwargs)
        self.orientation = "horizontal"

        self.path = path
        self.tipo = tipo

        self.text = path

        self.size_hint = (1, None)
        self.height = 30

        self.check = CheckBox()
        self.check.size_hint = (None, 1)
        self.check.width = 20

        self.folder = Folder(self.text, self.tipo)

        self.add_widget(self.check)
        self.add_widget(self.folder)


class Encabezado_old(Button):
    def __init__(self, **kwargs):
        super(Encabezado_old, self).__init__(**kwargs)
        self.size_hint = (0.2, None)
        self.height = 30


class Encabezado(BoxLayout):
    def __init__(self, **kwargs):
        super(Encabezado, self).__init__(**kwargs)
        self.orientation = "horizontal"

        self.text = kwargs.get("text", "No hay texto")

        self.size_hint = (1, None)  # (0.2,None)
        self.height = 30

        # TEXTO
        self.base = Label(text=self.text, font_size=20, size_hint=(0.8, 1))

        # EXIT
        self.exit = Button(text="X", font_size=20, size_hint=(None, 1),
                           width=20)

        # CHECKBOX
        self.check = CheckBox(size_hint=(None, 1), width=20)
        # self.check.

        self.add_widget(self.check)
        self.add_widget(self.base)
        self.add_widget(self.exit)


class Error(BoxLayout):
    def __init__(self, **kwargs):
        super(Error, self).__init__(**kwargs)

        app = App.get_running_app()
        # root = app.root

        self.mje = kwargs.get("mensaje", "no hay mensaje")

        self.orientation = "vertical"
        self.mjeWid = Label(text=self.mje)
        self.salir = Button(text="Salir", size_hint=(0.1, 0.1))
        # self.salir.on_press = partial(app.stop())
        self.mjeWid.text = "app.root: " + str(app.root) + " app: " + str(app)
        self.add_widget(self.mjeWid)
        self.add_widget(self.salir)


class InfoWin(BoxLayout):
    def __init__(self, **kwargs):
        super(InfoWin, self).__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint = (1, 0.3)

        # self.logger = LabelScroll()
        self.logger = Label()
        self.add_widget(self.logger)


class ScrollLabel(BoxLayout):
    text = StringProperty('')

    def __init__(self, **kwargs):
        super(ScrollLabel, self).__init__(**kwargs)
        self.size_hint = (1, 1)

        self.label = Label(text=self.text, size_hint=(1, 1))
        self.add_widget(self.label)


class AssetManApp(App):
    def __init__(self, **kwargs):
        super(AssetManApp, self).__init__(**kwargs)
        # App.__init__(self, **kwargs)
        self.title = "Asset Manager ver.0.1 Beta"

    def on_start(self):
        Logger.info("[Tamaño de la ventana] " + str(Window.size))

    def mje(self):
        Logger.info("resize ventana")

    def build(self):

        self.root = root = Principal()

        self.contenedor = contenedor = Contenedor()

        # '''
        # PARA EL COMIENZO LISTO LO QUE ESTA EN EL ROOT

        try:
            asset = AssetEE("rprincipe")
        except Exception as e:
            print str(e)
            err = Error(mensaje=str(e))
            # err.salir.on_press = partial(self.stop)
            return err
            # return Label(text=str(e))
            # return BoxLayout().add_widget(Label(text=str(e)))#.add_widget(
            # Salir().bind(on_press=self.stop))

        # asset = AssetEE("rprincipe")

        folders = asset.folders  # lista de folders (str)
        nom = asset.nombres
        tipos = asset.tipos

        # '''
        def on_checkbox_active(checkbox, value):
            lista_wid = checkbox.parent.parent.children[:-1]
            for wid in lista_wid:
                wid.check.active = value

        def addMenu(folder):
            """            
            Funcion para agregar la lista del contenido de un folder
            (para Button.click())
            """
            scroll = Scrolling()
            men = ContenedorAssets(folder)
            completo, nombres, tipos = asset.listFolders2(folder)

            # LOGGER
            info_json = ee.data.getInfo(folder)
            info = json.dumps(info_json, indent=2, sort_keys=True,
                              separators=[",", ": "])

            # print info
            self.infowin.text = info

            if nombres is not None:
                men.add_widget(Menu())
                enc = Encabezado(text=str(men.orden) + " " + men.path)
                # enc.exit.on_press = partial(root.remove_widget,scroll)
                enc.exit.on_press = partial(contenedor.remove_widget, scroll)
                enc.check.bind(active=on_checkbox_active)
                men.add_widget(enc)
                for n, nom in enumerate(nombres):
                    # print completo[n], tipos[n], nom
                    # lab = Folder(completo[n], tipos[n])
                    lab = Filas(completo[n], tipos[n])
                    lab.folder.text = nom
                    lab.folder.on_press = partial(addMenu, completo[n])
                    men.add_widget(lab)

                scroll.add_widget(men)
                # root.add_widget(scroll)
                contenedor.add_widget(scroll)

        # menu = contenedorInterno(size_hint=(0.2, None))
        # menu = FloatLayout()
        # manager = contenedorInterno(size_hint=(0.8, None), pos_hint={
        # "top":1})
        # manager = ContenedorAssets()
        assCont = ContenedorAssets(asset.user)
        manager = Scrolling()
        # fold = ["unoaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","dos",
        # "tres",
        #        "cuatro","cinco","seis","site","ocjho","Mieve", "doez"]

        # nom = [str(i) for i in range(100)]
        if nom is not None:
            # print assCont.n
            assCont.add_widget(Menu())
            enc = Encabezado(text=str(assCont.orden) + " " + assCont.path)
            enc.check.bind(active=on_checkbox_active)
            pop = PopAuth()
            enc.exit.bind(on_press=pop.open)

            assCont.add_widget(enc)
            for n, f in enumerate(nom):
                # lab.on_press = addMenu()
                path = folders[n]
                tipo = tipos[n]
                # lab = Folder(path, tipo)
                lab = Filas(path, tipo)
                lab.folder.on_press = partial(addMenu, path)
                # lab.on_press = partial(Logger.info, tipo+" "+f+" "+folder)

                # TEXTO            
                lab.folder.text = f
                assCont.add_widget(lab)
                # Logger.info(str(lab.text_size))

        manager.add_widget(assCont)

        # root.add_widget(manager)
        contenedor.add_widget(manager)
        root.add_widget(contenedor)

        self.infowin = ScrollLabel()  # InfoWin()

        root.add_widget(self.infowin)

        # root.add_widget(menu)
        return root


if __name__ == "__main__":
    unaApp = AssetManApp()
    # unaApp.title = "Asset Manager
    unaApp.run()
