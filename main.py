from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path

import flet as ft

from amount_words import format_money, format_money_rub, receipt_summary
from create_template import build_order_docx
from seller import SELLER_NAME, SELLER_TAGLINE, resolve_logo_path

ROOT = Path(__file__).parent
OUTPUT_DIR = ROOT / "Товарные чеки"
COUNTER_PATH = ROOT / "receipt_counter.txt"

VAT_OPTIONS = ["Без НДС", "0%", "10%", "20%"]

C_INK = "#1A2E24"
C_MUTED = "#5C6B63"
C_LINE = "#D5DDD8"
C_SURFACE = "#F7F5F0"
C_PANEL = "#FFFFFF"
C_ACCENT = "#2F6B4F"
C_ACCENT_SOFT = "#E4EFE8"
C_HEADER = "#243D32"
C_DANGER = "#B42318"
C_OK = "#1B6B3A"

SPACE_XS = 4
SPACE_SM = 8
SPACE_MD = 12
SPACE_LG = 16
SPACE_XL = 24

PAD_PAGE = SPACE_XL
PAD_CARD = SPACE_LG
RADIUS_SM = 8
RADIUS_LG = 12


def parse_decimal(text: str) -> Decimal:
    cleaned = (text or "0").strip().replace(" ", "").replace(",", ".")
    if not cleaned:
        return Decimal("0")
    try:
        return Decimal(cleaned)
    except InvalidOperation:
        return Decimal("0")


def peek_receipt_no() -> str:
    if COUNTER_PATH.exists():
        try:
            return str(int(COUNTER_PATH.read_text().strip() or "0") + 1)
        except ValueError:
            pass
    return "1"


@dataclass
class ItemRow:
    name: str = ""
    qty: str = "1"
    unit: str = "шт"
    price: str = ""
    vat: str = "Без НДС"
    name_tf: ft.TextField | None = field(default=None, repr=False)
    qty_tf: ft.TextField | None = field(default=None, repr=False)
    price_tf: ft.TextField | None = field(default=None, repr=False)
    vat_dd: ft.Dropdown | None = field(default=None, repr=False)
    sum_label: ft.Text | None = field(default=None, repr=False)


def line_sum(item: ItemRow) -> Decimal:
    qty = parse_decimal(item.qty_tf.value if item.qty_tf else item.qty)
    price = parse_decimal(item.price_tf.value if item.price_tf else item.price)
    return (qty * price).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def section_title(text: str, hint: str = "") -> ft.Control:
    controls: list[ft.Control] = [
        ft.Text(text, size=15, weight=ft.FontWeight.W_600, color=C_INK),
    ]
    if hint:
        controls.append(ft.Text(hint, size=12, color=C_MUTED))
    return ft.Column(controls, spacing=SPACE_XS)


def panel_card(content: ft.Control, *, soft: bool = False) -> ft.Container:
    return ft.Container(
        content=content,
        padding=PAD_CARD,
        bgcolor=C_ACCENT_SOFT if soft else C_PANEL,
        border=ft.Border.all(1, "#C5D9CC" if soft else C_LINE),
        border_radius=RADIUS_LG,
    )


