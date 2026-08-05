"""
Testes do DTO ParecerCIPA.

Cobre a validacao de invariantes do value object imutavel.
"""

import pytest
from dataclasses import FrozenInstanceError

from core.dtos.parecer_cipa import ParecerCIPA


class TestConstrutor:
    """Testes de instanciacao e validacao em __post_init__."""

    def test_construtor_aceita_valores_validos(self):
        """
        DTO aceita numero no formato NNN/AAAA, texto e referencia nao vazios.
        """
        # Arrange & Act
        parecer = ParecerCIPA(
            numero="847/2026",
            referencia="Conduta do Inspetor",
            texto="Texto de exemplo com mais de 10 caracteres.",
        )

        # Assert
        assert parecer.numero == "847/2026"
        assert parecer.referencia == "Conduta do Inspetor"
        assert parecer.texto == "Texto de exemplo com mais de 10 caracteres."

    def test_numero_com_formato_incorreto_levanta_erro(self):
        """
        Numero fora do formato NNN/AAAA levanta ValueError com tag.
        """
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="\\[Erro - ParecerCIPA\\]"):
            ParecerCIPA(
                numero="ABC/2024",
                referencia="X",
                texto="algum texto aqui",
            )

    def test_numero_ano_com_5_digitos_levanta_erro(self):
        """
        Numero com ano de 5 digitos e levantado como invalido.
        """
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="\\[Erro - ParecerCIPA\\]"):
            ParecerCIPA(
                numero="123/20240",
                referencia="X",
                texto="algum texto aqui",
            )

    def test_numero_ano_nao_numerico_levanta_erro(self):
        """
        Numero com ano nao numerico e levantado como invalido.
        """
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="\\[Erro - ParecerCIPA\\]"):
            ParecerCIPA(
                numero="123/20AB",
                referencia="X",
                texto="algum texto aqui",
            )

    def test_numero_parte_inicial_com_2_digitos_levanta_erro(self):
        """
        Numero com 2 digitos antes da barra e levantado como invalido.
        """
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="\\[Erro - ParecerCIPA\\]"):
            ParecerCIPA(
                numero="12/2026",
                referencia="X",
                texto="algum texto aqui",
            )

    def test_numero_sem_barra_levanta_erro(self):
        """
        Numero sem separador '/' e levantado como invalido.
        """
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="\\[Erro - ParecerCIPA\\]"):
            ParecerCIPA(
                numero="123-2026",
                referencia="X",
                texto="algum texto aqui",
            )

    def test_texto_vazio_levanta_erro(self):
        """Texto vazio ou em branco e rejeitado."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="\\[Erro - ParecerCIPA\\]"):
            ParecerCIPA(
                numero="123/2026",
                referencia="X",
                texto="",
            )

    def test_texto_apenas_espacos_levanta_erro(self):
        """Texto com apenas espacos em branco e rejeitado."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="\\[Erro - ParecerCIPA\\]"):
            ParecerCIPA(
                numero="123/2026",
                referencia="X",
                texto="     ",
            )

    def test_referencia_vazia_levanta_erro(self):
        """Referencia vazia e rejeitada por consistencia."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="\\[Erro - ParecerCIPA\\]"):
            ParecerCIPA(
                numero="123/2026",
                referencia="",
                texto="algum texto",
            )

    def test_referencia_apenas_espacos_levanta_erro(self):
        """Referencia contendo apenas espacos e rejeitada."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="\\[Erro - ParecerCIPA\\]"):
            ParecerCIPA(
                numero="123/2026",
                referencia="   ",
                texto="algum texto",
            )


class TestImutabilidade:
    """DTO e frozen: atributos nao podem ser reatribuidos."""

    def test_atribuir_a_numero_levanta_frozen_error(self):
        """
        Tentar reatribuir .numero levanta FrozenInstanceError.
        """
        # Arrange
        parecer = ParecerCIPA(
            numero="100/2026",
            referencia="X",
            texto="texto qualquer",
        )

        # Act & Assert
        with pytest.raises(FrozenInstanceError):
            parecer.numero = "200/2026"  # type: ignore[misc]

    def test_atribuir_a_texto_levanta_frozen_error(self):
        """
        Tentar reatribuir .texto levanta FrozenInstanceError.
        """
        # Arrange
        parecer = ParecerCIPA(
            numero="100/2026",
            referencia="X",
            texto="texto original",
        )

        # Act & Assert
        with pytest.raises(FrozenInstanceError):
            parecer.texto = "novo texto"  # type: ignore[misc]

    def test_atribuir_a_referencia_levanta_frozen_error(self):
        """
        Tentar reatribuir .referencia levanta FrozenInstanceError.
        """
        # Arrange
        parecer = ParecerCIPA(
            numero="100/2026",
            referencia="original",
            texto="texto qualquer",
        )

        # Act & Assert
        with pytest.raises(FrozenInstanceError):
            parecer.referencia = "nova"  # type: ignore[misc]


class TestEquality:
    """DTOs com mesmos valores sao iguais (frozen + dataclass)."""

    def test_dois_pareceres_iguais_sao_iguais(self):
        """Dois DTOs com mesmos valores tem igualdade por valor."""
        # Arrange & Act
        a = ParecerCIPA(numero="100/2026", referencia="R", texto="texto qualquer")
        b = ParecerCIPA(numero="100/2026", referencia="R", texto="texto qualquer")

        # Assert
        assert a == b

    def test_pareceres_com_texto_diferente_sao_diferentes(self):
        """Textos diferentes tornam os DTOs diferentes."""
        # Arrange & Act
        a = ParecerCIPA(numero="100/2026", referencia="R", texto="texto A")
        b = ParecerCIPA(numero="100/2026", referencia="R", texto="texto B")

        # Assert
        assert a != b

    def test_pareceres_com_numero_diferente_sao_diferentes(self):
        """Numeros diferentes tornam os DTOs diferentes."""
        # Arrange & Act
        a = ParecerCIPA(numero="111/2026", referencia="R", texto="texto comum")
        b = ParecerCIPA(numero="222/2026", referencia="R", texto="texto comum")

        # Assert
        assert a != b

    def test_pareceres_com_referencia_diferente_sao_diferentes(self):
        """Referencias diferentes tornam os DTOs diferentes."""
        # Arrange & Act
        a = ParecerCIPA(numero="100/2026", referencia="R1", texto="texto comum")
        b = ParecerCIPA(numero="100/2026", referencia="R2", texto="texto comum")

        # Assert
        assert a != b
