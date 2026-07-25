import logging
from contextlib import contextmanager
from dataclasses import dataclass
from typing import List, Optional

from PySide6.QtCore import (
    Qt, QPropertyAnimation, QAbstractAnimation, Property,
    Signal, QEasingCurve, QRectF, Slot,
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
from view.infrastructure.layout_loader import LayoutLoader

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
        self.setObjectName("character_carousel")
        self.setProperty("class", "character_carousel")

        self.__characters = characters
        self.__index = 0
        self.__scroll_offset = 0.0
        self.__animation: Optional[QPropertyAnimation] = None

        self.__layout_loader = LayoutLoader.instance()
        self.__scale = self.__compute_scale()

        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.__btn_prev = QPushButton("\u25C0", self)
        self.__btn_prev.setObjectName("carousel_btn_prev")
        self.__btn_prev.setProperty("class", "carousel_nav_btn")

        self.__btn_next = QPushButton("\u25B6", self)
        self.__btn_next.setObjectName("carousel_btn_next")
        self.__btn_next.setProperty("class", "carousel_nav_btn")

        self.__update_nav_buttons()

        self.__btn_prev.setToolTip("Anterior (\u2190)")
        self.__btn_prev.clicked.connect(self.slide_previous)

        self.__btn_next.setToolTip("Pr\u00F3ximo (\u2192)")
        self.__btn_next.clicked.connect(self.slide_next)

        self.index_changed.emit(self.__index)

        self.__layout_loader.escala_atualizada.connect(self.__on_escala_atualizada)

    def __compute_scale(self) -> float:
        """Factor de escala proporcional ao tamanho disponivel.

        Usa o factor global do LayoutLoader combinado com a area
        de referencia do carousel.
        """
        L = self.__layout_loader
        ref_w = L.get("character_carousel", "ref_area", "largura")
        ref_h = L.get("character_carousel", "ref_area", "altura")
        global_scale = L.scale_factor()

        if self.width() == 0 or self.height() == 0:
            return global_scale

        local_scale = min(self.width() / ref_w, self.height() / ref_h)
        return min(global_scale, local_scale)

    def __card_width(self) -> float:
        return self.__layout_loader.scaled("character_carousel", "card", "largura_base") * self.__scale

    def __card_height(self) -> float:
        return self.__layout_loader.scaled("character_carousel", "card", "altura_base") * self.__scale

    def __slot_spacing(self) -> float:
        return self.__layout_loader.scaled("character_carousel", "slot_spacing") * self.__scale

    def __nav_btn_size(self) -> int:
        return int(self.__layout_loader.scaled("character_carousel", "nav_btn", "tamanho") * self.__scale)

    def __nav_btn_margin(self) -> int:
        return int(self.__layout_loader.scaled("character_carousel", "nav_btn", "margem") * self.__scale)

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
        if not self.__characters:
            raise ValueError(
                "[Erro - CharacterCarousel] Nao ha personagens no carousel."
            )
        return self.__characters[self.__index]

    def slide_previous(self) -> None:
        """Desliza para o perfil anterior ou executa bump no inicio."""
        self.__tentar_deslizar(-1)

    def slide_next(self) -> None:
        """Desliza para o perfil seguinte ou executa bump no fim."""
        self.__tentar_deslizar(1)

    def __tentar_deslizar(self, direcao: int) -> None:
        """Tenta deslizar o carousel, executando bump se estiver no limite."""
        if direcao not in (-1, 1):
            return
        if (self.__animation
                and self.__animation.state() == QAbstractAnimation.State.Running):
            self.__animation.stop()
            self.__ancorar_indice()
        if direcao == -1:
            if self.__index <= 0:
                self.__bump_animation(1.0)
                return
            self.__start_animation(self.__slot_spacing())
            return
        if direcao == 1:
            if self.__index >= len(self.__characters) - 1:
                self.__bump_animation(-1.0)
                return
            self.__start_animation(-self.__slot_spacing())

    def __bump_animation(self, direction: float) -> None:
        """Animacao elastica de ricochete nos limites do carousel."""
        if (self.__animation
                and self.__animation.state() == QAbstractAnimation.State.Running):
            self.__animation.stop()
        L = self.__layout_loader
        bump_dur = L.get("character_carousel", "bump_duration")
        self.__animation = QPropertyAnimation(self, b"scroll_offset")
        self.__animation.setDuration(bump_dur)
        self.__animation.setStartValue(0.0)
        self.__animation.setKeyValueAt(0.4, direction * 15.0 * self.__scale)
        self.__animation.setEndValue(0.0)
        self.__animation.setEasingCurve(QEasingCurve.Type.OutElastic)
        self.__animation.start()

    def __start_animation(self, target: float) -> None:
        """Animacao de deslize suave entre perfis."""
        if (self.__animation
                and self.__animation.state() == QAbstractAnimation.State.Running):
            self.__animation.stop()
        L = self.__layout_loader
        anim_dur = L.get("character_carousel", "anim_duration")
        self.__animation = QPropertyAnimation(self, b"scroll_offset")
        self.__animation.setDuration(anim_dur)
        self.__animation.setStartValue(0.0)
        self.__animation.setEndValue(target)
        self.__animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.__animation.finished.connect(lambda: self.__ancorar_indice())
        self.__animation.start()

    def __ancorar_indice(self) -> None:
        """Fixa o indice na carta mais proxima apos deslize."""
        if not self.__characters:
            self.__scroll_offset = 0.0
            self.update()
            return
        if self.__scroll_offset < 0:
            self.__index = min(len(self.__characters) - 1, self.__index + 1)
            self.__scroll_offset = 0.0
            self.update()
            self.index_changed.emit(self.__index)
            return
        if self.__scroll_offset > 0:
            self.__index = max(0, self.__index - 1)
            self.__scroll_offset = 0.0
            self.update()
            self.index_changed.emit(self.__index)
            return
        self.__scroll_offset = 0.0
        self.update()

    @Slot()
    def __on_escala_atualizada(self) -> None:
        """Reage a mudanca de escala global (resize da janela)."""
        self.__scale = self.__compute_scale()
        self.__update_nav_buttons()
        self.update()

    def resizeEvent(self, event: QResizeEvent) -> None:
        """Reposiciona os botoes de navegacao ao redimensionar."""
        self.__scale = self.__compute_scale()
        self.__update_nav_buttons()
        super().resizeEvent(event)

    def __update_nav_buttons(self) -> None:
        btn_size = self.__nav_btn_size()
        btn_margin = self.__nav_btn_margin()
        self.__btn_prev.setFixedSize(btn_size, btn_size)
        self.__btn_next.setFixedSize(btn_size, btn_size)
        cy = self.height() // 2 - btn_size // 2
        self.__btn_prev.move(btn_margin, cy)
        self.__btn_next.move(
            self.width() - btn_size - btn_margin, cy
        )

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Navegacao por teclado: setas laterais."""
        if event.key() == Qt.Key.Key_Left:
            self.slide_previous()
            return
        if event.key() == Qt.Key.Key_Right:
            self.slide_next()
            return
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
        self.__scale = self.__compute_scale()
        with QPainter(self) as painter:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

            self.__draw_background(painter)

            if not self.__characters:
                return

            cx = self.width() / 2.0
            cy = self.height() / 2.0
            cards = self.__build_cards_data(
                cx, cy, self.__slot_spacing(),
                self.__card_width(), self.__card_height(),
            )
            self.__render_cards(painter, cards)

    def __build_cards_data(
        self,
        cx: float,
        cy: float,
        slot_spacing: float,
        card_width: float,
        card_height: float,
    ) -> List[CardRenderData]:
        """Constroi a lista de dados de renderizacao para cada carta visivel."""
        L = self.__layout_loader
        cards: List[CardRenderData] = []
        for i, ch in enumerate(self.__characters):
            offset_px = (
                (i - self.__index) * slot_spacing + self.__scroll_offset
            )
            dist = abs(offset_px)

            if dist > slot_spacing * 2.3:
                continue

            t = min(1.0, dist / slot_spacing)
            scale_at_centre = L.get("character_carousel", "scale", "centro")
            scale_at_slot = L.get("character_carousel", "scale", "slot")
            scale_min = L.get("character_carousel", "scale", "min")
            card_scale = max(
                scale_min,
                scale_at_centre - t * (scale_at_centre - scale_at_slot),
            )
            opacity_at_centre = L.get("character_carousel", "opacity", "centro")
            opacity_at_slot = L.get("character_carousel", "opacity", "slot")
            opacity_min = L.get("character_carousel", "opacity", "min")
            opacity = max(
                opacity_min,
                opacity_at_centre
                - t * (opacity_at_centre - opacity_at_slot),
            )

            card_w = card_width * card_scale
            card_h = card_height * card_scale
            x = cx + offset_px - card_w / 2.0
            y = cy - card_h / 2.0

            cards.append(CardRenderData(
                rect=QRectF(x, y, card_w, card_h),
                scale=card_scale,
                opacity=opacity,
                character=ch,
                is_centre=dist < 1.0,
                depth=t,
                offset_px=offset_px,
                z_order=1.0 - t,
            ))

        cards.sort(key=lambda c: c.z_order)
        return cards

    def __render_cards(
        self,
        p: QPainter,
        cards: List[CardRenderData],
    ) -> None:
        """Itera pelas cartas ordenadas e delega o desenho."""
        for card in cards:
            self.__draw_card(p, card)

    def __draw_card(self, p: QPainter, card: CardRenderData) -> None:
        """Orquestrador de desenho — chama cada etapa por ordem."""
        r = card.rect
        radius = 12 * card.scale * self.__scale

        with self.__aplicar_perspectiva(p, card):
            self.__desenhar_sombra(p, r, radius, card)
            self.__desenhar_glow(p, r, radius, card)
            self.__desenhar_fundo(p, r, radius, card)
            self.__desenhar_vinheta(p, r, card)
            self.__desenhar_retrato(p, r, card)
            self.__desenhar_barra_nome(p, r, card)
            self.__desenhar_badge(p, r, card)
        self.__desenhar_borda(p, r, radius, card)

    @contextmanager
    def __aplicar_perspectiva(self, p: QPainter, card: CardRenderData):
        """Contexto de transformacao 3D: garante save/restore simetricos."""
        r = card.rect
        voff = card.depth * 30.0 * card.scale * self.__scale
        squish = 1.0 - card.depth * 0.15
        cx = r.center().x()
        cy = r.center().y()

        p.save()
        p.translate(cx, cy + voff)
        p.scale(squish, 1.0)
        p.translate(-cx, -cy - voff)
        try:
            yield
        finally:
            p.restore()

    def __desenhar_sombra(self, p: QPainter, r: QRectF, radius: float,
                          card: CardRenderData) -> None:
        """Sombra distante para cartas com profundidade > 0.1."""
        if card.depth <= 0.1:
            return
        shadow = r.translated(
            15 * card.scale * self.__scale, 20 * card.scale * self.__scale
        )
        alpha = int(35 * card.opacity * card.depth)
        p.setBrush(QColor(0, 0, 0, alpha))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(shadow, radius, radius)

    def __desenhar_glow(self, p: QPainter, r: QRectF, radius: float,
                        card: CardRenderData) -> None:
        """Glow verde na carta central ou sombra lateral nas restantes."""
        L = self.__layout_loader
        accent_glow = QColor(L.get("character_carousel", "cores", "accent_glow"))
        if card.is_centre:
            sr = r.translated(10, 10)
            p.setBrush(QBrush(accent_glow))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawRoundedRect(sr, radius, radius)
            return
        soff = 6 + int(8 * card.depth)
        sr = r.translated(soff, soff)
        alpha = int(40 * card.opacity * (1.0 - card.depth * 0.5))
        p.setBrush(QBrush(QColor(0, 0, 0, alpha)))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(sr, radius, radius)

    def __desenhar_fundo(self, p: QPainter, r: QRectF, radius: float,
                         card: CardRenderData) -> None:
        """Clip-path + fundo escurecido proporcionalmente a profundidade."""
        L = self.__layout_loader
        card_bg = QColor(L.get("character_carousel", "cores", "card_bg"))

        clip = QPainterPath()
        clip.addRoundedRect(r, radius, radius)
        p.setClipPath(clip)

        d = card.depth
        alpha = int(255 * card.opacity * (1.0 - d * 0.2))
        if d > 0:
            bg = QColor(
                int(card_bg.red() * (1.0 - d * 0.3)),
                int(card_bg.green() * (1.0 - d * 0.3)),
                int(card_bg.blue() * (1.0 - d * 0.1)),
            )
            bg.setAlpha(alpha)
            p.fillRect(r, bg)
            return
        bg = QColor(card_bg)
        bg.setAlpha(alpha)
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
        L = self.__layout_loader
        name_bar_ratio = L.get("character_carousel", "name_bar_ratio")
        bar_h = r.height() * name_bar_ratio
        bar = QRectF(r.x(), r.bottom() - bar_h, r.width(), bar_h)
        grad = QLinearGradient(bar.topLeft(), bar.bottomLeft())
        grad.setColorAt(0.0, QColor(0, 0, 0, 0))
        alpha = int(210 * card.opacity * (1.0 - card.depth * 0.3))
        grad.setColorAt(1.0, QColor(0, 0, 0, alpha))
        p.fillRect(bar, QBrush(grad))

        name_rect = bar.adjusted(
            int(8 * card.scale), int(4 * card.scale),
            int(-8 * card.scale), int(-2 * card.scale)
        )
        font = QFont("Segoe UI", int(14 * card.scale * self.__scale))
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
        font = QFont(
            "Segoe UI", int(7 * card.scale * self.__scale), QFont.Weight.Light
        )
        p.setFont(font)
        badge_alpha = int(160 * card.opacity * (1.0 - card.depth * 0.5))
        badge_text = f"#{card.character.char_id}"
        fm = QFontMetrics(font, self)
        bw = fm.horizontalAdvance(badge_text) + int(8 * self.__scale)
        bh = fm.height()
        bx = r.right() - bw - int(6 * self.__scale)
        by = r.bottom() - bh - int(4 * self.__scale)

        p.setPen(Qt.PenStyle.NoPen)
        bg_alpha = int(80 * card.opacity * (1.0 - card.depth * 0.3))
        p.setBrush(QColor(0, 0, 0, bg_alpha))
        p.drawRoundedRect(
            QRectF(bx, by, bw, bh),
            max(1.0, 3 * self.__scale), max(1.0, 3 * self.__scale)
        )

        p.setPen(QColor(130, 130, 170, badge_alpha))
        p.drawText(QRectF(bx, by, bw, bh),
                   Qt.AlignmentFlag.AlignCenter, badge_text)

    def __desenhar_borda(self, p: QPainter, r: QRectF, radius: float,
                         card: CardRenderData) -> None:
        """Borda accent na carta central ou edge nas restantes."""
        L = self.__layout_loader
        accent_color = QColor(L.get("character_carousel", "cores", "accent"))
        with self.__aplicar_perspectiva(p, card):
            if not card.is_centre:
                alpha = int(70 * card.opacity * (1.0 - card.depth * 0.4))
                p.setPen(QPen(QColor(60, 60, 90, alpha), 1.0))
                p.setBrush(Qt.BrushStyle.NoBrush)
                p.drawRoundedRect(r, radius, radius)
                return

            border = QPen(accent_color, max(2.0, 2.5 * card.scale * self.__scale))
            p.setPen(border)
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawRoundedRect(r, radius, radius)

            offset = 3 * card.scale * self.__scale
            inner = r.adjusted(offset, offset, -offset, -offset)
            glow = QPen(
                QColor(47, 158, 65, int(50 * card.opacity)),
                1.5 * card.scale * self.__scale
            )
            p.setPen(glow)
            inner_rad = max(2.0, radius - offset)
            p.drawRoundedRect(inner, inner_rad, inner_rad)