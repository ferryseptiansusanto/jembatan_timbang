import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from modules.Login.login_main import LoginMain
from modules.setup.initialize import initialize_superuser

initialize_superuser()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login = LoginMain()
    login.show()
    sys.exit(app.exec_())