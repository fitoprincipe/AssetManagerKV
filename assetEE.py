#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon May 22 10:46:12 2017

@author: labgeo1
"""
from subprocess import call, check_output

import ee
ee.Initialize()

class AssetEE():
    """
    Clase que accede a los assets del usuario mediante el modulo
    subprocess
    
    Iniciacion:
    | **user**: usuario de GEE (ejemplo: rprincipe)
    |
    Metodos (estaticos):
    | listFolders(path)
    | listFolders2(path)
    | delFolder(path)
    """
    def __init__(self, user):
        # inicia Earth Engine
        ee.Initialize()
        
        self.user = "users/"+user
        self.folders, self.nombres, self.tipos = self.listFolders2(self.user)
    
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
        lista = path.split("/")        
        #base = "/".join([lista[0],lista[1]])+"/" # ej: users/rprincipe/
        #resto = path.lstrip(base) # ej: AP_tierraDelFuego/10NBRcut
        
        #print "base: ",base,"resto ",resto        
        try:
            listjson = ee.data.getList({"id":path})        
        except Exception as e:
            return None, None, None
            '''
            if str(e)[:14] == "No such folder":
                return None, None, None
            else:
                return BoxLayout().add_widget(Label(text=str(e)))
            '''
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
        return completos, nombres, tipos
            
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