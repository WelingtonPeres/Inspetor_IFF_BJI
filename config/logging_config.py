"""
logging_config.py
-----------------
Configuração central de logging do projeto.

USO:
  - Chame `setup_logging()` UMA VEZ no entry-point (main.py / app.py)
  - Em todos os outros módulos, use apenas:
        import logging
        logger = logging.getLogger(__name__)

AMBIENTES:
  APP_ENV=development  → DEBUG  (console colorido + arquivos)
  APP_ENV=staging      → INFO   (console + arquivos)
  APP_ENV=production   → WARNING (só console/stdout)
  LOG_LEVEL=<NIVEL>    → sobrescreve qualquer ambiente manualmente
"""

import logging
import logging.config
import os
from pathlib import Path

# ── Ambiente e nível ───────────────────────────────────────────────────────────
ENV = os.getenv("APP_ENV", "development")

_LEVEL_BY_ENV: dict[str, str] = {
    "development": "DEBUG",
    "staging":     "INFO",
    "production":  "WARNING",
}

LOG_LEVEL = (os.getenv("LOG_LEVEL") or _LEVEL_BY_ENV.get(ENV, "WARNING")).upper()

# ── Diretório de logs (criado automaticamente) ────────────────────────────────
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# ── Formato: sem timestamp, com módulo/função/linha ─────────────────────────
#    %(levelname)-8s  → nível alinhado em 8 chars  (ex: "INFO    ")
#    %(name)s         → caminho do módulo           (ex: "services.payment")
#    %(funcName)s     → nome da função              (ex: "process")
#    %(lineno)d       → número da linha             (ex: 42)
#    %(message)s      → mensagem do log
LOG_FORMAT = "%(levelname)-8s | %(name)s.%(funcName)s():%(lineno)d | %(message)s"

# ── Handlers ativos por ambiente ──────────────────────────────────────────────
_HANDLERS_BY_ENV: dict[str, list[str]] = {
    "development": ["console", "file_app", "file_errors"],
    "staging":     ["console", "file_app", "file_errors"],
    "production":  ["console"],   # stdout → coletor externo (CloudWatch, Datadog…)
}

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,

    # ── Formatters ────────────────────────────────────────────────────────────
    "formatters": {
        "console": {
            "()": "config.logging_config.ColorFormatter",
            "fmt": LOG_FORMAT,
        },
        "file": {
            "format": LOG_FORMAT,
        },
    },

    # ── Handlers ──────────────────────────────────────────────────────────────
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "console",
            "level": "DEBUG",
            "stream": "ext://sys.stdout",
        },
        "file_app": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(LOG_DIR / "app.log"),
            "maxBytes": 10 * 1024 * 1024,   # 10 MB
            "backupCount": 5,
            "formatter": "file",
            "level": "INFO",
            "encoding": "utf-8",
        },
        "file_errors": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(LOG_DIR / "errors.log"),
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
            "formatter": "file",
            "level": "ERROR",
            "encoding": "utf-8",
        },
    },

    # ── Root logger ───────────────────────────────────────────────────────────
    "root": {
        "level": LOG_LEVEL,
        "handlers": _HANDLERS_BY_ENV.get(ENV, ["console"]),
    },

    # ── Silenciar libs verbosas ───────────────────────────────────────────────
    "loggers": {
        "urllib3":   {"level": "WARNING"},
        "httpx":     {"level": "WARNING"},
        "asyncio":   {"level": "WARNING"},
        "sqlalchemy":{"level": "WARNING"},
    },
}


# ── Color Formatter ───────────────────────────────────────────────────────────
class ColorFormatter(logging.Formatter):
    """Colore o nível da mensagem no terminal. Sem efeito em arquivos."""

    _GREY     = "\033[38;5;245m"
    _CYAN     = "\033[36m"
    _YELLOW   = "\033[33m"
    _RED      = "\033[31m"
    _BOLD_RED = "\033[1;31m"
    _RESET    = "\033[0m"

    _COLORS: dict[int, str] = {
        logging.DEBUG:    _GREY,
        logging.INFO:     _CYAN,
        logging.WARNING:  _YELLOW,
        logging.ERROR:    _RED,
        logging.CRITICAL: _BOLD_RED,
    }

    def __init__(self, fmt: str) -> None:
        super().__init__()
        self._fmt = fmt

    def format(self, record: logging.LogRecord) -> str:
        color = self._COLORS.get(record.levelno, self._RESET)
        colored_fmt = self._fmt.replace(
            "%(levelname)-8s",
            f"{color}%(levelname)-8s{self._RESET}",
        )
        return logging.Formatter(colored_fmt).format(record)


# ── Ponto de entrada público ──────────────────────────────────────────────────
def setup_logging() -> None:
    """
    Inicializa o sistema de logging.
    Chame uma única vez no entry-point antes de qualquer outro import.
    """
    logging.config.dictConfig(LOGGING_CONFIG)
    logging.getLogger(__name__).info(
        "Logging inicializado | env=%s | nível=%s", ENV, LOG_LEVEL
    )