from fbs_runtime.application_context.PyQt5 import ApplicationContext
from fbs_runtime.application_context import cached_property
from ps_app.views.ui import Ui_MainWindow


class AppContext(ApplicationContext):
    @cached_property
    def window(self):
        return Ui_MainWindow(self.excel_logo)

    @cached_property
    def csv_logo(self):
        return self.get_resource('csv_logo.png')

    @cached_property
    def excel_logo(self):
        return self.get_resource('excel_logo.png')

    def run(self):
        self.window.show()
        return self.app.exec()


if __name__ == '__main__':
    appctxt = AppContext()
    appctxt.run()
