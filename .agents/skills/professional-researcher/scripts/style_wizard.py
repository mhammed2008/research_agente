"""
Interactive Style & Branding Wizard for Professional Researcher (v2.1).
Conducts an interactive, multi-turn intake questionnaire to configure:
- Brand Logo (file validation and embedding)
- Visual Style & Palette (curated presets or custom hex colors)
- Typography preferences
- Target Audience & Executive Tone
- Adaptive domain & regulatory requirements (unlimited follow-up inquiries)

Can be invoked standalone or via CLI:
    python style_wizard.py --output style_config.json
    python export_engine.py --wizard --input report.md
"""

import os
import sys
import re
import json

# 5 Structural Design Archetypes
ARCHETYPE_PRESETS = {
    "1": {
        "id": "consulting_grid",
        "name": "Consulting Grid (McKinsey/BCG structured cards, soft slate canvas)",
        "card_framing": "rounded_card",
        "header_style": "accent_bar",
        "primary": "#0F172A",
        "accent": "#2563EB",
        "font": "Calibri"
    },
    "2": {
        "id": "modern_dark",
        "name": "Modern Dark Tech (Deep obsidian canvas, dark translucent cards, electric cyan/violet)",
        "card_framing": "translucent",
        "header_style": "glow_badge",
        "primary": "#0A0F1D",
        "accent": "#38BDF8",
        "font": "Arial"
    },
    "3": {
        "id": "minimal_editorial",
        "name": "Minimal Editorial (Swiss typography, pure white canvas, frameless borderless layout)",
        "card_framing": "frameless",
        "header_style": "clean_underline",
        "primary": "#0A0A0A",
        "accent": "#2563EB",
        "font": "Arial"
    },
    "4": {
        "id": "warm_organic",
        "name": "Warm Organic (Soft cream/sand canvas, earthy forest/sage tones, organic rounded cards)",
        "card_framing": "rounded_card",
        "header_style": "pill",
        "primary": "#1C3A27",
        "accent": "#059669",
        "font": "Calibri"
    },
    "5": {
        "id": "vibrant_bold",
        "name": "Vibrant Bold (High contrast, solid colored metric tiles, high energy pitch deck)",
        "card_framing": "rounded_card",
        "header_style": "accent_bar",
        "primary": "#0F172A",
        "accent": "#7C3AED",
        "font": "Segoe UI"
    }
}

# Curated Style Presets with full hex tokens
PRESET_STYLES = {
    "1": {
        "id": "corporate-navy",
        "name": "Corporate Navy (Executive & Enterprise Intelligence)",
        "primary": "#0F172A",
        "accent": "#2563EB",
        "accent_light": "#DBEAFE",
        "bg_light": "#F8FAFC",
        "card_bg": "#FFFFFF",
        "card_border": "#E2E8F0",
        "font": "Calibri"
    },
    "2": {
        "id": "fintech-emerald",
        "name": "FinTech Emerald (Payments, Banking & Security)",
        "primary": "#064E3B",
        "accent": "#059669",
        "accent_light": "#D1FAE5",
        "bg_light": "#F0FDF4",
        "card_bg": "#FFFFFF",
        "card_border": "#A7F3D0",
        "font": "Calibri"
    },
    "3": {
        "id": "minimal-slate",
        "name": "Modern Slate (Cloud, Architecture & Systems)",
        "primary": "#1E293B",
        "accent": "#3B82F6",
        "accent_light": "#EFF6FF",
        "bg_light": "#F1F5F9",
        "card_bg": "#FFFFFF",
        "card_border": "#CBD5E1",
        "font": "Arial"
    },
    "4": {
        "id": "executive-crimson",
        "name": "Executive Crimson (High-Stakes, Healthcare & Risk)",
        "primary": "#881337",
        "accent": "#E11D48",
        "accent_light": "#FFE4E6",
        "bg_light": "#FFF1F2",
        "card_bg": "#FFFFFF",
        "card_border": "#FECDD3",
        "font": "Calibri"
    },
    "5": {
        "id": "luxury-violet",
        "name": "Luxury Violet (AI, Web3 & Future Innovation)",
        "primary": "#2E1065",
        "accent": "#7C3AED",
        "accent_light": "#EDE9FE",
        "bg_light": "#FAF5FF",
        "card_bg": "#FFFFFF",
        "card_border": "#DDD6FE",
        "font": "Segoe UI"
    }
}

