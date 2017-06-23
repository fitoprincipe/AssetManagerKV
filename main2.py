# -*- coding: utf-8 -*-

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout

from kivy.properties import StringProperty

from kivy.logger import Logger
import json
from assetEE import AssetEE
from functools import partial
import ee


class Principal(BoxLayout):
    pass


class Contenedor(BoxLayout):
    pass


class Scrolling(ScrollView):
    pass


class Menu(BoxLayout):
    """Aca van los widgets que realizan las acciones sobre una o varias carpetas

    Se coloca por encima de la lista de carpetas y queda fijo

    Widgets
    #######

    :widget: Borrar: borra los assets seleccionados llamando a AssetEE.delFolder
    :type: Borrar: kivy.uix.Button


    """
    def __init__(self, **kwargs):
        super(Menu, self).__init__(**kwargs)

    def borrar_click(self):
        Logger.info("borrar")
        activos = self.activos()
        for fila in activos:
            AssetEE.delFolder(fila.path)
            fila.parent.remove_widget(fila)

    def activos(self):
        filas = self.parent.children[:-2]
        # Logger.info(filas)
        filas_activas = []

        for fila in filas:
            check = fila.check
            estado = check.active
            if estado:
                filas_activas.append(fila)

        return filas_activas


class Folder(Button):
    """ Estos son los labels que representan cada asset"""

    path = StringProperty()
    tipo = StringProperty()

    def __init__(self, **kwargs):
        super(Folder, self).__init__(**kwargs)

        self.bind(size=self.setter('text_size'))

        # del folder
        self.lista = self.path.split("/")

        self.orden = len(self.lista) - 2
        self.anterior = "/".join(self.lista[:-1])

        colors = {"red": (1, 0, 0, 1), "green": (0, 1, 0, 1),
                  "blue": (0, 0, 1, 1),
                  "black": (0, 0, 0, 1)}

        self.colores = {"Folder": colors["blue"],
                        "ImageCollection": colors["green"],
                        "Image": colors["red"],
                        "unk": colors["black"]}

        self.background_color = self.colores.get(self.tipo, "unk")

        self.color = self.colores.get(self.tipo, "unk")
        self.background_color = self.color
        self.color = (1, 1, 1, 1)


class ContenedorAssets(GridLayout):
    """ Contiene al Menu, al Encabezado y a las Filas

    """
    cantidad = 0

    def __init__(self, path, **kwargs):
        """ Este es el contenedor de assets """
        super(ContenedorAssets, self).__init__(**kwargs)
        self.bind(minimum_height=self.setter('height'))
        self.path = path
        self.lista = path.split("/")
        self.orden = len(self.lista) - 2
        self.anterior = "/".join(self.lista[:-1])

        # cuenta
        ContenedorAssets.cantidad += 1
        self.n = ContenedorAssets.cantidad


class Encabezado(BoxLayout):
    """el encabezado que está encima de la lista de Filas. Tiene una cruz para
    cerrar el ContenedorAss()"""

    # PROPIEDADES
    texto = StringProperty()

    def __init__(self, **kwargs):
        super(Encabezado, self).__init__(**kwargs)

        self.exit = self.ids["exit_enc"]
        self.check = self.ids["check_enc"]


class Filas(BoxLayout):
    """ Widget que contiene:
    Un <Folder> y un CheckBox

    :prop: path: path completo del asset
    :prop: tipo: tipo de asset (Image, ImageCollection, Folder)

    """

    path = StringProperty()
    tipo = StringProperty()

    def __init__(self, **kwargs):
        super(Filas, self).__init__(**kwargs)

        self.folder = Folder(tipo=self.tipo, path=self.path)
        self.add_widget(self.folder)

        self.check = self.ids["check_fila"]
        # self.folder = self.ids["folder_fila"]


class Error(BoxLayout):
    def __init__(self, **kwargs):
        super(Error, self).__init__(**kwargs)

        # app = App.get_running_app()
        # root = app.root

        self.mje = kwargs.get("mensaje", "no hay mensaje")

        self.mjeWid = Label(text=self.mje)

        #self.mjeWid.text = "app.root: " + str(app.root) + " app: " + str(app)
        self.add_widget(self.mjeWid)


