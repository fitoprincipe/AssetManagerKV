# -*- coding: utf-8 -*-
# colors dict
import ee
ee.Initialize()

COLORS = {"red": (1, 0, 0, 0.8),
          "green": (0, 1, 0, 0.8),
          "blue": (0, 0, 1, 0.8),
          "black": (0, 0, 0, 0.8)}

# coltype dict
COLTYPE = {"Folder": COLORS["blue"],
           "ImageCollection": COLORS["green"],
           "Image": COLORS["red"],
           "unk": COLORS["black"]}

USER = ee.data.getAssetRoots()[0]['id']