# مشخصات فنی موتور رندر ابری (`60fps Studio Engine`)

* **ابعاد تصویر:** `1080 × 1920` (نسبت `9:16` عمودی استاندارد Instagram Reels)
* **نرخ فریم:** **`60.0 fps`** (حداکثر نرمی حرکت خطوط برداری، ذرات و اسکنرها)
* **پس‌زمینه:** مشکی مطلق `#000000` (`RGB 0, 0, 0`) بهینه‌شده برای نمایشگرهای OLED
* **موتور گرافیک برداری:** `cairocffi` با Anti-Aliasing دقیق زیرپیکسلی + درخشش هاله‌ای دو مرحله‌ای (`Dual-Pass Gaussian Deep Glow`: شعاع هسته و شعاع هاله وسیع)
* **موتور تایپوگرافی فارسی:** `Pillow + HarfBuzz/Raqm` با خانواده فونت `Vazirmatn` (`Light`, `Regular`, `Medium`, `Bold`, `ExtraBold`) و زیرنویس کارائوکه راست‌به‌چپ (`RTL Word-by-Word Highlight`)
* **همگام‌سازی صحنه‌ها (`Word-Index Choreography`):** زمان شروع و پایان هر ضرب بصری (`Visual Beat`) مستقیماً به زمان واقعی ادا شدن خطوط در خروجی `faster-whisper (medium)` قفل می‌شود؛ بنابراین حتی یک فریم جا‌به‌جایی بین کلام گوینده و انیمیشن رخ نمی‌دهد.
* **پروفایل انکودینگ خروجی `FFmpeg`:**
  * ویدیو: `libx264 -preset slow -crf 14 -profile:v high -level 4.2 -pix_fmt yuv420p`
  * صدا: `aac -b:a 320k -ar 48000 -ac 2`
  * پرچم استریم سریع: `-movflags +faststart`
