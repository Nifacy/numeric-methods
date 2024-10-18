import numpy as np
from PyQt5.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

import common.tools as tools


class InputForm(QWidget):
    TASK_TYPE_VALUES = ("первая", "вторая", "третья")
    METHOD_VALUES = ("явная схема", "неявная схема", "схема Кранка-Николсона")
    APPROX_VALUES = (
        "двуточечная (1 порядок)",
        "трехточечная (2 порядок)",
        "двуточечная (2 порядок)",
    )

    def __init__(self, on_enter_clicked, parent=None):
        super().__init__(parent)

        self.on_enter_clicked = on_enter_clicked

        layout = QVBoxLayout()

        self.header = QLabel("Ввод")
        self.header.setStyleSheet("font-size: 16px; font-weight: bold;")

        # Поле "Тип начально-краевой задачи"
        self.label_task_type = QLabel("Тип начально-краевой задачи:")
        self.task_type_input = QComboBox()
        self.task_type_input.addItems(self.TASK_TYPE_VALUES)
        self.task_type_input.currentIndexChanged.connect(self.update_form)

        # Метод решения
        self.solve_method = QLabel("Метод:")
        self.solve_method_input = QComboBox()
        self.solve_method_input.addItems(self.METHOD_VALUES)
        self.solve_method_input.currentIndexChanged.connect(self.update_form)

        # Поле "Аппроксимация"
        self.label_approx = QLabel("Аппроксимация:")
        self.approx_input = QComboBox()
        self.approx_input.addItems(self.APPROX_VALUES)
        self.label_approx.setVisible(False)
        self.approx_input.setVisible(False)

        # эталонная функция
        self.label_etalone = QLabel("U(x, t):")
        self.etalone_input = QLineEdit()

        # Поля для коэффициентов a, b, g
        self.label_a = QLabel("Коэффициент a:")
        self.a_input = QDoubleSpinBox()
        self.label_b = QLabel("Коэффициент b:")
        self.b_input = QDoubleSpinBox()
        self.label_g = QLabel("Коэффициент g:")
        self.g_input = QDoubleSpinBox()

        # Текстовое поле для функции f
        self.label_f = QLabel("Функция f:")
        self.f_input = QLineEdit()

        # Поля для функций phi_0, phi_l, psi
        self.label_psi = QLabel("\u03A8:")
        self.psi_input = QLineEdit()

        self.label_phi0 = QLabel("\u03C6\u2080:")
        self.phi0_input = QLineEdit()
        self.label_phil = QLabel("\u03C6\u2093:")
        self.phil_input = QLineEdit()

        # Поля для коэффициентов L, T
        self.label_L = QLabel("Коэффициент L:")
        self.L_input = QDoubleSpinBox()
        self.L_input.setMinimum(0)
        self.L_input.setValue(np.pi / 2.0)
        self.label_T = QLabel("Коэффициент T:")
        self.T_input = QDoubleSpinBox()
        self.T_input.setMinimum(0)

        # Поля для коэффициентов M, N
        self.label_M = QLabel("Коэффициент M:")
        self.M_input = QSpinBox()
        self.M_input.setMaximum(10_000)
        self.M_input.setMinimum(2)
        self.label_N = QLabel("Коэффициент N:")
        self.N_input = QSpinBox()
        self.N_input.setMaximum(10_000)
        self.N_input.setMinimum(2)

        # Поля для коэффициентов α, β, γ, δ (по умолчанию скрыты)
        self.label_alpha = QLabel("\u03B1:")
        self.alpha_input = QDoubleSpinBox()
        self.label_beta = QLabel("\u03B2:")
        self.beta_input = QDoubleSpinBox()
        self.label_gamma = QLabel("\u03B3:")
        self.gamma_input = QDoubleSpinBox()
        self.label_delta = QLabel("\u03B4:")
        self.delta_input = QDoubleSpinBox()

        # Изначально скрываем поля для третьей задачи
        self.label_alpha.setVisible(False)
        self.alpha_input.setVisible(False)
        self.label_beta.setVisible(False)
        self.beta_input.setVisible(False)
        self.label_gamma.setVisible(False)
        self.gamma_input.setVisible(False)
        self.label_delta.setVisible(False)
        self.delta_input.setVisible(False)

        # Кнопка Enter
        self.enter_button = QPushButton("Enter")
        self.enter_button.clicked.connect(
            lambda: self.on_enter_clicked(self.get_user_data())
        )

        # Сетка для размещения всех элементов
        grid_elements = [
            (self.label_task_type, self.task_type_input),
            (self.solve_method, self.solve_method_input),
            (self.label_approx, self.approx_input),
            (self.label_etalone, self.etalone_input),
            (self.label_a, self.a_input),
            (self.label_b, self.b_input),
            (self.label_g, self.g_input),
            (self.label_f, self.f_input),
            (self.label_phi0, self.phi0_input),
            (self.label_phil, self.phil_input),
            (self.label_psi, self.psi_input),
            (self.label_L, self.L_input),
            (self.label_T, self.T_input),
            (self.label_M, self.M_input),
            (self.label_N, self.N_input),
            (self.label_alpha, self.alpha_input),
            (self.label_beta, self.beta_input),
            (self.label_gamma, self.gamma_input),
            (self.label_delta, self.delta_input),
        ]

        grid_layout = QGridLayout()

        for index, (label, input_widget) in enumerate(grid_elements):
            grid_layout.addWidget(label, index, 0)
            grid_layout.addWidget(input_widget, index, 1)

        # Добавление заголовка, сетки и кнопки
        layout.addWidget(self.header)
        layout.addLayout(grid_layout)
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        layout.addWidget(self.enter_button)

        self.setLayout(layout)

    def update_form(self):
        # Обновление видимости полей в зависимости от выбранной задачи
        task_type = self.task_type_input.currentText()

        match task_type:
            case "первая":
                self.label_approx.setVisible(False)
                self.approx_input.setVisible(False)
                self.show_abc_fields(False)
            case "вторая":
                self.label_approx.setVisible(True)
                self.approx_input.setVisible(True)
                self.show_abc_fields(False)
            case "третья":
                self.label_approx.setVisible(True)
                self.approx_input.setVisible(True)
                self.show_abc_fields(True)

    def show_abc_fields(self, visible):
        # Показывать или скрывать поля для α, β, γ, δ
        self.label_alpha.setVisible(visible)
        self.alpha_input.setVisible(visible)
        self.label_beta.setVisible(visible)
        self.beta_input.setVisible(visible)
        self.label_gamma.setVisible(visible)
        self.gamma_input.setVisible(visible)
        self.label_delta.setVisible(visible)
        self.delta_input.setVisible(visible)

    def get_user_data(self):
        return {
            "task_type": self.TASK_TYPE_VALUES.index(
                self.task_type_input.currentText()
            ),
            "solve_method": self.METHOD_VALUES.index(
                self.solve_method_input.currentText()
            ),
            "approx": self.APPROX_VALUES.index(self.approx_input.currentText()),
            "a": self.a_input.value(),
            "b": self.b_input.value(),
            "g": self.g_input.value(),
            "f": tools.function_from_expr(self.f_input.text() or "0", "x t"),
            "phi0": tools.function_from_expr(self.phi0_input.text() or "0", "t"),
            "phil": tools.function_from_expr(self.phil_input.text() or "0", "t"),
            "L": self.L_input.value(),
            "T": self.T_input.value(),
            "M": self.M_input.value(),
            "N": self.N_input.value(),
            "alpha": self.alpha_input.value(),
            "beta": self.beta_input.value(),
            "gamma": self.gamma_input.value(),
            "delta": self.delta_input.value(),
            "psi": tools.function_from_expr(self.psi_input.text() or "0", "x"),
            "etalone": tools.function_from_expr(
                self.etalone_input.text() or "0", "x t"
            ),
        }
