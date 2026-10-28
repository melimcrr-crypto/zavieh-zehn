# مشخصات فنی پایپ‌لاین رندر ابری و حفاظت کادرها — زاویه ذهن (`@zavieh.penhann`)

## ۱. حفاظت ریاضی کادرها (`Anti-Overflow Layout System`)
- `SAFE_MARGIN_X = 64.0`: هیچ باکس یا متنی اجازه‌ی ورود به ۶۴ پیکسل لبه‌ی چپ و راست بوم `1080×1920` را ندارد.
- `fit_font_to_width(text, font, max_width)`: اندازه‌گیری دقیق `textbbox` با `HarfBuzz/Raqm` و کاهش خودکار سایز فونت در صورت تجاوز از عرض مجاز.
- `draw_safe_card(...)`: محاسبه‌ی خودکار عرض موردنیاز یا فیت کردن متن با حداقل پدینگ داخلی `28px` از هر طرف.
- `draw_folder_window(...)` و `draw_pill_badge(...)`: کلمپ خودکار مختصات افقی و پدینگ داخلی ایمن.

## ۲. معماری زیرنویس تک‌بیت‌مپ تراز و ابریشمی (`SUBTITLE_BASELINE_Y = 1520.0` / `DEEP_GLOW_SUB_Y = 1510.0`)
- کل عبارت کوتاه (۴ تا ۷ کلمه) در یک بیت‌مپ واحد RTL روی خط کرسی ثابت `y = 1510..1520` (کاملاً بالاتر از آیدی پیج و کپشن اینستاگرام) شکل‌دهی می‌شود (`0.000px` پرش).
- مسک گرادیانی نرم `56..64px` در ۶۰ فریم‌برثانیه از راست به چپ لایه‌ی سفید درخشان `#FFFFFF` را روی لایه‌ی خاکستری مات `rgb(70,70,76)` آشکار می‌کند.

## ۳. موتور موشن‌گرافیک پیوسته‌ی `Studio v5.0 Deep-Glow` (`src/engine/deep_glow_core.py`)
- هاله‌ی اپتیکال ۴ اکتاو ۳۲ بیتی (`Float32 Multi-Scale Gaussian Pyramid + Reinhard Soft-Knee + Filmic Micro-Dither`) بدون هیچ پله‌ی کوانتیزاسیون در تاریکی مطلق `#000000`.
- لایه‌ی فوکوس‌کشی پیش‌زمینه (`Foreground DoF Pass-Through`) برای زوم‌های پیوسته‌ی دوربین از دل المان‌های نئونی، Whip-Pan با منحنی نمایی S-Curve، و رسم تدریجی خطوط (`Trim Paths`).

## ۴. خروجی مستر GitHub Actions
- تصویر: `1080×1920` • `60fps` • `libx264 -preset slow -crf 14 -profile:v high -level:v 4.2`.
- صدا: `LOCKED_SIGNATURE_VOICE = Rasalgethi` + `ENSAN_FIR_24K` + `-0.34st` • `AAC 320kbps @ 48kHz Stereo`.
