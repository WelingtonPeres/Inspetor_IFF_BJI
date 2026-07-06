import logging
from dataclasses import dataclass
from typing import List, Optional

from PySide6.QtCore import (
    Qt, QPropertyAnimation, Property, Signal,
    QEasingCurve, QRectF,
)
from PySide6.QtWidgets import (
    QWidget, QPushButton, QSizePolicy,
)
from PySide6.QtGui import (
    QPainter, QPainterPath, QLinearGradient,
    QColor, QPen, QFont, QBrush, QFontMetrics,
    QPaintEvent, QResizeEvent, QKeyEvent,
)

from view.expediente.modelos.character_data import CharacterData

logger = logging.getLogger(__name__)


@dataclass
class CardRenderData:
    """Dados de renderizacao de uma carta no carousel."""
    rect: QRectF
    scale: float
    opacity: float
    character: CharacterData
    is_centre: bool
    depth: float
    offset_px: float
    z_order: float


CARD_WIDTH      = 180
CARD_HEIGHT     = 340
SLOT_SPACING    = 250
ANIM_DURATION   = 350
BUMP_DURATION   = 200

SCALE_AT_CENTRE  = 1.0
SCALE_AT_SLOT    = 0.72
SCALE_MIN        = 0.45
OPACITY_AT_CENTRE = 1.0
OPACITY_AT_SLOT   = 0.5
OPACITY_MIN       = 0.2

CARD_BG        = QColor("#12121e")
ACCENT_COLOR   = QColor("#2F9E41")
ACCENT_GLOW    = QColor(47, 158, 65, 45)
TEXT_WHITE     = QColor("#ffffff")
TEXT_MUTED     = QColor("#7777aa")

NAV_BTN_SIZE   = 52
NAV_BTN_MARGIN = 16

NAME_BAR_RATIO = 0.17


