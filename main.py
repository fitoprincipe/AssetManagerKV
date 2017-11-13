# -*- coding: utf-8 -*-

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout

from kivy.properties import StringProperty, ObjectProperty, ListProperty, NumericProperty

from kivy.logger import Logger as LoggerKV
import json
from assetEE import AssetEE
from functools import partial
import ee

logbox = None
logtext = None

COLORS = {"red": (1, 0, 0, 0.8),
          "green": (0, 1, 0, 0.8),
          "blue": (0, 0, 1, 0.8),
          "black": (0, 0, 0, 0.8)}

COLTYPE = {"Folder": COLORS["blue"],
           "ImageCollection": COLORS["green"],
           "Image": COLORS["red"],
           "unk": COLORS["black"]}

class Logger(BoxLayout):
    texto = StringProperty("LOGGER")

class Principal(BoxLayout):
    def __init__(self, **kwargs):
        super(Principal, self).__init__(**kwargs)
        global logbox
        global logtext
        log = self.ids["box_log"]
        logbox = log.ids["log_action"]
        logtext = log.ids["logger"]


class Contenedor(BoxLayout):
    pass


class Scrolling(ScrollView):
    pass


class Columnas(BoxLayout):
    pass


class Menu(BoxLayout):
    """Aca van los widgets que realizan las acciones sobre una o varias carpetas

    Se coloca por encima de la lista de carpetas y queda fijo

    Widgets
    #######

    :widget Borrar: borra los assets seleccionados llamando a AssetEE.delFolder
    :type Borrar: kivy.uix.Button


    """
    borrar = ObjectProperty()

    def __init__(self, **kwargs):
        super(Menu, self).__init__(**kwargs)

    def borrar_click(self):
        LoggerKV.info("borrar")
        activos = self.activos()

        for fila in activos:
            AssetEE.delFolder(fila.path)
            fila.parent.remove_widget(fila)

        logtext.text = "Borrado finalizado!"

    def compartir_click(self):
        activos = self.activos()

        for fila in activos:
            # TODO: generar un metodo para que se pueda elegir el tipo de permiso
            AssetEE.shareFolder(fila.path, ("agustinambouza@gmail.com",), "W")

        logtext.text = "Asset compartido correctamente!"

    def activos(self):
        # Logger.info(filas)
        filas_activas = []

        columnas = self.parent
        scrolling = columnas.children[0]
        contAsset = scrolling.children[0]
        filas = contAsset.children

        for fila in filas:
            check = fila.check
            estado = check.active
            if estado:
                filas_activas.append(fila)

        return filas_activas


class ContenedorAssets(GridLayout):
    """ Contiene al Menu, al Encabezado y a las Filas

    """
    cantidad = 0
    filas = ListProperty([])

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
    exit = ObjectProperty()
    reload = ObjectProperty()
    check = ObjectProperty()

    def __init__(self, **kwargs):
        super(Encabezado, self).__init__(**kwargs)

        # self.exit = self.ids["exit_enc"]
        # self.check = self.ids["check_enc"]

        # self.exit.bind(on_press=self.cerrar)

    def cerrar(self, widget):
        t = widget.parent.texto
        raiz = t.split(" ")
        if int(raiz[0]) > 0:
            columna = widget.parent.parent
            ppal = widget.parent.parent.parent
            ppal.remove_widget(columna)
        else:
            mje = "No se puede cerrar la primer pantalla (root folder)"
            # log.ids["logger"].text = mje
            logtext.text = mje
            print mje, logtext.size


class Filas(BoxLayout):
    """ Widget que contiene:
    Un <Folder> y un CheckBox

    :prop: path: path completo del asset
    :prop: tipo: tipo de asset (Image, ImageCollection, Folder)

    """

    path = StringProperty()
    tipo = StringProperty()
    texto = StringProperty()
    color_fondo = ListProperty()
    boton = ObjectProperty()

    def __init__(self, **kwargs):
        super(Filas, self).__init__(**kwargs)

        self.check = self.ids["check_fila"]

        self.lista = self.path.split("/")

        self.orden = len(self.lista) - 2
        self.anterior = "/".join(self.lista[:-1])

        self.color_fondo = COLTYPE.get(self.tipo, "unk")

