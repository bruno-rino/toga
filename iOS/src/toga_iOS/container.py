from .libs import (
    UIApplication,
    UINavigationController,
    UIView,
    UIViewController,
)


class BaseContainer:
    def __init__(self, content=None, on_refresh=None):
        """A base class for iOS containers.

        :param content: The widget impl that is the container's initial content.
        :param on_refresh: The callback to be notified when this container's layout is
            refreshed.
        """
        self._content = content
        self.on_refresh = on_refresh

        # iOS renders everything at 96dpi.
        self.dpi = 96
        self.baseline_dpi = self.dpi

    @property
    def content(self):
        """The Toga implementation widget that is the root content of this container.

        All children of the root content will also be added to the container as a result
        of assigning content.

        If the container already has content, the old content will be replaced. The old
        root content and all it's children will be removed from the container.
        """
        return self._content

    @content.setter
    def content(self, widget):
        if self._content:
            self._content.container = None

        self._content = widget
        if widget:
            widget.container = self

    def refreshed(self):
        if self.on_refresh:
            self.on_refresh()


class Container(BaseContainer):
    def __init__(self, content=None, layout_native=None, on_refresh=None):
        """
        :param content: The widget impl that is the container's initial content.
        :param layout_native: The native widget that should be used to provide size
            hints to the layout. This will usually be the container widget itself;
            however, for widgets like ScrollContainer where the layout needs to be
            computed based on a different size to what will be rendered, the source of
            the size can be different.
        :param on_refresh: The callback to be notified when this container's layout is
            refreshed.
        """
        super().__init__(content=content, on_refresh=on_refresh)
        self.native = UIView.alloc().init()
        self.native.translatesAutoresizingMaskIntoConstraints = True

        self.layout_native = self.native if layout_native is None else layout_native

    @property
    def width(self):
        return self.layout_native.bounds.size.width

    @property
    def height(self):
        return self.layout_native.bounds.size.height

    @property
    def top_offset(self):
        return 0


class RootContainer(Container):
    def __init__(
        self,
        content=None,
        layout_native=None,
        on_refresh=None,
    ):
        """
        :param content: The widget impl that is the container's initial content.
        :param layout_native: The native widget that should be used to provide
            size hints to the layout. This will usually be the container widget
            itself; however, for widgets like ScrollContainer where the layout
            needs to be computed based on a different size to what will be
            rendered, the source of the size can be different.
        :param on_refresh: The callback to be notified when this container's layout is
            refreshed.
        """
        super().__init__(
            content=content,
            layout_native=layout_native,
            on_refresh=on_refresh,
        )

        # Construct a NavigationController that provides a navigation bar, and
        # is able to maintain a stack of navigable content. This is initialized
        # with a root UIViewController that is the actual content
        self.content_controller = UIViewController.alloc().init()
        self.controller = UINavigationController.alloc().initWithRootViewController(
            self.content_controller
        )

        # Set the controller's view to be the root content widget
        self.content_controller.view = self.native

    @property
    def height(self):
        return self.layout_native.bounds.size.height - self.top_offset

    @property
    def top_offset(self):
        return (
            UIApplication.sharedApplication.statusBarFrame.size.height
            + self.controller.navigationBar.frame.size.height
        )

    @property
    def title(self):
        return self.controller.topViewController.title

    @title.setter
    def title(self, value):
        self.controller.topViewController.title = value