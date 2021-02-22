from fbs_runtime.application_context.PyQt5 import ApplicationContext
from fbs_runtime.application_context import cached_property
from ps_app.views.ui import Ui_MainWindow
import sys
import os

class AppContext(ApplicationContext):
    @cached_property
    def window(self):
        os.environ["PATH"] += os.pathsep + self.get_resource('lib')
        os.environ["PATH"] += os.pathsep + self.get_resource('lib/graphviz')
        os.environ["DYLD_LIBRARY_PATH"] = self.get_resource('lib')
        os.environ["DYLD_LIBRARY_PATH"] += os.pathsep + self.get_resource('lib/graphviz')
        os.environ["DYLD_FALLBACK_LIBRARY_PATH"] = self.get_resource('lib/graphviz')
        return Ui_MainWindow(self.csv_logo)
    @cached_property
    def csv_logo(self):
        return self.get_resource('csv_logo.png')
    def run(self):
        self.window.show()
        return self.app.exec()

if __name__ == '__main__':
    appctxt = AppContext()
    appctxt.run()

