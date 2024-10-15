import sys
import asyncio
import qasync
from PyQt5.QtWidgets import QApplication
from app.windows.application_window import ApplicationWindow


if __name__ == '__main__':
    app = QApplication(sys.argv)
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)
    application_window = ApplicationWindow()
    with loop:
        loop.run_forever()
    sys.exit(app.exec_())
