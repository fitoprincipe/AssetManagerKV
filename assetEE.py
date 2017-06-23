#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon May 22 10:46:12 2017

@author: labgeo1
"""
from subprocess import call, check_output
from collections import namedtuple
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

import ee


class AssetEE():
    """
    Clase que accede a los assets del usuario mediante el modulo
    subprocess

    :arg: user: usuario de GEE (ejemplo: rprincipe)
    :type: user: str

    Metodos (estaticos):
    | listFolders(path)
    | listFolders2(path)
    | delFolder(path)
    """
    def __init__(self, user):
        # inicia Earth Engine
        try:
            ee.Initialize()
        except Exception as e:
            error = BoxLayout().add_widget(
                Label(text=str(e)))
            return error
        
        self.root = "users/"+user
        # self.folders, self.nombres, self.tipos = self.listFolders2(self.root)
    
    @staticmethod
    def listFolders(path):
        """
        Metodo estatico que devuelve el contenido de un path
        
        completo, nombres = listFolders(path)
        
        Argumentos:
        | **path**: ruta del asset completa
        """
        
        # lista con cada parte del asset
        lista = path.split("/")
        
        base = "/".join([lista[0],lista[1]])+"/" # ej: users/rprincipe/
        #resto = path.lstrip(base) # ej: AP_tierraDelFuego/10NBRcut
        
        # chekeo que el path exista
        check_cont = call(["earthengine", "ls", path])
        # si existe
        if check_cont == 0:
            # leo el contenido
            contenido = check_output(["earthengine", "ls", "-l", path])
            
            # convierto el contenido (str) a una lista
            completo = contenido.split("\n")
            
            # borro la base de cada contenido
            nombres = []            
            for c in completo:
                nombre = c.replace(base, "")
                nombres.append(nombre)
            print nombres
            
            # devuelve la lista de los path completos y
            # la lista de los nombres (sin la base)
            return completo, nombres
        else:
            return None
    
    @staticmethod
    def listFolders2(path):
        """ Enlistar las carpetas de un path

        :param: path: ruta que se quiere enlistar
        :type: path: str

        :returns: namedtuple con las siguientes propiedades:
            :prop: completos: lista con la ruta completa de cada asset
            :type: completos: list
            :prop: nombres: lista con los nombres unicamente de cada asset
            :type: nombres: list
            :prop: tipos: lista con los tipo de elem ("Folder", ImageCollection" o "Image")
            :type: tipos: list
            :prop: error: BoxLayout indicando el error

        :obs: Si no puede obtener los datos del path devuelve un BoxLayout
            con un Label adentro indicando el error
        """
        lista = path.split("/")        
        # base = "/".join([lista[0],lista[1]])+"/" # ej: users/rprincipe/
        # resto = path.lstrip(base) # ej: AP_tierraDelFuego/10NBRcut
        
        # print "base: ",base,"resto ",resto
        try:
            listjson = ee.data.getList({"id":path})
            error = None
        except Exception as e:
            error = BoxLayout().add_widget(Label(text=str(e)))
        else:
            error = BoxLayout().add_widget(Label(text="Sin Errores"))

        completos = []
        nombres = []
        tipos = []
        
        for i, n in enumerate(listjson):
            # print i, "json", n
            tipo = n["type"].decode("utf_8")
            tipos.append(tipo)
            
            completo = n["id"].decode("utf_8")
            completos.append(completo)
            
            lista = completo.split("/")
            
            #nombre = completo.replace(base,"")
            nombre = lista[-1]
            nombres.append(nombre)
            
            #print i, tipo, completo, nombre
            #print tipo, nombre
        #print nombres

        resultado = namedtuple("listFolders2", ("completos", "nombres",
                                                "tipos", "error"
                                               ))

        return resultado(completos, nombres, tipos, error)
        # return completos, nombres, tipos
            
    @staticmethod
    def delFolder(path):
        """
        Método para borrar una carpeta completa
        """
        try:
            #ee.data.deleteAsset(path)            
            call(["earthengine", "rm", "-r", path])
            return True
        except Exception as e:
            print str(e)
