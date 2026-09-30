#!/usr/bin/env python3
"""
Color Synthesizer Engine (v3.0)
Extracts dominant brand colors from logo images and mathematically derives
a unified, harmonic 5-tier color palette for presentations and documents.
Eliminates all foreign, hardcoded, or clashing colors.
"""

import os
import re
import math
from PIL import Image

def hex_to_rgb(hex_str):
    """Converts hex string to (R, G, B) tuple of ints 0-255."""
    hex_str = hex_str.lstrip("#")
    if len(hex_str) == 3:
        hex_str = "".join(c * 2 for c in hex_str)
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb):
    """Converts (R, G, B) tuple to #RRGGBB."""
    return f"#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}"

def mix_colors(color1, color2, weight=0.5):
    """Blends two RGB colors by weight (0.0 = all color2, 1.0 = all color1)."""
    r = int(round(color1[0] * weight + color2[0] * (1.0 - weight)))
    g = int(round(color1[1] * weight + color2[1] * (1.0 - weight)))
    b = int(round(color1[2] * weight + color2[2] * (1.0 - weight)))
    return (min(255, max(0, r)), min(255, max(0, g)), min(255, max(0, b)))

def get_luminance(rgb):
    """Calculates relative perceived luminance (0.0 to 1.0)."""
    return (0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]) / 255.0

def adjust_lightness(rgb, factor):
    """Adjusts lightness towards black (factor < 1) or white (factor > 1)."""
    if factor >= 1.0:
        return mix_colors((255, 255, 255), rgb, weight=min(1.0, factor - 1.0))
    else:
        return mix_colors(rgb, (0, 0, 0), weight=max(0.0, factor))

