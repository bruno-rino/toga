import asyncio

import toga
from toga_web.libs import create_element, js
from toga_web.window import Window


class MainWindow(Window):
    def on_close(self, *args):
        pass


class App:
    def __init__(self, interface):
        self.interface = interface
        self.interface._impl = self

    def create(self):
        # self.resource_path = os.path.dirname(os.path.dirname(NSBundle.mainBundle.bundlePath))
        self.native = js.document.getElementById("app-placeholder")

        formal_name = self.interface.formal_name

        self.interface.commands.add(
            # ---- Help menu ----------------------------------
            toga.Command(
                lambda _: self.interface.about(),
                "About " + formal_name,
                group=toga.Group.HELP,
            ),
            toga.Command(
                None,
                "Preferences",
                group=toga.Group.HELP,
            ),
        )

        # Create the menus.
        self.create_menus()

        # Call user code to populate the main window
        self.interface.startup()

    def _create_submenu(self, group, items):
        submenu = create_element(
            "sl-dropdown",
            children=[
                create_element(
                    "span",
                    id=f"menu-{id(group)}",
                    classes=["menu"],
                    slot="trigger",
                    content=group.text,
                ),
                create_element(
                    "sl-menu",
                    children=items,
                ),
            ],
        )
        return submenu

    def create_menus(self):
        self._menu_groups = {}
        submenu = None

        for cmd in self.interface.commands:
            if cmd == toga.GROUP_BREAK:
                submenu = None
            elif cmd == toga.SECTION_BREAK:
                # TODO - add a section break
                pass
            else:
                # TODO - this doesn't handle submenus properly;
                # all menu items will appear in their root group.
                submenu = self._menu_groups.setdefault(cmd.group, [])

                menu_item = create_element(
                    "sl-menu-item",
                    content=cmd.text,
                    disabled=not cmd.enabled,
                )
                menu_item.onclick = cmd.action

                submenu.append(menu_item)

        menu_container = create_element("nav", classes=["menubar"])
        help_menu_container = create_element("nav", classes=["menubar"])

        # If there isn't an explicit app menu group, add an inert placeholder
        if toga.Group.APP not in self._menu_groups:
            menu_container.appendChild(
                create_element(
                    "span",
                    classes=["app"],
                    content=self.interface.formal_name,
                )
            )

        for group, items in self._menu_groups.items():
            submenu = self._create_submenu(group, items)
            if group != toga.Group.HELP:
                menu_container.appendChild(submenu)
            else:
                help_menu_container.appendChild(submenu)

        self.menubar = create_element(
            "header",
            classes=["toga"],
            children=[
                create_element(
                    "a",
                    classes=["brand"],
                    children=[
                        create_element(
                            "img",
                            src="static/logo-32.png",
                            alt=f"{self.interface.formal_name} logo",
                            loading="lazy",
                        )
                    ],
                ),
                menu_container,
                help_menu_container,
            ],
        )

        # Menubar exists at the app level.
        self.native.appendChild(self.menubar)

    def main_loop(self):
        self.create()

    def set_main_window(self, window):
        pass

    def show_about_dialog(self):
        name_and_version = f"{self.interface.formal_name}"

        if self.interface.version is not None:
            name_and_version += f" v{self.interface.version}"

        if self.interface.author is not None:
            copyright = f"\n\nCopyright © {self.interface.author}"

        close_button = create_element(
            "sl-button", slot="footer", variant="primary", content="Ok"
        )
        about_dialog = create_element(
            "sl-dialog",
            id="toga-about-dialog",
            label="About",
            children=[
                create_element("p", content=name_and_version),
                create_element("p", content=copyright),
                close_button,
            ],
        )

        # Create a button handler to capture the close,
        # and destroy the dialog
        def dialog_close(event):
            about_dialog.hide()
            self.native.removeChild(about_dialog)

        close_button.onclick = dialog_close

        # Add the dialog to the DOM.
        self.native.appendChild(about_dialog)

        # The dialog needs to fully render in the DOM, so we can't
        # call show() immediately. Create a task to show the dialog,
        # and queue it to be run "later".
        async def show_dialog():
            about_dialog.show()

        asyncio.create_task(show_dialog())

    def exit(self):
        pass

    def current_window(self):
        self.interface.factory.not_implemented("App.current_window()")

    def enter_full_screen(self, windows):
        self.interface.factory.not_implemented("App.enter_full_screen()")

    def exit_full_screen(self, windows):
        self.interface.factory.not_implemented("App.exit_full_screen()")

    def show_cursor(self):
        self.interface.factory.not_implemented("App.show_cursor()")

    def hide_cursor(self):
        self.interface.factory.not_implemented("App.hide_cursor()")
