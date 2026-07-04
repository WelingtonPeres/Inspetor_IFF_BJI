from pathlib import Path

DIRETORIO_BASE: str = str(Path(__file__).resolve().parent.parent / "resources" / "data")

QUANTIDADE_GERACAO: int = 5

CURSOS: list[str] = [
    "DEFAULT",
    "T_QUIMICA",
    "T_INFORMATICA",
    "T_AGROPECUARIA",
    "T_ALIMENTOS",
    "T_MEIO_AMBIENTE",
    "T_ZOOTECNIA",
    "CT_ALIMENTOS",
    "E_COMPUTACAO",
]

TEMA_PADRAO: str = "dark"  # "dark" ou "light"