def main(page: ft.Page) -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    page.title = "PROSTOR"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = C_SURFACE
    page.padding = 0
    page.scroll = ft.ScrollMode.AUTO
    page.window.width = 1180
    page.window.height = 840
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=C_ACCENT,
            on_primary="#FFFFFF",
            secondary=C_HEADER,
            surface=C_PANEL,
            on_surface=C_INK,
        ),
    )

    items: list[ItemRow] = []

    def field_style(**kwargs) -> dict:
        return {
            "dense": False,
            "height": 52,
            "border_color": C_LINE,
            "focused_border_color": C_ACCENT,
            "cursor_color": C_ACCENT,
            "text_style": ft.TextStyle(color=C_INK, size=13),
            "label_style": ft.TextStyle(color=C_MUTED, size=12),
            **kwargs,
        }

    number_field = ft.TextField(
        label="№ чека",
        value=peek_receipt_no(),
        width=110,
        **field_style(),
    )
    date_field = ft.TextField(
        label="Дата",
        value=date.today().strftime("%d.%m.%Y"),
        width=150,
        **field_style(),
    )
    buyer_field = ft.TextField(
        label="Покупатель",
        value="Розничный покупатель",
        hint_text="ФИО / организация",
        expand=True,
        **field_style(),
    )

    total_text = ft.Text(
        "0,00 ₽", size=28, weight=ft.FontWeight.BOLD, color=C_INK)
    words_text = ft.Text(
        receipt_summary(0, 0),
        size=13,
        color=C_ACCENT,
        italic=True,
    )
    status_text = ft.Text("", size=13, color=C_OK)
    items_count = ft.Text("1 позиция", size=12, color=C_MUTED)

    rows_column = ft.Column(spacing=SPACE_MD)

    def sync_item_from_ui(item: ItemRow) -> None:
        if item.name_tf:
            item.name = item.name_tf.value or ""
        if item.qty_tf:
            item.qty = item.qty_tf.value or "0"
        if item.price_tf:
            item.price = item.price_tf.value or ""
        if item.vat_dd:
            item.vat = item.vat_dd.value or "Без НДС"

    def filled_items() -> list[ItemRow]:
        result = []
        for item in items:
            sync_item_from_ui(item)
            if (item.name or "").strip():
                result.append(item)
        return result

    def recalc(_: ft.ControlEvent | None = None) -> None:
        for item in items:
            sync_item_from_ui(item)
            if item.sum_label:
                item.sum_label.value = format_money_rub(line_sum(item))

        n = len(items)
        if n == 1:
            items_count.value = "1 позиция"
        elif 2 <= n <= 4:
            items_count.value = f"{n} позиции"
        else:
            items_count.value = f"{n} позиций"

        filled = filled_items()
        total_sum = sum((line_sum(item) for item in filled), Decimal("0"))
        total_text.value = format_money_rub(total_sum)
        words_text.value = receipt_summary(len(filled), total_sum)
        page.update()

    def remove_item(item: ItemRow) -> None:
        if len(items) <= 1:
            return
        items.remove(item)
        rebuild_rows()
        recalc()

    def make_row_ui(item: ItemRow, index: int) -> ft.Container:
        item.name_tf = ft.TextField(
            label="Название товара или услуги",
            value=item.name,
            expand=True,
            on_change=recalc,
            **field_style(),
        )
        item.qty_tf = ft.TextField(
            label="Кол-во",
            value=item.qty,
            width=88,
            on_change=recalc,
            **field_style(),
        )
        item.price_tf = ft.TextField(
            label="Цена",
            value=item.price,
            width=120,
            on_change=recalc,
            **field_style(),
        )
        item.vat_dd = ft.Dropdown(
            label="НДС",
            value=item.vat if item.vat in VAT_OPTIONS else VAT_OPTIONS[0],
            options=[ft.dropdown.Option(v) for v in VAT_OPTIONS],
            width=145,
            dense=False,
            height=52,
            on_select=recalc,
            border_color=C_LINE,
            focused_border_color=C_ACCENT,
            text_style=ft.TextStyle(color=C_INK, size=13),
            label_style=ft.TextStyle(color=C_MUTED, size=12),
        )
        item.sum_label = ft.Text(
            format_money_rub(line_sum(item)),
            size=14,
            weight=ft.FontWeight.W_600,
            color=C_INK,
            width=110,
            text_align=ft.TextAlign.RIGHT,
        )

        num_badge = ft.Container(
            content=ft.Text(
                str(index),
                size=13,
                weight=ft.FontWeight.BOLD,
                color=C_ACCENT,
            ),
            width=40,
            height=52,
            alignment=ft.Alignment.CENTER,
            bgcolor=C_ACCENT_SOFT,
            border_radius=RADIUS_SM,
        )
        delete_btn = ft.IconButton(
            icon=ft.Icons.CLOSE,
            icon_size=18,
            icon_color=C_MUTED,
            tooltip="Удалить",
            on_click=lambda e, it=item: remove_item(it),
            disabled=len(items) <= 1,
        )

        return panel_card(
            ft.Column(
                [
                    ft.Row(
                        [num_badge, item.name_tf, delete_btn],
                        spacing=SPACE_MD,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Row(
                        [
                            item.qty_tf,
                            item.price_tf,
                            item.vat_dd,
                            ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Text("Сумма", size=11,
                                                color=C_MUTED),
                                        item.sum_label,
                                    ],
                                    spacing=SPACE_XS,
                                    horizontal_alignment=ft.CrossAxisAlignment.END,
                                ),
                                expand=True,
                                alignment=ft.Alignment.CENTER_RIGHT,
                                padding=ft.Padding.only(
                                    left=SPACE_SM, top=SPACE_XS),
                            ),
                        ],
                        spacing=SPACE_MD,
                        vertical_alignment=ft.CrossAxisAlignment.START,
                    ),
                ],
                spacing=SPACE_SM,
            ),
        )

    def rebuild_rows() -> None:
        rows_column.controls = [
            make_row_ui(item, i + 1) for i, item in enumerate(items)
        ]
        page.update()

    def add_item(_: ft.ControlEvent | None = None) -> None:
        items.append(ItemRow())
        rebuild_rows()
        recalc()

    def export_docx(_: ft.ControlEvent) -> None:
        buyer = (buyer_field.value or "").strip()
        if not buyer:
            status_text.value = "Укажите покупателя."
            status_text.color = C_DANGER
            page.update()
            return

        filled = filled_items()
        if not filled:
            status_text.value = "Добавьте хотя бы один товар с названием."
            status_text.color = C_DANGER
            page.update()
            return

        receipt_no = (number_field.value or "").strip() or peek_receipt_no()
        doc_items = []
        total_sum = Decimal("0")

        for i, item in enumerate(filled, start=1):
            s = line_sum(item)
            total_sum += s
            qty = parse_decimal(item.qty)
            qty_str = str(int(qty)) if qty == qty.to_integral(
            ) else format_money(qty)
            vat_label = item.vat_dd.value if item.vat_dd else item.vat
            doc_items.append(
                {
                    "num": i,
                    "name": item.name.strip(),
                    "qty": qty_str,
                    "unit": item.unit,
                    "price": format_money_rub(parse_decimal(item.price)),
                    "vat": vat_label,
                    "sum": format_money_rub(s),
                }
            )

        order_date = date_field.value or date.today().strftime("%d.%m.%Y")
        out_path = OUTPUT_DIR / \
            f"Товарный чек №{receipt_no} от {order_date}.docx"

        build_order_docx(
            receipt_no=receipt_no,
            order_date=order_date,
            buyer=buyer,
            items=doc_items,
            total=format_money(total_sum),
            total_words_line=receipt_summary(len(doc_items), total_sum),
            path=out_path,
        )

        try:
            used = int(receipt_no)
            current = int(COUNTER_PATH.read_text().strip()
                          ) if COUNTER_PATH.exists() else 0
            if used >= current:
                COUNTER_PATH.write_text(str(used))
                number_field.value = str(used + 1)
        except ValueError:
            pass

        status_text.value = f"Сохранено: {out_path.name}"
        status_text.color = C_OK
        page.update()

        try:
            if page.platform == ft.PagePlatform.MACOS:
                os.system(f'open "{out_path}"')
            elif page.platform == ft.PagePlatform.WINDOWS:
                getattr(os, "startfile")(out_path)
            else:
                os.system(f'xdg-open "{out_path}"')
        except Exception:
            pass

    items.append(ItemRow())
    rebuild_rows()
    recalc()

    logo_path = resolve_logo_path()
    if logo_path is not None:
        logo_control: ft.Control = ft.Image(
            src=str(logo_path),
            width=112,
            height=112,
            fit=ft.BoxFit.CONTAIN,
        )
    else:
        logo_control = ft.Container(
            content=ft.Column(
                [
                    ft.Text("ЛОГО", size=11, weight=ft.FontWeight.BOLD,
                            color=C_ACCENT_SOFT),
                    ft.Text("assets/", size=9, color="#8FA898"),
                ],
                spacing=0,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            width=112,
            height=112,
            alignment=ft.Alignment.CENTER,
            border=ft.Border.all(1, "#3D5C4A"),
            border_radius=RADIUS_SM,
            bgcolor="#1C3228",
        )

    header = ft.Container(
        content=ft.Row(
            [
                logo_control,
                ft.Column(
                    [
                        ft.Text(
                            "PROSTOR",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            color="#FFFFFF",
                        ),
                        ft.Text(SELLER_NAME, size=12, color="#B8C9BF"),
                        ft.Text(SELLER_TAGLINE, size=11, color="#8FA898"),
                    ],
                    spacing=SPACE_XS,
                    expand=True,
                ),
            ],
            spacing=SPACE_LG,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.Padding.symmetric(horizontal=PAD_PAGE, vertical=SPACE_SM),
        bgcolor=C_HEADER,
    )

    details_card = panel_card(
        ft.Column(
            [
                section_title("Чек", "Номер, дата и покупатель"),
                ft.Row(
                    [number_field, date_field, buyer_field],
                    spacing=SPACE_MD,
                ),
            ],
            spacing=SPACE_MD,
        ),
    )

    items_header = ft.Row(
        [
            section_title("Товары и услуги"),
            ft.Container(expand=True),
            items_count,
            ft.OutlinedButton(
                "Добавить",
                icon=ft.Icons.ADD,
                on_click=add_item,
                style=ft.ButtonStyle(
                    color=C_ACCENT,
                    side=ft.BorderSide(1, C_ACCENT),
                    shape=ft.RoundedRectangleBorder(radius=RADIUS_SM),
                    padding=ft.Padding.symmetric(
                        horizontal=SPACE_LG, vertical=SPACE_MD),
                ),
            ),
        ],
        spacing=SPACE_MD,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    summary_card = panel_card(
        ft.Column(
            [
                ft.Text(
                    "ИТОГ К ОПЛАТЕ",
                    size=12,
                    weight=ft.FontWeight.W_600,
                    color=C_MUTED,
                ),
                total_text,
                ft.Divider(color=C_LINE, height=1),
                words_text,
                ft.FilledButton(
                    "Сформировать чек",
                    icon=ft.Icons.DESCRIPTION_OUTLINED,
                    on_click=export_docx,
                    style=ft.ButtonStyle(
                        bgcolor=C_ACCENT,
                        color="#FFFFFF",
                        shape=ft.RoundedRectangleBorder(radius=RADIUS_SM),
                        padding=ft.Padding.symmetric(
                            horizontal=SPACE_LG, vertical=SPACE_MD),
                    ),
                    width=float("inf"),
                ),
                status_text,
            ],
            spacing=SPACE_MD,
        ),
        soft=True,
    )
    summary_card.width = 300

    body = ft.Container(
        content=ft.Row(
            [
                ft.Container(
                    content=ft.Column(
                        [
                            details_card,
                            ft.Column(
                                [items_header, rows_column],
                                spacing=SPACE_MD,
                            ),
                        ],
                        spacing=SPACE_XL,
                        expand=True,
                    ),
                    expand=True,
                ),
                summary_card,
            ],
            spacing=SPACE_XL,
            vertical_alignment=ft.CrossAxisAlignment.START,
        ),
        padding=PAD_PAGE,
    )

    page.add(ft.Column([header, body], spacing=0, expand=True))


if __name__ == "__main__":
    ft.app(target=main)