AUDIENCE_PRESETS = {
    "1": "C-Suite & Executive Leadership (High-level ROI, strategic impact, and KPIs)",
    "2": "Engineering & Architecture (Technical deep dive, code hooks, and system specs)",
    "3": "Commercial & Investor Pitch (Unit economics, market sizing, and competitive moat)",
    "4": "Regulatory & Compliance (Formal standards, attestation, and audit evidence)"
}


def parse_style_prompt(prompt_text):
    """
    Parses a user's natural language style prompt and infers the best matching
    archetype, primary/accent colors, and layout framing.
    """
    p_lower = prompt_text.lower()
    hexes = re.findall(r'#(?:[0-9a-fA-F]{3}){1,2}', prompt_text)
    primary = hexes[0] if len(hexes) > 0 else None
    accent = hexes[1] if len(hexes) > 1 else None

    if any(k in p_lower for k in ["black and white", "monochrome", "minimal", "swiss", "clean", "editorial", "frameless", "borderless", "stark", "بسيط", "أبيض", "بدون إطار"]) and not any(k in p_lower for k in ["dark mode", "dark theme", "obsidian", "night", "cyber", "neon", "terminal", "داكن", "مظلم"]):
        arch = "minimal_editorial"
        primary = primary or "#0A0A0A"
        accent = accent or "#2563EB"
    elif any(k in p_lower for k in ["dark", "black", "obsidian", "night", "cyber", "neon", "terminal", "dark mode", "مظلم", "داكن", "ليلي"]):
        arch = "modern_dark"
        primary = primary or "#0A0F1D"
        accent = accent or "#38BDF8"
    elif any(k in p_lower for k in ["warm", "organic", "earth", "cream", "sand", "nature", "eco", "green", "canine", "animal", "دافئ", "بيئي", "طبيعي"]):
        arch = "warm_organic"
        primary = primary or "#1C3A27"
        accent = accent or "#059669"
    elif any(k in p_lower for k in ["vibrant", "bold", "pitch", "startup", "colorful", "high contrast", "حيوي", "جريء", "ستارتب"]):
        arch = "vibrant_bold"
        primary = primary or "#0F172A"
        accent = accent or "#7C3AED"
    elif any(k in p_lower for k in ["consulting", "corporate", "mckinsey", "bcg", "bain", "grid", "sharp", "مؤسسي", "استشاري"]):
        arch = "consulting_grid"
        primary = primary or "#0F172A"
        accent = accent or "#2563EB"
    else:
        arch = "consulting_grid"
        primary = primary or "#0F172A"
        accent = accent or "#2563EB"

    card_framing = "translucent" if arch == "modern_dark" else (
        "frameless" if arch == "minimal_editorial" else (
            "rounded_card" if arch == "warm_organic" else (
                "flat_tile" if arch == "vibrant_bold" else "sharp_card"
            )
        )
    )

    return {
        "archetype": arch,
        "is_dark_canvas": arch == "modern_dark",
        "card_framing": card_framing,
        "primary": primary,
        "primary_color": primary,
        "accent": accent,
        "accent_color": accent,
        "style_prompt": prompt_text
    }


def is_valid_hex(hex_str):
    """Validates 3 or 6 character hex color string."""
    if not isinstance(hex_str, str):
        return False
    return bool(re.match(r'^#(?:[0-9a-fA-F]{3}){1,2}$', hex_str.strip()))


def prompt_logo():
    """Prompts user for brand logo file path with existence verification."""
    print("\n[Question 1/4] Brand Logo Integration")
    print("─────────────────────────────────────────────────────────────")
    print("Do you have a specific company or project logo file to embed?")
    print("Supported formats: .png, .jpg, .jpeg, .svg")
    print("(Press Enter to skip if no logo is available)")

    while True:
        try:
            val = input("Logo file path: ").strip().strip('"').strip("'")
        except (EOFError, KeyboardInterrupt):
            print("\n[!] Skipping logo selection.")
            return None

        if not val:
            print("  -> No logo specified. Proceeding with clean typography branding.")
            return None

        clean_path = os.path.abspath(val)
        if os.path.exists(clean_path):
            ext = os.path.splitext(clean_path)[1].lower()
            if ext in [".png", ".jpg", ".jpeg", ".svg"]:
                print(f"  ✓ Verified logo: {clean_path}")
                return clean_path
            else:
                print(f"  [!] Unsupported image format: {ext}. Please provide PNG, JPG, or SVG.")
        else:
            print(f"  [!] File not found at: {clean_path}. Please re-enter or press Enter to skip.")


