# -*- coding: utf-8 -*-

from kivy.app import App
from kivy.uix.button import Button


class AssetMan2App(App):
    def build(self):
        pass


class Folder(Button):
    pass

if __name__ == "__main__":
    app = AssetMan2App()
    app.run()