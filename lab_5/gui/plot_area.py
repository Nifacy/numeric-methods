from PyQt5.QtWidgets import (QTabWidget, QVBoxLayout, QWidget)

import domain
from gui.tab_widgets.compare_error_tab import CompareErrorRateTab
from gui.tab_widgets.error_rate_tab import ErrorRateTab
from gui.tab_widgets.solution_tab import SolutionTab


class PlotArea(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout()
        self.tabs = QTabWidget()

        self.tab1 = SolutionTab()
        self.tabs.addTab(self.tab1, "Решение")

        self.tab2 = ErrorRateTab()
        self.tabs.addTab(self.tab2, "Ошибка")

        self.tab3 = CompareErrorRateTab()
        self.tabs.addTab(self.tab3, "Сравнение ошибок")

        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def update_graphs(self, grid: domain.Grid, U, U2, Ux, Ut):
        self.tab1.update_content(grid, U, U2)
        self.tab2.update_content(grid, U, U2)
        self.tab3.update_content(grid, U, Ux, Ut)