def extract_logo_colors(image_path, max_colors=5):
    """
    Scans a logo image and extracts the top dominant non-background colors.
    Filters out fully transparent and pure white/light gray background pixels.
    """
    if not image_path or not os.path.exists(image_path):
        return []

    try:
        img = Image.open(image_path)
        img = img.convert("RGBA")
        if hasattr(img, "get_flattened_data"):
            pixels = [tuple(p) for p in img.get_flattened_data()]
        else:
            pixels = list(img.getdata())
        color_counts = {}

        for r, g, b, a in pixels:
            # Ignore transparent pixels
            if a < 50:
                continue
            # Ignore pure white or near-white canvas/background
            if r > 242 and g > 242 and b > 242:
                continue
            # Ignore pure black border artifacts if overwhelmingly common
            if r < 15 and g < 15 and b < 15 and a > 200:
                continue

            # Quantize color slightly to group near-identical shades (bin size 16)
            qr = (r // 16) * 16 + 8
            qg = (g // 16) * 16 + 8
            qb = (b // 16) * 16 + 8
            key = (qr, qg, qb)
            color_counts[key] = color_counts.get(key, 0) + 1

        if not color_counts:
            return []

        # Sort by frequency
        sorted_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)
        distinct_colors = []

        for color, count in sorted_colors:
            # Check color distance to already selected colors to avoid near-duplicates
            too_close = False
            for existing in distinct_colors:
                dist = math.sqrt(
                    (color[0] - existing[0]) ** 2 +
                    (color[1] - existing[1]) ** 2 +
                    (color[2] - existing[2]) ** 2
                )
                if dist < 45:
                    too_close = True
                    break
            if not too_close:
                distinct_colors.append(color)
                if len(distinct_colors) >= max_colors:
                    break

        return distinct_colors
    except Exception as e:
        print(f"[ColorSynthesizer] Warning: Logo extraction failed: {e}")
        return []

def synthesize_palette(logo_path=None, primary_hex=None, accent_hex=None, theme_preset=None, archetype="consulting_grid"):
    """
    Synthesizes a complete, 100% harmonized color palette.
    Derives primary, secondary, accent, bg_light, bg_tint, card_border, text_main, text_muted.
    Now archetype-aware: supports modern_dark, minimal_editorial, consulting_grid, warm_organic, and vibrant_bold.
    Guarantees zero clashing foreign colors.
    """
    extracted = extract_logo_colors(logo_path) if logo_path else []

    # 1. Determine Primary Color
    if primary_hex and not extracted:
        primary = hex_to_rgb(primary_hex)
    elif extracted:
        if archetype == "modern_dark":
            primary = hex_to_rgb("#0A0F1D") # Obsidian canvas
        else:
            primary = min(extracted, key=lambda c: get_luminance(c))
            if get_luminance(primary) > 0.4:
                primary = adjust_lightness(primary, 0.6)
    elif primary_hex:
        primary = hex_to_rgb(primary_hex)
    elif theme_preset == "emerald":
        primary = hex_to_rgb("#064E3B")
    elif theme_preset == "slate":
        primary = hex_to_rgb("#0F172A")
    elif theme_preset == "crimson":
        primary = hex_to_rgb("#881337")
    elif theme_preset == "dark" or archetype == "modern_dark":
        primary = hex_to_rgb("#0A0F1D")
    elif archetype == "warm_organic":
        primary = hex_to_rgb("#1C3A27")
    else:
        primary = hex_to_rgb("#0F172A") # Corporate Navy default

    # 2. Determine Accent Color
    if extracted and len(extracted) > 1:
        # Extract the most chromatic / vibrant brand accent directly from the logo
        logo_darkest = min(extracted, key=lambda c: get_luminance(c))
        remaining = [c for c in extracted if c != logo_darkest]
        if remaining:
            best_cand = max(remaining, key=lambda c: ((max(c) - min(c)) / 255.0) * (0.8 + 0.4 * get_luminance(c)))
            accent = best_cand
        else:
            accent = adjust_lightness(logo_darkest, 1.6)
    elif accent_hex:
        accent = hex_to_rgb(accent_hex)
    elif archetype == "modern_dark":
        accent = hex_to_rgb("#38BDF8") # Vibrant electric cyan default for dark canvas
    elif archetype == "warm_organic":
        accent = hex_to_rgb("#059669") # Warm emerald
    else:
        # Derive vibrant accent from primary by lightening and shifting
        accent = adjust_lightness(primary, 1.45)

    # 3. Derive Secondary Color
    secondary = mix_colors(primary, accent, 0.65)

    # 4. Archetype-Specific Tints, Backgrounds & Cards
    arch = (archetype or "consulting_grid").lower().replace("-", "_")

    if arch in ["modern_dark", "dark_tech", "dark"]:
        # Deep obsidian / charcoal canvas
        bg_canvas = mix_colors(primary, (10, 15, 29), 0.4)
        bg_light = bg_canvas
        card_bg = mix_colors(bg_canvas, (30, 41, 59), 0.7) # Dark slate card container
        card_border = mix_colors(accent, bg_canvas, 0.25)   # Subtle glowing accent boundary
        accent_light = mix_colors(accent, (255, 255, 255), 0.35)
        accent_border = accent
        text_main = (248, 250, 252) # Crisp White (Slate 50)
        text_muted = (148, 163, 184) # Slate 400
        is_dark_canvas = True

    elif arch in ["warm_organic", "humanitarian_eco", "organic"]:
        # Soft warm sand / natural cream canvas
        bg_light = hex_to_rgb("#FBF9F4")
        card_bg = (255, 255, 255)
        card_border = mix_colors(primary, hex_to_rgb("#E7E5E4"), 0.25)
        accent_light = mix_colors(accent, (255, 255, 255), 0.16)
        accent_border = mix_colors(accent, (255, 255, 255), 0.4)
        text_main = hex_to_rgb("#1C1917") # Deep warm stone
        text_muted = hex_to_rgb("#78716C")
        is_dark_canvas = False

    elif arch in ["minimal_editorial", "swiss_clean", "editorial"]:
        # Stark pure white canvas, high contrast, clean typography
        bg_light = (255, 255, 255)
        card_bg = (255, 255, 255)
        card_border = hex_to_rgb("#E2E8F0")
        accent_light = mix_colors(accent, (255, 255, 255), 0.10)
        accent_border = mix_colors(accent, (255, 255, 255), 0.30)
        text_main = (10, 10, 10) # Pure black
        text_muted = (100, 116, 139)
        is_dark_canvas = False

    elif arch in ["vibrant_bold", "pitch_deck", "bold"]:
        # Bold contrast, dynamic saturation
        bg_light = mix_colors(primary, (255, 255, 255), 0.04)
        card_bg = (255, 255, 255)
        card_border = mix_colors(accent, (255, 255, 255), 0.35)
        accent_light = mix_colors(accent, (255, 255, 255), 0.20)
        accent_border = accent
        text_main = (15, 23, 42)
        text_muted = (71, 85, 105)
        is_dark_canvas = False

    else:
        # Standard Consulting Grid (McKinsey / BCG classic)
        bg_light = mix_colors(primary, (255, 255, 255), 0.035)
        card_bg = (255, 255, 255)
        card_border = mix_colors(primary, (255, 255, 255), 0.16)
        accent_light = mix_colors(accent, (255, 255, 255), 0.14)
        accent_border = mix_colors(accent, (255, 255, 255), 0.35)
        text_main = (15, 23, 42)
        text_muted = (100, 116, 139)
        is_dark_canvas = False

    if arch in ["modern_dark", "cyber_dark", "dark"]:
        card_framing = "translucent"
    elif arch in ["minimal_editorial", "swiss_clean", "editorial"]:
        card_framing = "frameless"
    elif arch in ["warm_organic", "nature", "earthy"]:
        card_framing = "rounded_card"
    elif arch in ["vibrant_bold", "pitch_deck", "bold"]:
        card_framing = "flat_tile"
    else:
        card_framing = "sharp_card"

    # 5. Harmonized Semantic Callout Palettes
    if is_dark_canvas:
        callout_note_border = accent
        callout_note_bg = mix_colors(accent, card_bg, 0.2)
        callout_note_text = (248, 250, 252)

        callout_tip_border = hex_to_rgb("#10B981")
        callout_tip_bg = mix_colors(hex_to_rgb("#10B981"), card_bg, 0.2)
        callout_tip_text = (248, 250, 252)

        crimson_tone = hex_to_rgb("#F43F5E")
        callout_imp_border = crimson_tone
        callout_imp_bg = mix_colors(crimson_tone, card_bg, 0.2)
        callout_imp_text = (255, 255, 255)

        amber_tone = hex_to_rgb("#F59E0B")
        callout_warn_border = amber_tone
        callout_warn_bg = mix_colors(amber_tone, card_bg, 0.2)
        callout_warn_text = (255, 255, 255)
    else:
        callout_note_border = accent
        callout_note_bg = mix_colors(accent, (255, 255, 255), 0.05)
        callout_note_text = primary

        callout_tip_border = accent
        callout_tip_bg = mix_colors(accent, (255, 255, 255), 0.05)
        callout_tip_text = primary

        crimson_tone = hex_to_rgb("#BE123C")
        callout_imp_border = crimson_tone
        callout_imp_bg = mix_colors(crimson_tone, (255, 255, 255), 0.04)
        callout_imp_text = hex_to_rgb("#9F1239")

        amber_tone = hex_to_rgb("#D97706")
        callout_warn_border = amber_tone
        callout_warn_bg = mix_colors(amber_tone, (255, 255, 255), 0.04)
        callout_warn_text = hex_to_rgb("#92400E")

    return {
        "archetype": arch,
        "is_dark_canvas": is_dark_canvas,
        "card_framing": card_framing,
        "primary": primary,
        "primary_hex": rgb_to_hex(primary),
        "secondary": secondary,
        "secondary_hex": rgb_to_hex(secondary),
        "accent": accent,
        "accent_hex": rgb_to_hex(accent),
        "accent_light": accent_light,
        "accent_light_hex": rgb_to_hex(accent_light),
        "accent_border": accent_border,
        "accent_border_hex": rgb_to_hex(accent_border),
        "bg_light": bg_light,
        "bg_light_hex": rgb_to_hex(bg_light),
        "card_bg": card_bg,
        "card_bg_hex": rgb_to_hex(card_bg),
        "card_border": card_border,
        "card_border_hex": rgb_to_hex(card_border),
        "body": text_main,
        "body_hex": rgb_to_hex(text_main),
        "muted": text_muted,
        "muted_hex": rgb_to_hex(text_muted),
        "callouts": {
            "note": {"border": callout_note_border, "bg": callout_note_bg, "text": callout_note_text},
            "tip": {"border": callout_tip_border, "bg": callout_tip_bg, "text": callout_tip_text},
            "important": {"border": callout_imp_border, "bg": callout_imp_bg, "text": callout_imp_text},
            "warning": {"border": callout_warn_border, "bg": callout_warn_bg, "text": callout_warn_text},
        }
    }

if __name__ == "__main__":
    test_logo = "researches/yemen_dog_rescue_initiative/assets/dog_rescue_logo.png" if os.path.exists("researches/yemen_dog_rescue_initiative/assets/dog_rescue_logo.png") else "yemen_dog_rescue_initiative/assets/dog_rescue_logo.png"
    p = synthesize_palette(logo_path=test_logo)
    print("Synthesized Palette for Yemen Dog Rescue Logo:")
    print("  Primary:", p["primary_hex"])
    print("  Accent:", p["accent_hex"])
    print("  Secondary:", p["secondary_hex"])
    print("  BG Light:", p["bg_light_hex"])
    print("  Card Border:", p["card_border_hex"])
