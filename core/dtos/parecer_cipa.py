from dataclasses import dataclass


@dataclass(frozen=True)
class ParecerCIPA:
    """
    Parecer técnico emitido pela CIPA sobre a conduta do inspetor.

    Value Object imutável que representa um parecer completo: número de
    referência, categoria temática e corpo do texto. É construído pelo
    RepositorioDePareceresCIPA e consumido pela view.
    """

    numero: str
    referencia: str
    texto: str

    def __post_init__(self) -> None:
        if not self.texto or not self.texto.strip():
            raise ValueError("[Erro - ParecerCIPA] Texto do parecer nao pode ser vazio.")
        if not self.numero or "/" not in self.numero:
            raise ValueError(
                f"[Erro - ParecerCIPA] Numero '{self.numero}' invalido; esperado formato 'NNN/AAAA'."
            )
        partes = self.numero.split("/")
        if (
            len(partes) != 2
            or len(partes[0]) != 3
            or not partes[0].isdigit()
            or len(partes[1]) != 4
            or not partes[1].isdigit()
        ):
            raise ValueError(
                f"[Erro - ParecerCIPA] Numero '{self.numero}' invalido; esperado formato 'NNN/AAAA'."
            )
        if not self.referencia or not self.referencia.strip():
            raise ValueError("[Erro - ParecerCIPA] Referencia do parecer nao pode ser vazia.")
