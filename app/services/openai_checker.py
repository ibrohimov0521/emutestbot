from __future__ import annotations

import json
import logging
from dataclasses import dataclass

from openai import AsyncOpenAI

from app.config import settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CheckResult:
    is_correct: bool
    score: float
    reason: str


class AnswerCheckError(Exception):
    pass


class OpenAIAnswerChecker:
    def __init__(self) -> None:
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def check(self, question: str, correct_answer: str, user_answer: str) -> CheckResult:
        prompt = f"""
Savol: {question}
To'g'ri javob: {correct_answer}
User javobi: {user_answer}

Vazifa: User javobini bahola. Savollar EMU operator yo'riqnomasi, ish jarayonlari,
xavfsizlik qoidalari yoki O'zbekiston tumanlari bo'yicha bo'lishi mumkin.

Mayda imlo xatolari, 1-2 ta harf adashishi, apostrof farqlari, o'zbek kirill/lotin
yozuvidagi farqlar, qisqa javoblar va bir xil ma'noli variantlarni to'g'ri deb
qabul qil. Masalan "Namangan", "Наманган", "Namangan viloyati", "Наманган вилояти",
"Namanganda" bir xil ma'noda bo'lishi mumkin. "manifest", "манифест",
"manifest orqali" kabi javoblar ham mazmuni bir xil bo'lsa to'g'ri hisoblanadi.

Tuman nomlarida "tumani", "тумани", "tuman" qo'shimchalari yoki tushib qolishi
mazmunni o'zgartirmasa, javobni to'g'ri deb qabul qil.

Javob mazmunan boshqa bo'lsa yoki muhim talabni noto'g'ri aytsa, noto'g'ri deb bahola.

Faqat JSON qaytar:
{{"is_correct": true, "score": 0.0, "reason": "qisqa izoh"}}
"""
        try:
            response = await self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Sen EMU operator yo'riqnomasi va umumiy test javoblarini qat'iy, "
                            "lekin adolatli tekshiradigan baholovchisan. Faqat valid JSON qaytar."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0,
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content or "{}"
            data = json.loads(content)
            return CheckResult(
                is_correct=bool(data["is_correct"]),
                score=max(0.0, min(1.0, float(data.get("score", 0.0)))),
                reason=str(data.get("reason", ""))[:500],
            )
        except Exception as exc:
            logger.exception("OpenAI answer check failed")
            raise AnswerCheckError("Answer checking failed") from exc
