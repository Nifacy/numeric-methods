import sys
from PyQt5.QtWidgets import QApplication
import numpy as np
from gui.main_window import MainWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()

    # устанавливаем значения, соответствующие варианту 6
    window.input_form.task_type_input.setCurrentIndex(2)
    window.input_form.alpha_input.setValue(0.0)
    window.input_form.beta_input.setValue(1.0)
    window.input_form.gamma_input.setValue(1.0)
    window.input_form.delta_input.setValue(0.0)
    window.input_form.solve_method_input.setCurrentIndex(1)
    window.input_form.f_input.setText("cos(x) * (cos(t) + sin(t))")
    window.input_form.etalone_input.setText("sin(t) * cos(x)")
    window.input_form.N_input.setValue(14)
    window.input_form.M_input.setValue(500)
    window.input_form.T_input.setValue(np.pi)
    window.input_form.a_input.setValue(1.0)
    window.input_form.psi_input.setText("0")
    window.input_form.phi0_input.setText("sin(t)")
    window.input_form.phil_input.setText("-sin(t)")

    # отображаем графики
    window.input_form.enter_button.click()

    window.show()
    sys.exit(app.exec_())
