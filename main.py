# -*- coding: utf-8 -*-

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout

from kivy.properties import StringProperty, ObjectProperty, ListProperty, \
                            NumericProperty

from kivy.logger import Logger as LoggerKV
from assetEE import recrusive_delete_asset
import ee
ee.Initialize()

from config import COLTYPE, USER

# global variables to have access from any widget
logbox = None
logtext = None

# Functions
def on_checkbox_active(checkbox, value):
    """ Select all rows """
    # checkbox.parent => Header()
    # Header().parent => AssetsContainer
    # AssetsContainer.children => Row (n), Header, Menu
    widgets_list = checkbox.parent.parent.children[0].children[0].children#[:-2]
    for widget in widgets_list:
        widget.check.active = value
        widget.children[1].active = value

def add_column():
    pass

class Logger(BoxLayout):
    text = StringProperty()


class GlobalContainer(BoxLayout):
    def __init__(self, **kwargs):
        super(GlobalContainer, self).__init__(**kwargs)
        global logbox
        global logtext

        # redefine global variables
        log = self.ids["box_log"]
        logbox = log.ids["log_action"]
        logtext = log.ids["logger"]


class Container(BoxLayout):
    """ This container is meant to change the layout direction to
        horizontal """
    pass


class Scrolling(ScrollView):
    pass


class Column(BoxLayout):
    """ a Column contain a Menu Widget (in kv file) """
    path = StringProperty(USER) # if no argument is passed, the root path is returned
    text = StringProperty()
    count = 0
    def __init__(self, **kwargs):
        super(Column, self).__init__(**kwargs)
        # Count Columns
        Column.count += 1
        self.assets_count = Column.count

        content = USER if self.path == USER else self.path.replace(USER, '')
        # Text for the column (name of the asset)
        self.text = '{} {}'.format(self.assets_count, content)
        # Menu is created on kv side

        # Create and add Header
        header = Header(text=self.text)
        header.check.bind(active=on_checkbox_active)
        self.add_widget(header)

        # Get content of the path
        path_data = ee.data.getList({'id':self.path})

        # Scroll
        scrolling = Scrolling()
        # Container
        container = AssetsContainer()

        # Add rows to the container
        for asset in path_data:
            # Get data
            path = asset['id']
            name = path.replace(USER, '')
            ty = asset['type']
            # Create Row with data and add to container
            row = Row(path=path, text=name, asset_type = ty)
            container.add_widget(row)

        # Add container to scrolling
        scrolling.add_widget(container)

        # Add scrolling to the column
        self.add_widget(scrolling)


class Menu(BoxLayout):
    """ The menu is placed above each list of folders and stay static. It has
    two buttons predefined in the kv file

    :param delete: a button to delete selected folders using AssetEE.delFolder
    :type delete: kivy.uix.Button
    """
    delete = ObjectProperty()
    share = ObjectProperty()

    def __init__(self, **kwargs):
        super(Menu, self).__init__(**kwargs)

    def click_delete(self):
        """ callback function to delete all active rows """
        LoggerKV.info("delete")
        # get active rows
        active_rows = self.active()
        totaln = len(active_rows)

        for n, row in enumerate(active_rows):
            logtext.text = 'Erasing {} ({}/{})'.format(row.path, n, totaln)
            recrusive_delete_asset(row.path)
            row.parent.remove_widget(row)

        logtext.text = "Erase completed"

    def click_share(self):
        actives = self.active()

        for active in actives:
            # TODO: generar un metodo para que se pueda elegir el tipo de permiso
            AssetEE.shareFolder(active.path, ("@",), "W")

        logtext.text = "Asset shared to .."

    def active(self):
        """ Get active rows

        :return: a list of """
        # Logger.info(rows)
        active_rows = []

        columns = self.parent # a Column
        scrolling = columns.children[0] # a Scrolling
        asset_content = scrolling.children[0] # a AssetsContainer
        rows = asset_content.children # all rows

        for row in rows:
            check = row.check
            state = check.active
            if state: active_rows.append(row)

        return active_rows


class AssetsContainer(GridLayout):
    """ Assets container """

    def __init__(self, **kwargs):
        """ Assets container """
        super(AssetsContainer, self).__init__(**kwargs)
        self.bind(minimum_height=self.setter('height'))


class Header(BoxLayout):
    """ The header is above the list of rows. Has a checkbox to select all
    children, a Label with the path name, and an X to close the Column"""

    # PROPERTIES
    text = StringProperty()
    exit = ObjectProperty()
    reload = ObjectProperty()
    check = ObjectProperty()

    def __init__(self, **kwargs):
        super(Header, self).__init__(**kwargs)

    def close(self, widget):
        t = widget.parent.text # text of self (Header)
        root = t.split(" ") # its a number and a path: 0 root
        if int(root[0]) > 0:
            column = widget.parent.parent # the Column
            container = column.parent # the Container
            container.remove_widget(column)
        else:
            mje = "Can't close root folder"
            logtext.text = mje


class Row(BoxLayout):
    """ This Widget contains a <Folder> and a CheckBox

    :param path: complete path of the asset
    :param asset_type: type of the asset
    :type asset_type: Image | ImageCollection | Folder
    """
    path = StringProperty()
    asset_type = StringProperty()
    text = StringProperty()
    background_color = ListProperty()
    button = ObjectProperty()

    def __init__(self, **kwargs):
        """ This Widget contains a <Folder> and a CheckBox

        :param path: complete path of the asset
        :param asset_type: type of the asset
        :type asset_type: Image | ImageCollection | Folder
        """
        super(Row, self).__init__(**kwargs)
        self.check = self.ids["check_row"]
        self.thebutton = self.ids['row_label']
        self.background_color = COLTYPE[self.asset_type]

    def create_column(self):
        """ Create a Column with the Row data """
        try:
            return Column(path=self.path)
        except:
            return None

    def add_column(self):
        """ Add a column to the Container """
        newcolumn = self.create_column()
        if self.parent and newcolumn:
            asset_container = self.parent # AssetContainer
            scroll = asset_container.parent # Scrolling
            column = scroll.parent # Column
            container = column.parent # Container
            container.add_widget(newcolumn)


class Error(BoxLayout):
    def __init__(self, **kwargs):
        super(Error, self).__init__(**kwargs)
        self.msg = kwargs.get("message", "no message")
        self.msg_widget = Label(text=self.msg)
        self.add_widget(self.msg_widget)


class AssetManApp(App):
    def __init__(self, **kwargs):
        super(AssetManApp, self).__init__(**kwargs)
        self.title = "Asset Manager KV ver.0.1 Beta"

    def close(self, instance):
        self.stop()

    def build(self):
        self.root = root = GlobalContainer()
        self.container = container = Container()

        # Root column
        root_column = Column()

        # Add root column to container
        container.add_widget(root_column)

        # Add container to global container
        root.add_widget(container)

        return root

if __name__ == "__main__":
    app = AssetManApp()
    app.run()