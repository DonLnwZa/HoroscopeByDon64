# 🔮 Rules: Thai Divination & Horoscope UI/UX Standards

## 1. Pure Thai Output Invariant
- User-facing horoscope/divination outputs must use pure, polished Thai text.
- Never output raw English strings for Thai astrology fields (e.g. use `วันอังคาร` instead of `Tuesday`, `ปีกุน (หมู)` instead of `ปีPig`).

## 2. Readable Divination Provenance
- Technical or astrological provenance formulas must be translated into friendly Thai explanations for end users:
  - `ตำราพรมชาติมหาภูติ: ฐานัง (1) + โภคา (5)`
  - `โหราศาสตร์ไทย: ดาวเจ้าเรือนตนุ (2)`
  - `ไพ่ทาโรต์ใบที่ X: <ชื่อไพ่>`
  - `คัมภีร์เลขศาสตร์ 7x9: ฐานเลข X`
  - `สังเคราะห์การคำนวณรวมจากทั้ง 4 ศาสตร์`

## 3. Clear Statistical Badges
- Heat index and statistical badges must clearly convey lottery context:
  - 🔥 `เลขเด็ดสุดฮิต (สถิติตลอดปีออก X ครั้ง)`
  - ⚡ `เลขสถิติดี (สถิติตลอดปีออก X ครั้ง)`
  - ❄️ `เลขลุ้นบิ๊กเซอร์ไพรส์ (ยังไม่เคยออกในปีนี้)` *(Avoid ambiguous terms like "หายาก (ชนะ 0 ครั้ง)")*

## 4. Thai Province Dropdowns
- Always populate Thai location selects with all **77 provinces** of Thailand, sorted alphabetically.

## 5. Mobile Responsive & Touch Safety
- On mobile viewports (including high-resolution WQHD+ 3120x1440 screens):
  - Stack form inputs into a single column (`grid-template-columns: 1fr`) to prevent uneven label wrapping.
  - Set `font-size: 16px` on text and select inputs to prevent iOS/Android unwanted page zooming.
  - Avoid emojis like `🃏` that fail to render on Android Chrome; prefer universally supported emojis like `🔮` or `✨`.
