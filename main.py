import logging
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.RunScriptAction import RunScriptAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from niri import Window
import subprocess




logger = logging.getLogger(__name__)


class NiriWindowsExtension(Extension):

    def __init__(self):
        super(NiriWindowsExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())

class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        search_keyword = event.get_query().get_argument("").lower().split()
        if not search_keyword:
            return

    def matches_query(self, window: Window, query: list[str]):
        '''Enable word-wise fuzzy searching'''

        s = f"{window.get_app_id()} {window.get_title()}".lower()

        for word in query:
            if word not in s:
                return False

        return True

    def get_result_item(self, window):
        return ExtensionResultItem(
                icon=window.get_icon(),
                name=window.get_title(),
                description=window.get_app_id(),
                # This only works because con is a dict, and therefore
                # pickleable
                on_enter=ExtensionCustomAction(window))


class ItemEnterEventListener(EventListener):
    '''Executes the focus event, using the data provided in ExtensionCustomAction'''

    def on_event(self, event, extension):
        window = event.get_data()
        logger.debug("Focusing window: %s", window.get_id())
        window.focus()


if __name__ == '__main__':
    NiriWindowsExtension().run()
