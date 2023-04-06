import sys
import random
import sqlite3
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.uic import loadUi

class FlashcardsAnki(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi('flashcards.ui', self)
        self.setFixedSize(790, 530)

        self.conexao = sqlite3.connect('flashcards.db')
        self.cursor = self.conexao.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS flashcards (id INTEGER PRIMARY KEY, pergunta TEXT, resposta TEXT)''')


        self.contagem_perguntas()
        self.proxima_pergunta()

        self.add_button.clicked.connect(self.adicionar_pergunta)
        self.flip_button.clicked.connect(self.mostrar_resposta)
        self.next_button.clicked.connect(self.proxima_pergunta)
        self.delete_button.clicked.connect(self.excluir_dados)

        self.question_label.setWordWrap(True)
        self.answer_label.setWordWrap(True)

    def contagem_perguntas(self):
        self.cursor.execute('SELECT COUNT(*) FROM flashcards')
        count = self.cursor.fetchone()[0]
        self.count_label.setText(f'Perguntas cadastradas: {count}')

    def adicionar_pergunta(self):
        pergunta = self.question_input.text().strip()
        resposta = self.answer_input.text().strip()

        if pergunta and resposta:
            self.cursor.execute('INSERT INTO flashcards (pergunta, resposta) VALUES (?, ?)', (pergunta, resposta))
            self.conexao.commit()
            self.contagem_perguntas()
            self.question_input.clear()
            self.answer_input.clear()
            QMessageBox.information(self, 'Sucesso', 'Pergunta adicionada com sucesso.')
        else:
            QMessageBox.warning(self, 'Aviso', 'Por favor, preencha a pergunta e a resposta.')

    def mostrar_resposta(self):
        if self.answer_label.isHidden():
            self.answer_label.show()
            self.flip_button.setText('Esconder Resposta')
        else:
            self.answer_label.hide()
            self.flip_button.setText('Mostrar Resposta')

    def proxima_pergunta(self):
        self.cursor.execute('SELECT COUNT(*) FROM flashcards')
        count = self.cursor.fetchone()[0]

        if count == 0:
            QMessageBox.warning(self, 'Atenção', 'Não há perguntas cadastradas.')
            return

        self.cursor.execute('SELECT id FROM flashcards')
        ids = [row[0] for row in self.cursor.fetchall()]
        random_id = random.choice(ids)

        self.cursor.execute('SELECT * FROM flashcards WHERE id=?', (random_id,))
        flashcard = self.cursor.fetchone()

        pergunta, resposta = flashcard[1], flashcard[2]

        self.question_label.setText(pergunta)
        self.answer_label.setText(resposta)
        self.answer_label.hide()
        self.flip_button.setText('Mostrar Resposta')

    def excluir_dados(self):
        pergunta_atual = self.question_label.text()

        if pergunta_atual == 'Pergunta':
            QMessageBox.warning(self, 'Aviso', 'Não há pergunta selecionada para excluir.')
        else:
            self.cursor.execute('SELECT COUNT(*) FROM flashcards')
            count = self.cursor.fetchone()[0]

            if count > 0:
                self.cursor.execute('SELECT id FROM flashcards WHERE pergunta=?', (pergunta_atual,))
                id_atual = self.cursor.fetchone()[0]
                self.cursor.execute('DELETE FROM flashcards WHERE id=?', (id_atual,))
                self.conexao.commit()
                self.contagem_perguntas()
                QMessageBox.information(self, 'Sucesso', 'Pergunta excluída com sucesso.')
                self.proxima_pergunta()
            else:
                QMessageBox.warning(self, 'Aviso', 'Não há perguntas cadastradas.')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    janela = FlashcardsAnki()
    janela.show()
    #janela.setMaximumSize(790,530)
    sys.exit(app.exec_())

