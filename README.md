# EMU TEST BOT

Telegram uchun aiogram 3.x, OpenAI API va SQLite asosida yozilgan test bot.

## Imkoniyatlar

- `/start` orqali userni ro'yxatdan o'tkazadi.
- Bazadan 30 yoki 50 ta savolni tanlangan yo'nalish nisbatlari bo'yicha random tanlaydi.
- User javobni o'zi yozadi, OpenAI javobni JSON formatda baholaydi.
- Test sessiyasi va javoblar SQLite bazada saqlanadi.
- Bot restart bo'lsa ham aktiv test sessiyasi davom ettiriladi.
- Admin panel statistikani ko'rsatadi va userlarni pagination bilan chiqaradi.
- `/seed_questions` orqali tumanlar, operator yo'riqnomasi va EMU professional testlarini seed qiladi.

## Loyiha strukturasi

```text
emu_test_bot/
  app/
    main.py
    config.py
    database.py
    models.py
    keyboards.py
    states.py
    services/
      openai_checker.py
      test_service.py
      admin_service.py
      user_service.py
    handlers/
      user.py
      admin.py
      test.py
  data/
    bot.db
    uzbekistan_districts.json
    operator_manual_questions.json
    emu_operator_professional_test.json
  seed.py
  .env.example
  requirements.txt
  README.md
```

## O'rnatish

1. Python 3.11 yoki undan yangi versiya o'rnating.
2. Virtual environment yarating:

```bash
python -m venv .venv
```

3. Virtual environmentni yoqing.

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Linux yoki macOS:

```bash
source .venv/bin/activate
```

4. Kerakli paketlarni o'rnating:

```bash
pip install -r requirements.txt
```

5. `.env.example` faylidan `.env` yarating va qiymatlarni to'ldiring:

```env
BOT_TOKEN=telegram_bot_token
OPENAI_API_KEY=openai_api_key
OPENAI_MODEL=gpt-4o-mini
ADMIN_IDS=123456789
DATABASE_PATH=data/bot.db
QUESTIONS_PER_TEST=50
AUTO_SEED_DISTRICTS=false
```

`ADMIN_IDS` bir nechta bo'lsa vergul bilan yoziladi.

## Test yo'nalishlari

- `Sodda aralash` - tumanlar va `EMU operator professional test` savollari.
- `Murakkab aralash` - Toshkent tumanlarisiz tumanlar va `operator_manual_questions` savollari.
- `Tumanlar bo'yicha` - faqat tuman qaysi viloyatda joylashgani bo'yicha savollar.
- `Ish jarayoni bo'yicha` - 30% `EMU operator professional test`, 70% `operator_manual_questions`.

## Savollarni seed qilish

Barcha savollarni bazaga qo'shish:

```bash
python seed.py
```

Seed duplicate savollarni qayta qo'shmaydi. Bot ichida admin quyidagi komandalarni ishlatishi mumkin:

```text
/seed_questions
/seed_districts
```

## Botni ishga tushirish

```bash
python -m app.main
```

Bot lokal PC'da long polling orqali ishlaydi. Serverga chiqarishda ham shu arxitektura saqlanadi: `.env` qiymatlari serverda beriladi, SQLite fayl yo'li esa `DATABASE_PATH` orqali sozlanadi.

## Railway deploy

Railway GitHub repositorydan deploy qilganda start command `python -m app.main` bo'ladi. Repo ichida `railway.json` va `Procfile` tayyor.

Railway Variables bo'limiga quyidagilarni qo'shing:

```env
BOT_TOKEN=telegram_bot_token
OPENAI_API_KEY=openai_api_key
OPENAI_MODEL=gpt-4o-mini
ADMIN_IDS=123456789
QUESTIONS_PER_TEST=50
AUTO_SEED_DISTRICTS=true
DATABASE_PATH=/data/bot.db
```

SQLite ma'lumotlari restart yoki redeploydan keyin ham saqlanishi uchun Railway'da Volume yarating va mount path sifatida `/data` ni tanlang. Volume ishlatmasangiz, baza ephemeral filesystemda qoladi va deploy/restartlarda yo'qolishi mumkin.

## Admin komandalar

- `/admin` - umumiy statistika.
- `/users` - userlar ro'yxati, 10 tadan pagination.
- `/seed_questions` - barcha savollarni seed qilish.
- `/seed_districts` - O'zbekiston tumanlari savollarini seed qilish.

## OpenAI javob formati

Bot OpenAI'dan faqat quyidagi JSON formatni kutadi:

```json
{
  "is_correct": true,
  "score": 1.0,
  "reason": "qisqa izoh"
}
```

Agar OpenAI xato qaytarsa yoki JSON buzilsa, bot yiqilmaydi, xatoni log qiladi va userga qayta urinib ko'rishni aytadi.
