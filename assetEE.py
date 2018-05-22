#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon May 22 10:46:12 2017

@author: Rodrigo E. Principe
"""
import ee
ee.Initialize()

def recrusive_delete_asset(assetId):
    try:
        content = ee.data.getList({'id':assetId})
    except:
        return

    if len(content) == 0:
        ee.data.deleteAsset(assetId)
    else:
        for asset in content:
            path = asset['id']
            ty = asset['type']
            if ty == 'Image':
                ee.data.deleteAsset(path)
            else:
                recrusive_delete_asset(path)

def getAssetAcl(assetId):
    return ee.data.getAssetAcl(assetId)

def setAssetAcl(assetId, aclUpdate):
    return ee.data.setAssetAcl(assetId, aclUpdate)