from __future__ import annotations

import re
from collections import defaultdict

from fastapi import APIRouter, Depends
from sqlalchemy import literal, or_
from sqlalchemy.orm import Session, joinedload

from ..database import get_db
from ..models import FaqEntry, FaqKeyword
from ..schemas import ChatAskIn, ChatAskOut, ChatLinkOut, ChatOptionOut

router = APIRouter(prefix="/api/chat", tags=["chat"])

STOPWORDS = {
    "the",
    "and",
    "for",
    "are",
    "was",
    "you",
    "your",
    "can",
    "how",
    "what",
    "where",
    "with",
    "this",
    "that",
    "have",
    "need",
    "please",
    "just",
    "from",
    "about",
    "want",
    "would",
    "could",
    "some",
    "help",
    "lang",
    "naman",
    "yung",
    "mga",
    "ang",
    "ng",
    "sa",
    "ko",
    "mo",
    "po",
}

TAGALOG_HINTS = {
    "po",
    "opo",
    "ano",
    "paano",
    "pano",
    "saan",
    "kailan",
    "kelan",
    "magkano",
    "pwede",
    "pwedeng",
    "gusto",
    "hanap",
    "hanapin",
    "bulaklak",
    "padala",
    "alaga",
    "alagaan",
    "bayad",
    "bayaran",
    "presyo",
    "oras",
    "sundan",
    "nasaan",
    "nanay",
    "mama",
    "kaarawan",
    "pasensya",
    "pasensiya",
    "salamat",
    "kamusta",
    "kumusta",
    "meron",
    "wala",
    "hindi",
    "sakin",
    "natin",
    "ninyo",
    "kayo",
    "ako",
}

GREETINGS = {"hi", "hello", "hey", "yo", "kamusta", "kumusta"}

HANDOVER = {
    "en": (
        "I didn't quite catch that. I'll transfer you to an agent — a real person — "
        "so they can assist you better. You can also reach us at hello@sariwa.ph or 0917 000 0000, daily 8am–8pm."
    ),
    "tl": (
        "Hindi ko po naintindihan. Ililipat ko kayo sa isang ahente — isang tunay na tao — "
        "para mas matulungan kayo. Pwede rin po kayong mag-email sa hello@sariwa.ph o tumawag sa 0917 000 0000, 8am–8pm araw-araw."
    ),
}


def _sanitize_like(value: str) -> str:
    return value.replace("\\", "").replace("%", "").replace("_", "").strip()


def _tokens(message: str) -> list[str]:
    return [token for token in re.findall(r"[a-z0-9]+", message) if len(token) >= 3 and token not in STOPWORDS]


def _looks_tagalog(message: str, tokens: list[str]) -> bool:
    words = set(re.findall(r"[a-z0-9]+", message))
    return bool(words & TAGALOG_HINTS) or bool(set(tokens) & TAGALOG_HINTS)


def _reply_language(preferred: str | None, message: str, tokens: list[str], keyword_langs: list[str]) -> str:
    if preferred == "tl" or _looks_tagalog(message, tokens):
        return "tl"
    if "tl" in keyword_langs and "en" not in keyword_langs:
        return "tl"
    return "en"


def _pack(faq: FaqEntry, language: str, matched: bool = True, handover: bool = False) -> ChatAskOut:
    if language == "tl":
        reply = faq.answer_tl
        label = faq.link_label_tl
    else:
        reply = faq.answer_en
        label = faq.link_label_en
    link = None
    if faq.link_url and label:
        link = ChatLinkOut(url=faq.link_url, label=label)
    return ChatAskOut(
        reply=reply,
        matched=matched,
        language=language,
        handover=handover,
        show_options=faq.show_options,
        slug=faq.slug,
        link=link,
    )


@router.get("/options", response_model=list[ChatOptionOut])
def chat_options(language: str = "en", db: Session = Depends(get_db)):
    rows = (
        db.query(FaqEntry)
        .filter(FaqEntry.is_quick_action.is_(True))
        .order_by(FaqEntry.sort_order)
        .all()
    )
    use_tl = language == "tl"
    return [
        ChatOptionOut(
            slug=row.slug,
            icon=row.icon,
            label=row.question_tl if use_tl else row.question_en,
        )
        for row in rows
    ]


@router.post("/ask", response_model=ChatAskOut)
def ask(payload: ChatAskIn, db: Session = Depends(get_db)):
    raw = payload.message.strip()
    safe = _sanitize_like(raw.lower())
    tokens = _tokens(safe)
    preferred = (payload.language or "").lower() or None

    if payload.intent:
        faq = db.query(FaqEntry).filter(FaqEntry.slug == payload.intent).first()
        if faq:
            language = "tl" if preferred == "tl" or _looks_tagalog(safe, tokens) else "en"
            return _pack(faq, language)

    if safe.rstrip("!.?") in GREETINGS:
        faq = db.query(FaqEntry).filter(FaqEntry.slug == "greeting").first()
        if faq:
            language = "tl" if preferred == "tl" or safe.startswith("k") else "en"
            return _pack(faq, language)

    # Contains/LIKE must be dialect-agnostic: MySQL CONCAT() is not available on SQLite.
    like_filters = [literal(safe).contains(FaqKeyword.keyword)]
    for token in tokens:
        like_filters.append(FaqKeyword.keyword.like(f"%{token}%"))

    matches = (
        db.query(FaqKeyword)
        .options(joinedload(FaqKeyword.faq))
        .filter(or_(*like_filters))
        .all()
        if safe
        else []
    )

    scores: dict[int, list[int]] = defaultdict(lambda: [0, 0])
    langs: dict[int, list[str]] = defaultdict(list)
    faqs: dict[int, FaqEntry] = {}
    for row in matches:
        scores[row.faq_id][0] += 1
        scores[row.faq_id][1] = max(scores[row.faq_id][1], len(row.keyword or ""))
        langs[row.faq_id].append(row.language)
        faqs[row.faq_id] = row.faq

    if not scores:
        language = "tl" if preferred == "tl" or _looks_tagalog(safe, tokens) else "en"
        return ChatAskOut(
            reply=HANDOVER[language],
            matched=False,
            language=language,
            handover=True,
            show_options=False,
        )

    winner_id = max(scores, key=lambda faq_id: (scores[faq_id][0], scores[faq_id][1]))
    language = _reply_language(preferred, safe, tokens, langs[winner_id])
    return _pack(faqs[winner_id], language)
