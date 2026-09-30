---
name: humanizer
description: |
  Rewrite AI-sounding text so it reads naturally like an expert human writer without changing factual meaning.
  Removes AI tells: not-X-but-Y contrasts, one-line closers, staged openers, forced triads, em-dashes,
  inflated claims, sales language, stock AI filler, and machine-translated Arabic cliches.
license: MIT
metadata:
  version: "3.1.0"
---

# Humanizer: Remove AI Writing Patterns & Humanize Arabic & English Prose

Rewrite AI-sounding text so it reads like an authentic human specialist, not a chatbot. Keep what it says. Do not invent facts.

## Core Rules for English & Arabic Humanization

### 1. The Structure Tells
- **No "Not X, but Y" or "Not only X, but also Y":**
  - *English tell:* "It's not just a payment tool, but an enterprise ecosystem." -> *Human:* "An enterprise payment system."
  - *Arabic tell:* "لا يقتصر الأمر على... بل يمتد ليشمل..." / "ليست مجرد تقنية، بل هي..." -> *Human:* صياغة الخبر مباشرة دون نفي مسبق مصطنع.
- **No Forced Triads:** Models love grouping nouns or adjectives in threes ("innovation, security, and scalability"). Cut the weakest or vary the sentence structure.
- **No Staged Openers:** Eliminate "Let's dive in", "Here's what you need to know", "At its core", "Fundamentally".
- **No Dramatic Closers:** Cut standalone repetitive one-liners ("That is the real win", "Let that sink in").

### 2. Specialized Arabic Humanization Rules (أنسنة المحتوى العربي)
When writing or auditing Arabic technical and business copywriting:

1. **Avoid Robot Arabic Cliches (تجنب الكليشيهات الآلية المتكررة):**
   - ❌ "في ظل التطور الرقمي المتسارع..." -> احذفها تماماً وابدأ بالموضوع مباشرة.
   - ❌ "يجدر بالذكر أن..." / "من الأهمية بمكان..." -> اكتب المعلومة مباشرة.
   - ❌ "حل ثوري يغير قواعد اللعبة..." / "طفرة نوعية..." -> اذكر الإنجاز التقني الفعلي بالأرقام والمواصفات.
   - ❌ استخدام "تلامس" ومشتقاتها في سياق الدفع اللاتلامسي -> استخدم مصطلحات مصرفية طبيعية: "الدفع باللمس"، "تقريب الهاتف من القارئ"، "تمرير البطاقة".

2. **Executive & Engineering Tone (النبرة التنفيذية والهندسية):**
   - اكتب بلغة مهندس نظم يتحدث إلى قيادة تقنية ومصرفية.
   - ركّز على **ما تم تنفيذه وبرمجته بالفعل** (Who, What, How) بدلاً من الوعود المستقبلية والتسويقية.
   - اجعل الجمل رشيقة، واضحة، ومترابطة بروابط لغوية عربية طبيعية (الواو، الفاء، حيث، مع).
   - تجنب الترجمة الحرفية من الإنجليزية التي تؤدي إلى تراكيب لغوية هجينة وركيكة.