class CharacterCarousel(QWidget):
    """Carousel animado de cartas de perfil com navegacao horizontal.

    Renderiza as cartas com escala, opacidade e perspectiva 3D
    interpoladas pela distancia ao centro. Suporta navegacao por
    botoes laterais e teclas de seta.

    Signals
    -------
    index_changed : Signal(int)
        Emitido sempre que o indice do perfil activo muda, apos
        conclusao da animacao de deslize.

    Public API
    ----------
    current_index : int (property)
        Indice do perfil actualmente selecionado.
    current_character() -> CharacterData
        Retorna o CharacterData do perfil actual.
    characters : List[CharacterData] (property)
        Acesso de leitura a lista de personagens.
    slide_previous() -> None
        Inicia animacao de deslize para o perfil anterior.
    slide_next() -> None
        Inicia animacao de deslize para o perfil seguinte.
    """

    index_changed = Signal(int)

    def __init__(
        self,
        characters: List[CharacterData],
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.__characters = characters
        self.__index = 0
        self.__scroll_offset = 0.0
        self.__animation: Optional[QPropertyAnimation] = None

        self.setMinimumHeight(CARD_HEIGHT + 60)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.__btn_prev = QPushButton("\u25C0", self)
        self.__btn_prev.setObjectName("carousel_btn_prev")
        self.__btn_prev.setFixedSize(NAV_BTN_SIZE, NAV_BTN_SIZE)
        self.__btn_prev.setToolTip("Anterior (\u2190)")
        self.__btn_prev.clicked.connect(self.slide_previous)

        self.__btn_next = QPushButton("\u25B6", self)
        self.__btn_next.setObjectName("carousel_btn_next")
        self.__btn_next.setFixedSize(NAV_BTN_SIZE, NAV_BTN_SIZE)
        self.__btn_next.setToolTip("Pr\u00F3ximo (\u2192)")
        self.__btn_next.clicked.connect(self.slide_next)

        self.index_changed.emit(self.__index)

    def _get_offset(self) -> float:
        return self.__scroll_offset

    def _set_offset(self, value: float) -> None:
        self.__scroll_offset = value
        self.update()

    scroll_offset = Property(float, _get_offset, _set_offset)

    @property
    def characters(self) -> List[CharacterData]:
        """Lista de CharacterData disponiveis no carousel."""
        return self.__characters

    @property
    def current_index(self) -> int:
        """Indice do perfil actualmente selecionado."""
        return self.__index

    def current_character(self) -> CharacterData:
        """Retorna o CharacterData do perfil no centro do carousel."""
        return self.__characters[self.__index]

    def slide_previous(self) -> None:
        """Desliza para o perfil anterior ou executa bump no inicio."""
        if self.__index <= 0:
            self.__bump_animation(1.0)
            return
        self.__start_animation(SLOT_SPACING)

    def slide_next(self) -> None:
        """Desliza para o perfil seguinte ou executa bump no fim."""
        if self.__index >= len(self.__characters) - 1:
            self.__bump_animation(-1.0)
            return
        self.__start_animation(-SLOT_SPACING)

    def __bump_animation(self, direction: float) -> None:
        """Animacao elastica de ricochete nos limites do carousel."""
        if self.__animation and self.__animation.state():
            self.__animation.stop()
        self.__animation = QPropertyAnimation(self, b"scroll_offset")
        self.__animation.setDuration(BUMP_DURATION)
        self.__animation.setStartValue(0.0)
        self.__animation.setKeyValueAt(0.4, direction * 15.0)
        self.__animation.setEndValue(0.0)
        self.__animation.setEasingCurve(QEasingCurve.Type.OutElastic)
        self.__animation.start()

    def __start_animation(self, target: float) -> None:
        """Animacao de deslize suave entre perfis."""
        if self.__animation and self.__animation.state():
            self.__animation.stop()
        self.__animation = QPropertyAnimation(self, b"scroll_offset")
        self.__animation.setDuration(ANIM_DURATION)
        self.__animation.setStartValue(0.0)
        self.__animation.setEndValue(target)
        self.__animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.__animation.finished.connect(lambda: self.__ancorar_indice())
        self.__animation.start()

    def __ancorar_indice(self) -> None:
        """Fixa o indice na carta mais proxima apos deslize."""
        if self.__scroll_offset < 0:
            self.__index += 1
        elif self.__scroll_offset > 0:
            self.__index -= 1
        self.__scroll_offset = 0.0
        self.update()
        self.index_changed.emit(self.__index)

    def resizeEvent(self, event: QResizeEvent) -> None:
        """Reposiciona os botoes de navegacao ao redimensionar."""
        cy = self.height() // 2 - NAV_BTN_SIZE // 2
        self.__btn_prev.move(NAV_BTN_MARGIN, cy)
        self.__btn_next.move(
            self.width() - NAV_BTN_SIZE - NAV_BTN_MARGIN, cy
        )
        super().resizeEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Navegacao por teclado: setas laterais."""
        if event.key() == Qt.Key.Key_Left:
            self.slide_previous()
        elif event.key() == Qt.Key.Key_Right:
            self.slide_next()
        else:
            super().keyPressEvent(event)

    def __draw_background(self, p: QPainter) -> None:
        """Fundo escuro com gradiente lateral."""
        w, h = self.width(), self.height()
        p.fillRect(0, 0, w, h, QColor("#0e0e1a"))
        grad = QLinearGradient(w * 0.3, 0, w * 0.7, h)
        grad.setColorAt(0.0, QColor(30, 25, 50, 50))
        grad.setColorAt(0.5, QColor(0, 0, 0, 0))
        grad.setColorAt(1.0, QColor(30, 25, 50, 60))
        p.fillRect(0, 0, w, h, QBrush(grad))

    def paintEvent(self, event: QPaintEvent) -> None:
        """Renderiza todas as cartas visiveis com escala e opacidade."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        self.__draw_background(painter)

        cx = self.width() / 2.0
        cy = self.height() / 2.0

        cards: List[CardRenderData] = []
        for i, ch in enumerate(self.__characters):
            offset_px = (
                (i - self.__index) * SLOT_SPACING + self.__scroll_offset
            )
            dist = abs(offset_px)

            if dist > SLOT_SPACING * 2.3:
                continue

            t = min(1.0, dist / SLOT_SPACING)
            scale = max(
                SCALE_MIN,
                SCALE_AT_CENTRE - t * (SCALE_AT_CENTRE - SCALE_AT_SLOT),
            )
            opacity = max(
                OPACITY_MIN,
                OPACITY_AT_CENTRE
                - t * (OPACITY_AT_CENTRE - OPACITY_AT_SLOT),
            )

            card_w = CARD_WIDTH * scale
            card_h = CARD_HEIGHT * scale
            x = cx + offset_px - card_w / 2.0
            y = cy - card_h / 2.0

            cards.append(CardRenderData(
                rect=QRectF(x, y, card_w, card_h),
                scale=scale,
                opacity=opacity,
                character=ch,
                is_centre=dist < 1.0,
                depth=t,
                offset_px=offset_px,
                z_order=1.0 - t,
            ))

        cards.sort(key=lambda c: c.z_order)

        for card in cards:
            self.__draw_card(painter, card)

        painter.end()

    def __draw_card(self, p: QPainter, card: CardRenderData) -> None:
        """Orquestrador de desenho — chama cada etapa por ordem."""
        r = card.rect
        radius = 12 * card.scale

        self.__aplicar_perspectiva(p, card)
        self.__desenhar_sombra(p, r, radius, card)
        self.__desenhar_glow(p, r, radius, card)
        self.__desenhar_fundo(p, r, radius, card)
        self.__desenhar_vinheta(p, r, card)
        self.__desenhar_retrato(p, r, card)
        self.__desenhar_barra_nome(p, r, card)
        self.__desenhar_badge(p, r, card)
        p.restore()
        self.__desenhar_borda(p, r, radius, card)

    def __aplicar_perspectiva(self, p: QPainter, card: CardRenderData) -> None:
        """Aplica transformacao 3D: translacao, escala e rotacao por profundidade."""
        r = card.rect
        tilt = card.depth * 8.0
        voff = card.depth * 30.0 * card.scale
        squish = 1.0 - card.depth * 0.15
        cx = r.center().x()
        cy = r.center().y()

        p.save()
        p.translate(cx, cy + voff)
        p.scale(squish, 1.0)
        if not card.is_centre:
            rot = tilt if card.offset_px > 0 else -tilt
            p.rotate(rot)
        p.translate(-cx, -cy - voff)

    def __desenhar_sombra(self, p: QPainter, r: QRectF, radius: float,
                          card: CardRenderData) -> None:
        """Sombra distante para cartas com profundidade > 0.1."""
        if card.depth <= 0.1:
            return
        shadow = r.translated(15 * card.scale, 20 * card.scale)
        alpha = int(35 * card.opacity * card.depth)
        p.setBrush(QColor(0, 0, 0, alpha))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(shadow, radius, radius)

    def __desenhar_glow(self, p: QPainter, r: QRectF, radius: float,
                        card: CardRenderData) -> None:
        """Glow verde na carta central ou sombra lateral nas restantes."""
        soff = 10 if card.is_centre else (6 + int(8 * card.depth))
        sr = r.translated(soff, soff)
        if card.is_centre:
            color = ACCENT_GLOW
        else:
            alpha = int(40 * card.opacity * (1.0 - card.depth * 0.5))
            color = QColor(0, 0, 0, alpha)
        p.setBrush(QBrush(color))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(sr, radius, radius)

    def __desenhar_fundo(self, p: QPainter, r: QRectF, radius: float,
                         card: CardRenderData) -> None:
        """Clip-path + fundo escurecido proporcionalmente a profundidade."""
        clip = QPainterPath()
        clip.addRoundedRect(r, radius, radius)
        p.setClipPath(clip)

        d = card.depth
        if d > 0:
            bg = QColor(
                int(CARD_BG.red() * (1.0 - d * 0.3)),
                int(CARD_BG.green() * (1.0 - d * 0.3)),
                int(CARD_BG.blue() * (1.0 - d * 0.1)),
            )
        else:
            bg = QColor(CARD_BG)
        bg.setAlpha(int(255 * card.opacity * (1.0 - d * 0.2)))
        p.fillRect(r, bg)

    def __desenhar_vinheta(self, p: QPainter, r: QRectF,
                           card: CardRenderData) -> None:
        """Gradiente diagonal para cartas com profundidade > 0.15."""
        if card.depth <= 0.15:
            return
        vig = QLinearGradient(r.topLeft(), r.bottomRight())
        vig.setColorAt(0.0, QColor(0, 0, 30,
                         int(60 * card.opacity * card.depth)))
        vig.setColorAt(1.0, QColor(30, 0, 0,
                         int(40 * card.opacity * card.depth)))
        p.fillRect(r, QBrush(vig))

    def __desenhar_retrato(self, p: QPainter, r: QRectF,
                           card: CardRenderData) -> None:
        """Pixmap do perfil redimensionado com opacidade por profundidade."""
        pm = card.character.pixmap
        if pm is None or pm.isNull():
            return
        sf = r.height() / pm.height()
        dw = pm.width() * sf
        dx = r.x() + (r.width() - dw) / 2.0
        p.setOpacity(card.opacity * (1.0 - card.depth * 0.35))
        p.drawPixmap(QRectF(dx, r.y(), dw, r.height()), pm, QRectF(pm.rect()))
        p.setOpacity(1.0)

    def __desenhar_barra_nome(self, p: QPainter, r: QRectF,
                              card: CardRenderData) -> None:
        """Barra inferior com gradiente e nome do perfil."""
        bar_h = r.height() * NAME_BAR_RATIO
        bar = QRectF(r.x(), r.bottom() - bar_h, r.width(), bar_h)
        grad = QLinearGradient(bar.topLeft(), bar.bottomLeft())
        grad.setColorAt(0.0, QColor(0, 0, 0, 0))
        alpha = int(210 * card.opacity * (1.0 - card.depth * 0.3))
        grad.setColorAt(1.0, QColor(0, 0, 0, alpha))
        p.fillRect(bar, QBrush(grad))

        name_rect = bar.adjusted(8, 4, -8, -2)
        font = QFont("Segoe UI", int(14 * card.scale))
        font.setBold(True)
        p.setFont(font)
        name_alpha = int(255 * card.opacity * (1.0 - card.depth * 0.4))
        p.setPen(QColor(255, 255, 255, name_alpha))
        p.drawText(name_rect,
                   Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
                   card.character.name)

    def __desenhar_badge(self, p: QPainter, r: QRectF,
                         card: CardRenderData) -> None:
        """Tag com #char_id no canto inferior direito."""
        font = QFont("Segoe UI", int(7 * card.scale), QFont.Weight.Light)
        p.setFont(font)
        badge_alpha = int(160 * card.opacity * (1.0 - card.depth * 0.5))
        badge_text = f"#{card.character.char_id}"
        fm = QFontMetrics(font, self)
        bw = fm.horizontalAdvance(badge_text) + 8
        bh = fm.height()
        bx = r.right() - bw - 6
        by = r.bottom() - bh - 4

        p.setPen(Qt.PenStyle.NoPen)
        bg_alpha = int(80 * card.opacity * (1.0 - card.depth * 0.3))
        p.setBrush(QColor(0, 0, 0, bg_alpha))
        p.drawRoundedRect(QRectF(bx, by, bw, bh), 3, 3)

        p.setPen(QColor(130, 130, 170, badge_alpha))
        p.drawText(QRectF(bx, by, bw, bh),
                   Qt.AlignmentFlag.AlignCenter, badge_text)

    def __desenhar_borda(self, p: QPainter, r: QRectF, radius: float,
                         card: CardRenderData) -> None:
        """Borda accent na carta central ou edge nas restantes."""
        self.__aplicar_perspectiva(p, card)

        if card.is_centre:
            border = QPen(ACCENT_COLOR, max(2.0, 2.5 * card.scale))
            p.setPen(border)
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawRoundedRect(r, radius, radius)

            inner = r.adjusted(3 * card.scale, 3 * card.scale,
                               -3 * card.scale, -3 * card.scale)
            glow = QPen(QColor(47, 158, 65, int(50 * card.opacity)),
                        1.5 * card.scale)
            p.setPen(glow)
            inner_rad = max(2.0, radius - 3 * card.scale)
            p.drawRoundedRect(inner, inner_rad, inner_rad)
        else:
            alpha = int(70 * card.opacity * (1.0 - card.depth * 0.4))
            p.setPen(QPen(QColor(60, 60, 90, alpha), 1.0))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawRoundedRect(r, radius, radius)

        p.restore()
