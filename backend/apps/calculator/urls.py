"""Calculator app URL routing."""

from django.urls import path
from . import views

app_name = "calculator"

urlpatterns = [
    # Evaluation
    path("evaluate/", views.EvaluateView.as_view(), name="evaluate"),
    path("simplify/", views.SimplifyView.as_view(), name="simplify"),
    path("factor/", views.FactorView.as_view(), name="factor"),
    path("expand/", views.ExpandView.as_view(), name="expand"),

    # Equation solving
    path("solve/", views.SolveEquationView.as_view(), name="solve-equation"),
    path("solve-system/", views.SolveSystemView.as_view(), name="solve-system"),

    # Calculus
    path("derivative/", views.DerivativeView.as_view(), name="derivative"),
    path("integrate/", views.IntegralView.as_view(), name="integrate"),

    # Graphing
    path("plot/", views.PlotFunctionView.as_view(), name="plot-function"),
    path("plot-implicit/", views.PlotImplicitView.as_view(), name="plot-implicit"),

    # Custom functions
    path("functions/", views.CustomFunctionListView.as_view(), name="function-list"),
    path("functions/<uuid:pk>/", views.CustomFunctionDetailView.as_view(), name="function-detail"),
    path("functions/<uuid:pk>/evaluate/", views.EvaluateCustomFunctionView.as_view(), name="function-evaluate"),

    # History
    path("history/", views.CalculationHistoryView.as_view(), name="history"),
]