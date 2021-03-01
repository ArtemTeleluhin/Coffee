import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
from PyQt5 import uic
import sqlite3

TABLE_HEADER = ['ID', 'Сорт', 'Обжарка', 'Форма', 'Вкус', 'Цена', 'Объём']
MAX_VALUE = 10 ** 6


class AddEditCoffeeForm(QMainWindow):
    def __init__(self, parent_form, id_variety=None):
        super().__init__()
        uic.loadUi('addEditCoffeeForm.ui', self)
        self.setFixedSize(self.size())
        self.parent_form = parent_form
        self.id_variety = id_variety

        self.priceInput.setMinimum(1)
        self.priceInput.setMaximum(MAX_VALUE)
        self.volumeInput.setMinimum(1)
        self.volumeInput.setMaximum(MAX_VALUE)

        roastin_types = parent_form.cur.execute("""
            SELECT roastin
            FROM roastin_type
        """).fetchall()
        roastin_types = [record[0] for record in roastin_types]
        self.roastinInput.addItems(sorted(roastin_types))

        forms = parent_form.cur.execute("""
            SELECT form
            FROM form
        """).fetchall()
        forms = [record[0] for record in forms]
        self.formInput.addItems(sorted(forms))

        if id_variety:
            variety = parent_form.cur.execute("""
                SELECT name, roastin_type.roastin, form.form, taste, price, volume
                FROM (
                    varieties INNER JOIN roastin_type
                    ON varieties.roastin = roastin_type.id
                ) INNER JOIN form
                ON varieties.form = form.id
                WHERE varieties.id = ?
            """, (id_variety,)).fetchone()
            self.nameInput.setText(variety[0])
            self.roastinInput.setCurrentText(variety[1])
            self.formInput.setCurrentText(variety[2])
            self.tasteInput.setText(variety[3])
            self.priceInput.setValue(variety[4])
            self.volumeInput.setValue(variety[5])

        self.saveButton.clicked.connect(self.save_record)

    def save_record(self):
        name = self.nameInput.text()
        roastin = self.roastinInput.currentText()
        form = self.formInput.currentText()
        taste = self.tasteInput.text()
        price = self.priceInput.text()
        volume = self.volumeInput.text()
        if name == '':
            self.message('Имя не может быть пустым!')
            return
        if taste == '':
            self.message('Описание вкуса не может быть пустым!')
            return
        if self.id_variety:
            self.parent_form.cur.execute("""
                UPDATE varieties
                SET name = ?,
                roastin = (
                    SELECT id
                    FROM roastin_type
                    WHERE roastin = ?
                ),
                form = (
                    SELECT id
                    FROM form
                    WHERE form = ?
                ),
                taste = ?,
                price = ?,
                volume = ?
                WHERE id = ?
            """, (name, roastin, form, taste, price, volume, self.id_variety))
            self.parent_form.con.commit()
        else:
            self.parent_form.cur.execute("""
                INSERT INTO varieties(name, roastin, form, taste, price, volume)
                VALUES(
                    ?,
                    (
                    SELECT id
                    FROM roastin_type
                    WHERE roastin = ?
                    ),
                    (
                    SELECT id
                    FROM form
                    WHERE form = ?
                    ),
                    ?, ?, ?
                )
            """, (name, roastin, form, taste, price, volume))
            self.parent_form.con.commit()
        self.parent_form.load_varieties()
        self.close()

    def message(self, text):
        self.statusbar.showMessage(text)


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        self.setFixedSize(self.size())

        self.con = sqlite3.connect('coffee.db')
        self.cur = self.con.cursor()

        self.load_varieties()

        self.changeButton.clicked.connect(self.change_record)
        self.addButton.clicked.connect(self.add_record)

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

    def change_record(self):
        if len(self.tableWidget.selectedItems()) == 0:
            self.message('Нет выбранной записи')
            return
        row = [obj.row() for obj in self.tableWidget.selectedItems()][0]
        id_variety = self.tableWidget.item(row, 0).text()
        self.addEditCoffeeForm = AddEditCoffeeForm(self, id_variety)
        self.addEditCoffeeForm.show()

    def add_record(self):
        self.addEditCoffeeForm = AddEditCoffeeForm(self)
        self.addEditCoffeeForm.show()

    def closeEvent(self, event):
        self.con.close()

    def message(self, text):
        self.statusbar.showMessage(text)


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
