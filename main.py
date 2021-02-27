import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
from PyQt5 import uic
import sqlite3

TABLE_HEADER = ['ID', 'Сорт', 'Обжарка', 'Форма', 'Вкус', 'Цена', 'Объём']


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        self.setFixedSize(self.size())

        self.con = sqlite3.connect('coffee.db')
        self.cur = self.con.cursor()

        self.load_varieties()

    def load_varieties(self):
        result = self.cur.execute("""
            SELECT varieties.id, name, roastin_type.roastin, form.form, taste, price, volume
            FROM (
                varieties INNER JOIN roastin_type
                ON varieties.roastin = roastin_type.id
            ) INNER JOIN form
            ON varieties.form = form.id
        """).fetchall()
        self.tableWidget.setColumnCount(len(TABLE_HEADER))
        self.tableWidget.setHorizontalHeaderLabels(TABLE_HEADER)
        self.tableWidget.setRowCount(len(result))
        for i, record in enumerate(result):
            for j, value in enumerate(record):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(value)))
        self.tableWidget.resizeColumnsToContents()

    def closeEvent(self, event):
        self.con.close()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
