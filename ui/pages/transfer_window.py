from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QLineEdit,
    QVBoxLayout,
    QMessageBox
)

from database import transfer


class TransferWindow(QWidget):

    def __init__(self, account_number):
        super().__init__()

        self.account_number = account_number

        self.setWindowTitle("Transfer Money")
        self.resize(400, 300)

        layout = QVBoxLayout()

        title = QLabel("Transfer Money")

        self.receiver_input = QLineEdit()
        self.receiver_input.setPlaceholderText(
            "Receiver Account Number"
        )

        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText(
            "Amount"
        )

        transfer_button = QPushButton(
            "Transfer"
        )

        transfer_button.clicked.connect(
            self.make_transfer
        )

        layout.addWidget(title)
        layout.addWidget(self.receiver_input)
        layout.addWidget(self.amount_input)
        layout.addWidget(transfer_button)

        self.setLayout(layout)

    def make_transfer(self):

        try:

            receiver = self.receiver_input.text()

            amount = float(
                self.amount_input.text()
            )

            success = transfer(
                self.account_number,
                receiver,
                amount
            )

            if success:

                QMessageBox.information(
                    self,
                    "Success",
                    "Transfer Successful"
                )

                self.close()

            else:

                QMessageBox.warning(
                    self,
                    "Error",
                    "Transfer Failed"
                )

        except ValueError:

            QMessageBox.warning(
                self,
                "Error",
                "Enter a valid amount"
            )