class AssetMan2App(App):
    def __init__(self, **kwargs):
        super(AssetMan2App, self).__init__(**kwargs)
        self.title = "Asset Manager KV ver.0.1 Beta"
        self.user = "rprincipe"

    def build(self):

        # INICIO EARTH ENGINE
        try:
            ee.Initialize()
        except Exception as e:
            # return BoxLayout().add_widget(Label(text=str(e)))
            return Label(text=str(e))

        # INICIO
        self.root = root = Principal()
        self.contenedor = contenedor = Contenedor()

        # FUNCIONES
        def on_checkbox_active(checkbox, value):
            """Selecciona todos las Filas"""
            # checkbox.parent => Encabezado()
            # Encabezado().parent => ContenedorAssets
            # ContenedorAssets.children => Filas (n), Encabezado, Menu
            lista_wid = checkbox.parent.parent.children[:-2]
            for wid in lista_wid:
                # wid.check.active = value
                wid.children[1].active = value

        def addMenu(folder):
            """
            Agregar un ContenedorAsset (Menu, Ecabezado y Filas) nuevo con
            lo que hay dentro de 'folder' (para Folder.click())
            """
            scroll = Scrolling()
            men = ContenedorAssets(folder)
            listfold = asset.listFolders2(folder)
            completo = listfold.completos
            nombres = listfold.nombres
            tipos = listfold.tipos

            # LOGGER
            info_json = ee.data.getInfo(folder)
            info = json.dumps(info_json, indent=2, sort_keys=True,
                              separators=[",", ": "])

            # print info
            # self.infowin.text = info

            if nombres is not None:
                men.add_widget(Menu())
                enc = Encabezado(texto=str(men.orden) + " " + men.path)
                # enc.exit.on_press = partial(root.remove_widget,scroll)
                enc.exit.on_press = partial(contenedor.remove_widget, scroll)
                enc.check.bind(active=on_checkbox_active)
                men.add_widget(enc)
                for n, nom in enumerate(nombres):
                    # print completo[n], tipos[n], nom
                    # lab = Folder(completo[n], tipos[n])
                    lab = Filas(tipo=tipos[n], path=completo[n])
                    lab.folder.text = nom
                    lab.folder.on_press = partial(addMenu, completo[n])
                    men.add_widget(lab)

                scroll.add_widget(men)
                # root.add_widget(scroll)
                contenedor.add_widget(scroll)

        # PRIMER PANTALLA QUE CONTIENE EL CONTENIDO DE user/{user}/
        try:
            asset = AssetEE(self.user)
            root_ass = asset.root
        except Exception as e:
            print str(e)
            err = Error(mensaje=str(e))
            return err

        assCont = ContenedorAssets(asset.root)
        manager = Scrolling()

        root_fold = asset.listFolders2(root_ass)

        if root_fold.error is not None:
            return root_fold.error

        folders = root_fold.completos  # lista de folders (str)
        nom = root_fold.nombres
        tipos = root_fold.tipos

        if len(nom) > 0:

            # MENU
            assCont.add_widget(Menu())

            # ENCABEZADO
            enc = Encabezado(texto=str(assCont.orden) + " " + assCont.path)

            # AGREGO LAS ACCIONES PARA LOS CHILDREN DE Encabezado
            enc.check.bind(active=on_checkbox_active)
            # enc.exit.bind(on_press=)

            assCont.add_widget(enc)
            for n, f in enumerate(nom):
                # lab.on_press = addMenu()
                path = folders[n]
                tipo = tipos[n]
                # lab = Folder(path, tipo)
                lab = Filas(tipo=tipo, path=path)
                lab.folder.on_press = partial(addMenu, path)
                # lab.on_press = partial(Logger.info, tipo+" "+f+" "+folder)

                # TEXTO
                lab.folder.text = f
                assCont.add_widget(lab)

        manager.add_widget(assCont)

        # root.add_widget(manager)
        contenedor.add_widget(manager)
        root.add_widget(contenedor)

        # root.add_widget(menu)
        return root

if __name__ == "__main__":
    app = AssetMan2App()
    app.run()