class Error(BoxLayout):
    def __init__(self, **kwargs):
        super(Error, self).__init__(**kwargs)

        self.mje = kwargs.get("mensaje", "no hay mensaje")

        self.mjeWid = Label(text=self.mje)

        self.add_widget(self.mjeWid)


class AssetManApp(App):
    def __init__(self, **kwargs):
        super(AssetManApp, self).__init__(**kwargs)
        self.title = "Asset Manager KV ver.0.1 Beta"
        self.user = "rprincipe"

    def cerrar(self, instance):
        self.stop()

    def build(self):

        # INICIO EARTH ENGINE
        try:
            ee.Initialize()
        except Exception as e:
            return Label(text=str(e))

        # INICIO
        self.root = root = Principal()
        self.contenedor = contenedor = Contenedor()
        columnas = Columnas()
        manager = Scrolling()

        # FUNCIONES
        def on_checkbox_active(checkbox, value):
            """Selecciona todos las Filas"""
            # checkbox.parent => Encabezado()
            # Encabezado().parent => ContenedorAssets
            # ContenedorAssets.children => Filas (n), Encabezado, Menu
            lista_wid = checkbox.parent.parent.children[0].children[0].children#[:-2]
            for wid in lista_wid:
                wid.check.active = value
                wid.children[1].active = value

        def addMenu(folder):
            """
            Agregar un ContenedorAsset (Menu, Ecabezado y Filas) nuevo con
            lo que hay dentro de 'folder' (para Folder.click())
            """
            col = Columnas()
            scroll = Scrolling()
            men = ContenedorAssets(folder)
            listfold = asset.listFolders2(folder)

            if listfold is None:
                return None

            completo = listfold.completos
            nombres = listfold.nombres
            tipos = listfold.tipos

            # LOGGER
            info_json = ee.data.getInfo(folder)
            info = json.dumps(info_json, indent=2, sort_keys=True,
                              separators=[",", ": "])


            if nombres is not None:
                enc = Encabezado(texto=str(men.orden) + " " + men.path)
                enc.exit.on_press = partial(contenedor.remove_widget, scroll)
                enc.check.bind(active=on_checkbox_active)
                col.add_widget(enc)
                for n, nom in enumerate(nombres):
                    lab = Filas(tipo=tipos[n], path=completo[n], texto=nom)
                    lab.boton.on_press = partial(addMenu, completo[n])
                    men.add_widget(lab)

                scroll.add_widget(men)
                col.add_widget(scroll)
                contenedor.add_widget(col)

        # PRIMER PANTALLA QUE CONTIENE EL CONTENIDO DE user/{user}/
        try:
            asset = AssetEE(self.user)
            root_ass = asset.root
        except Exception as e:
            print str(e)
            err = Error(mensaje=str(e))
            return err

        assCont = ContenedorAssets(asset.root)

        root_fold = asset.listFolders2(root_ass)

        if root_fold is None:
            return Label(text="There is no data in the main path")

        folders = root_fold.completos  # lista de folders (str)
        nom = root_fold.nombres
        tipos = root_fold.tipos

        if len(nom) > 0:

            # ENCABEZADO
            enc = Encabezado(texto=str(assCont.orden) + " " + assCont.path)

            # AGREGO LAS ACCIONES PARA LOS CHILDREN DE Encabezado
            enc.check.bind(active=on_checkbox_active)
            columnas.add_widget(enc)

            for n, f in enumerate(nom):
                path = folders[n]
                tipo = tipos[n]
                lab = Filas(tipo=tipo, path=path, texto=f)
                lab.boton.on_press = partial(addMenu, path)
                assCont.add_widget(lab)

        manager.add_widget(assCont)

        columnas.add_widget(manager)
        contenedor.add_widget(columnas)
        root.add_widget(contenedor)

        return root

if __name__ == "__main__":
    app = AssetManApp()
    app.run()