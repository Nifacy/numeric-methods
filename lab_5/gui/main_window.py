from typing import Callable
import numpy as np
from PyQt5.QtWidgets import (QHBoxLayout, QWidget)

from common.typing import Matrix
import domain
from gui.input_form import InputForm
from gui.plot_area import PlotArea


def calculate_mean_error(grid: domain.Grid, U: Callable[[float, float], float], U2: Matrix) -> float:
    error_rate = 0.0
    point_amount = grid.M * grid.N
    h, tau = domain._get_steps(grid)

    for k in range(grid.M):
        for i in range(grid.N):
            error_rate += abs(U(i * h, k * tau) - U2[k][i])

    return error_rate / point_amount


class MainWindow(QWidget):
    SOLVE_METHODS = {
        (0, 0): domain.explicit_finite_difference_1,
        (0, 1): domain.implicit_finite_difference_1,
        (0, 2): domain.crank_nicolson_1,
        (1, 0, 0): domain.explicit_finite_difference_2,
        (1, 1, 0): domain.implicit_finite_difference_2,
        (1, 2, 0): domain.crank_nicolson_2,
        (1, 0, 1): domain.explicit_finite_difference_3,
        (1, 1, 1): domain.implicit_finite_difference_3,
        (1, 2, 1): domain.crank_nicolson_3,
        (1, 0, 2): domain.explicit_finite_difference_4,
        (1, 1, 2): domain.implicit_finite_difference_4,
        (1, 2, 2): domain.crank_nicolson_4,
        (2, 0, 0): domain.explicit_finite_difference_2,
        (2, 1, 0): domain.implicit_finite_difference_2,
        (2, 2, 0): domain.crank_nicolson_2,
        (2, 0, 1): domain.explicit_finite_difference_3,
        (2, 1, 1): domain.implicit_finite_difference_3,
        (2, 2, 1): domain.crank_nicolson_3,
        (2, 0, 2): domain.explicit_finite_difference_4,
        (2, 1, 2): domain.implicit_finite_difference_4,
        (2, 2, 2): domain.crank_nicolson_4,
    }

    def foo(self, data):
        grid = domain.Grid(
            L=data["L"],
            T=data["T"],
            N=data["N"],
            M=data["M"],
        )

        expr_coefs = domain.ExprCoefs(
            a=data["a"],
            b=data["b"],
            g=data["g"],
            f=data["f"],
        )

        start_conditions = domain.StartConditions(
            psi=data["psi"],
            phi_0=data["phi0"],
            phi_l=data["phil"],
        )

        T = ((data["alpha"], data["beta"]), (data["gamma"], data["delta"]))

        task_type = data["task_type"]

        if task_type == 0:
            solve_method_index = (data["task_type"], data["solve_method"])
            solve_method = self.SOLVE_METHODS[solve_method_index]
            solve = lambda grid: solve_method(
                coefs=expr_coefs,
                conditions=start_conditions,
                grid=grid,
            )

        elif task_type == 1:
            solve_method_index = (
                data["task_type"],
                data["solve_method"],
                data["approx"],
            )
            solve_method = self.SOLVE_METHODS[solve_method_index]

            solve = lambda grid: solve_method(
                coefs=expr_coefs,
                conditions=start_conditions,
                grid=grid,
                T=((1.0, 0.0), (1.0, 0.0)),
            )

        else:
            solve_method_index = (
                data["task_type"],
                data["solve_method"],
                data["approx"],
            )
            solve_method = self.SOLVE_METHODS[solve_method_index]
            solve = lambda grid: solve_method(
                coefs=expr_coefs,
                conditions=start_conditions,
                grid=grid,
                T=T,
            )

        grids_x = [
            domain.Grid(L=data["L"], T=data["T"], N=data["N"] * k, M=data["M"])
            for k in range(1, 4)
        ]

        grids_y = [
            domain.Grid(L=data["L"], T=data["T"], N=data["N"], M=data["M"] * k)
            for k in range(1, 4)
        ]

        self.plot_area.update_graphs(
            grid=grid,
            U=data["etalone"],
            U2=solve(grid),
            Ux=[solve(g) for g in grids_x],
            Ut=[solve(g) for g in grids_y],
        )

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Графическая программа")

        # Основной горизонтальный layout
        layout = QHBoxLayout()

        # Форма ввода и область графиков
        self.plot_area = PlotArea()
        self.input_form = InputForm(on_enter_clicked=self.foo)

        # Добавление формы ввода и области графиков в основной layout
        layout.addWidget(self.input_form)
        layout.addWidget(self.plot_area)

        self.setLayout(layout)