def prompt_style():
    """Prompts user to select from curated visual presets or input custom colors."""
    print("\n[Question 2/4] Visual Aesthetic & Color Palette")
    print("─────────────────────────────────────────────────────────────")
    for key, p in PRESET_STYLES.items():
        print(f"  [{key}] {p['name']} ({p['primary']} / {p['accent']})")
    print("  [6] Custom Brand Palette (Provide your own Primary & Accent Hex codes)")

    while True:
        try:
            choice = input("Select style [1-6] (default: 1): ").strip()
        except (EOFError, KeyboardInterrupt):
            choice = "1"

        if not choice:
            choice = "1"

        if choice in PRESET_STYLES:
            selected = dict(PRESET_STYLES[choice])
            print(f"  ✓ Selected: {selected['name']}")
            return selected
        elif choice == "6":
            # Custom Palette Flow
            print("\n  Custom Palette Configuration:")
            while True:
                p_hex = input("    Primary Dark Hex (e.g., #0F172A): ").strip()
                if not p_hex.startswith("#"):
                    p_hex = "#" + p_hex
                if is_valid_hex(p_hex):
                    break
                print("    [!] Invalid hex color. Please enter format like #1E293B.")

            while True:
                a_hex = input("    Accent Vibrant Hex (e.g., #2563EB): ").strip()
                if not a_hex.startswith("#"):
                    a_hex = "#" + a_hex
                if is_valid_hex(a_hex):
                    break
                print("    [!] Invalid hex color. Please enter format like #2563EB.")

            return {
                "id": "custom",
                "name": f"Custom Brand Palette ({p_hex} / {a_hex})",
                "primary": p_hex,
                "accent": a_hex,
                "accent_light": "#EFF6FF",
                "bg_light": "#F8FAFC",
                "card_bg": "#FFFFFF",
                "card_border": "#CBD5E1",
                "font": "Calibri"
            }
        else:
            print("  [!] Please select a number between 1 and 6.")


def prompt_audience():
    """Prompts user for target audience tone."""
    print("\n[Question 3/4] Target Audience & Depth Level")
    print("─────────────────────────────────────────────────────────────")
    for key, desc in AUDIENCE_PRESETS.items():
        print(f"  [{key}] {desc}")

    try:
        choice = input("Select audience [1-4] (default: 1): ").strip()
    except (EOFError, KeyboardInterrupt):
        choice = "1"

    if choice not in AUDIENCE_PRESETS:
        choice = "1"

    print(f"  ✓ Target Tone: {AUDIENCE_PRESETS[choice]}")
    return AUDIENCE_PRESETS[choice]


