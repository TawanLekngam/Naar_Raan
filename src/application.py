from PySide6.QtWidgets import QStackedWidget

from models import *
from views import *
from controllers import *


class Application(QStackedWidget):

    def __init__(self):
        QStackedWidget.__init__(self, None)
        self.setFixedSize(1920, 1080)
        self.setWindowTitle("Naar Raan")

        self.current_user = None

        # Login Page
        self.login_page = LoginPage(self, LoginView(), LoginModel())

        # home Page
        self.home_page = None

        # start page
        self.addWidget(self.login_page.view)

    def initialize_page(self) -> None:
        "set up method for user."
        if self.current_user is None:
            return

        self.home_page = HomePage(
            self, HomeView(), HomeModel(), self.current_user)

        self.order_page = OrderPage(OrderView(), OrderModel())

        # replace widget if already exist
        self.insertWidget(1, self.home_page.view)
        self.move_to_home()

    def set_current_user(self, user: User) -> None:
        self.current_user = user

    def move_to_login(self):
        self.current_user = None
        self.login_page.clear_input_field()
        self.setCurrentIndex(0)

    def move_to_home(self):
        self.setCurrentIndex(1)

    def start(self) -> None:
        "driver method."
        self.showFullScreen()