def prompt_adaptive_requirements():
    """
    Adaptive multi-turn questioning loop with NO limit on questions.
    Continues inquiring for extra data, specific benchmarks, competitors,
    or regulatory frameworks until the user confirms readiness.
    """
    print("\n[Question 4/4] Adaptive Domain Focus & Extra Context")
    print("─────────────────────────────────────────────────────────────")
    print("Specify any specific companies, competitors, regulatory mandates,")
    print("or custom KPIs to emphasize. (Press Enter to finish if none)")

    requirements = []
    question_count = 1

    while True:
        try:
            item = input(f"Requirement/Constraint #{question_count}: ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not item:
            break

        requirements.append(item)
        print(f"  ✓ Added: {item}")
        question_count += 1

    return requirements


def prompt_style_mode():
    """
    Prompts user FIRST: Choose style dynamically based on domain examples,
    write custom style prompt, or choose from 5 structural archetypes.
    """
    print("\n[Step 1/5] Presentation Design & Structural Strategy")
    print("─────────────────────────────────────────────────────────────")
    print("How would you like to define the presentation's visual style and structure?")
    print("  [1] (Recommended) Dynamic Domain-Adaptive (Auto-research real slide decks in this domain)")
    print("  [2] Custom Style Prompt (Describe your own design, mood, and colors in words)")
    print("  [3] Curated Structural Archetype (Pick from 5 proven consulting & tech architectures)")

    try:
        choice = input("Select mode [1-3] (default: 1): ").strip()
    except (EOFError, KeyboardInterrupt):
        choice = "1"

    if not choice or choice not in ["1", "2", "3"]:
        choice = "1"

    if choice == "1":
        print("\n  Dynamic Domain-Adaptive Mode:")
        print("  The engine will research slide decks in your target domain and match their visual DNA.")
        try:
            domain = input("  Target Domain / Industry (e.g., FinTech, AI, Canine Welfare, CyberSec): ").strip()
        except (EOFError, KeyboardInterrupt):
            domain = "General Technology"
        if not domain:
            domain = "General Technology"
        print(f"  ✓ Target Domain: {domain}")
        return {
            "mode": "dynamic_domain",
            "domain": domain,
            "archetype": "consulting_grid"
        }

    elif choice == "2":
        print("\n  Custom Style Prompt Mode:")
        print("  Describe how your presentation should look (e.g. 'Dark cyber tech with neon cyan,")
        print("  borderless cards, and high contrast stats' or 'Warm organic earth tones with sage green').")
        try:
            p_text = input("  Your Style Prompt: ").strip()
        except (EOFError, KeyboardInterrupt):
            p_text = "Modern professional slide deck"
        if not p_text:
            p_text = "Modern professional slide deck"
        parsed = parse_style_prompt(p_text)
        print(f"  ✓ Synthesized Archetype: {parsed['archetype']}")
        return {
            "mode": "custom_prompt",
            "prompt": p_text,
            "archetype": parsed["archetype"],
            "primary": parsed.get("primary"),
            "accent": parsed.get("accent")
        }

    else:
        print("\n  Curated Structural Archetypes:")
        for k, arch in ARCHETYPE_PRESETS.items():
            print(f"  [{k}] {arch['name']}")
        try:
            a_choice = input("Select archetype [1-5] (default: 1): ").strip()
        except (EOFError, KeyboardInterrupt):
            a_choice = "1"
        if a_choice not in ARCHETYPE_PRESETS:
            a_choice = "1"
        selected = ARCHETYPE_PRESETS[a_choice]
        print(f"  ✓ Selected Archetype: {selected['name']}")
        return {
            "mode": "archetype",
            "archetype": selected["id"],
            "primary": selected.get("primary"),
            "accent": selected.get("accent")
        }


def run_intake_wizard(output_json=None):
    """
    Executes the complete interactive intake wizard and returns the style config dict.
    Optionally saves to output_json.
    """
    print("═════════════════════════════════════════════════════════════")
    print("  🎨 Professional Researcher Interactive Style & Scope Wizard")
    print("═════════════════════════════════════════════════════════════")

    style_mode = prompt_style_mode()
    logo_path = prompt_logo()

    # If colors were not already provided by custom prompt, prompt style or inherit from archetype
    if style_mode.get("primary") and style_mode.get("accent"):
        style_info = {
            "id": style_mode.get("archetype", "custom"),
            "name": f"Dynamic {style_mode.get('archetype')}",
            "primary": style_mode["primary"],
            "accent": style_mode["accent"],
            "font": ARCHETYPE_PRESETS.get("1", {}).get("font", "Calibri")
        }
    else:
        style_info = prompt_style()

    audience = prompt_audience()
    focus_areas = prompt_adaptive_requirements()

    config = {
        "style_mode": style_mode.get("mode", "dynamic_domain"),
        "domain": style_mode.get("domain", ""),
        "style_prompt": style_mode.get("prompt", ""),
        "archetype": style_mode.get("archetype", "consulting_grid"),
        "style_id": style_info.get("id", "consulting_grid"),
        "style_name": style_info.get("name", "Custom"),
        "primary_color": style_info.get("primary"),
        "accent_color": style_info.get("accent"),
        "accent_light": style_info.get("accent_light", "#EFF6FF"),
        "bg_light": style_info.get("bg_light", "#F8FAFC"),
        "card_bg": style_info.get("card_bg", "#FFFFFF"),
        "card_border": style_info.get("card_border", "#CBD5E1"),
        "font_family": style_info.get("font", "Calibri"),
        "logo_path": logo_path,
        "audience": audience,
        "focus_areas": focus_areas
    }

    if output_json:
        out_dir = os.path.dirname(os.path.abspath(output_json))
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir, exist_ok=True)
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"\n[✓] Saved style configuration to: {output_json}")

    print("\n═════════════════════════════════════════════════════════════")
    print("  ✓ Style & Scope configuration finalized successfully!")
    print("═════════════════════════════════════════════════════════════\n")
    return config


def load_style_config(config_source):
    """
    Loads style config from either:
    - Path to a JSON file
    - Inline JSON string
    - Existing dictionary
    """
    if isinstance(config_source, dict):
        return config_source

    if not config_source:
        return {}

    if os.path.exists(config_source):
        with open(config_source, "r", encoding="utf-8") as f:
            return json.load(f)

    # Try parsing as inline JSON
    try:
        return json.loads(config_source)
    except Exception:
        return {}


if __name__ == "__main__":
    out_file = sys.argv[1] if len(sys.argv) > 1 else "style_config.json"
    run_intake_wizard(output_json=out_file)
