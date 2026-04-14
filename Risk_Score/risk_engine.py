from __future__ import annotations

import json
import os
import re
import tempfile
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote

import requests
from PIL import Image, ImageOps

try:
    import pytesseract
except ImportError:  # pragma: no cover - handled at runtime in the UI
    pytesseract = None


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
PROFILE_DIR = DATA_DIR / "profiles"
SCAN_DIR = DATA_DIR / "ingredient_scans"
DEFAULT_SAMPLE_IMAGE = PROJECT_ROOT / "sample2.jpg"


CANONICAL_ALIASES = {
    "aqua": "water",
    "water": "water",
    "parfum": "fragrance",
    "fragrance": "fragrance",
    "acetaminophen": "acetaminophen",
    "paracetamol": "acetaminophen",
    "glycine soja": "soy",
    "soybean": "soy",
    "soy": "soy",
    "wheat": "wheat",
    "lactose": "milk",
    "casein": "milk",
    "milk": "milk",
    "almond": "tree nut",
    "walnut": "tree nut",
    "cashew": "tree nut",
    "pecan": "tree nut",
    "hazelnut": "tree nut",
    "pistachio": "tree nut",
    "shrimp": "shellfish",
    "crab": "shellfish",
    "lobster": "shellfish",
    "shellfish": "shellfish",
    "egg": "egg",
    "peanut": "peanut",
    "gluten": "gluten",
    "lanolin": "lanolin",
    "peppermint": "peppermint",
}

ALLERGEN_GROUPS = {
    "soy": ["soy", "soybean", "glycine soja"],
    "wheat": ["wheat", "gluten"],
    "milk": ["milk", "lactose", "casein"],
    "egg": ["egg", "albumin"],
    "peanut": ["peanut"],
    "tree nut": ["tree nut", "almond", "walnut", "cashew", "pecan", "hazelnut", "pistachio"],
    "shellfish": ["shellfish", "shrimp", "crab", "lobster"],
    "lanolin": ["lanolin"],
    "peppermint": ["peppermint", "mentha piperita"],
}

YELLOW_FLAG_RULES = {
    "fragrance": "Fragrance can irritate people with sensitive skin or scent sensitivity.",
    "peppermint": "Peppermint can feel harsh for some sensitive skin types.",
    "potassium sorbate": "Potassium sorbate is usually safe, but it can be irritating for some users.",
    "sodium benzoate": "Sodium benzoate is a preservative worth flagging for sensitive users.",
    "citric acid": "Citric acid can sting already irritated skin.",
}

INGREDIENT_STOP_MARKERS = [
    "certified organic ingredient",
    "fair trade ingredient",
    "some ingredients may vary",
    "distributed by",
    "warning",
    "directions",
]

TESSERACT_CANDIDATES = [
    os.getenv("TESSERACT_CMD", "").strip(),
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    "/opt/homebrew/bin/tesseract",
    "/usr/bin/tesseract",
]


@dataclass
class StorageConfig:
    backend: str
    supabase_url: str = ""
    supabase_key: str = ""
    supabase_table: str = "user_profiles"


@dataclass
class AuthSession:
    access_token: str
    refresh_token: str
    user_id: str
    email: str


def ensure_directories() -> None:
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    SCAN_DIR.mkdir(parents=True, exist_ok=True)


def load_local_env() -> None:
    for candidate in (PROJECT_ROOT / ".env", PROJECT_ROOT / "blood-report-ai" / ".env"):
        if not candidate.exists():
            continue
        for raw_line in candidate.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def configure_tesseract() -> None:
    if pytesseract is None:
        return
    for candidate in TESSERACT_CANDIDATES:
        if candidate and Path(candidate).exists():
            pytesseract.pytesseract.tesseract_cmd = candidate
            return


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    compact = re.sub(r"[^a-zA-Z0-9]+", "-", normalized).strip("-").lower()
    return compact or f"profile-{datetime.now().strftime('%Y%m%d%H%M%S')}"


def normalize_for_matching(value: str) -> str:
    lowered = value.lower()
    lowered = re.sub(r"[\(\)\[\]\{\}/]", " ", lowered)
    lowered = re.sub(r"[^a-z0-9+\-\s]", " ", lowered)
    lowered = re.sub(r"\s+", " ", lowered).strip()
    return lowered


def canonicalize_label(value: str) -> str:
    simplified = normalize_for_matching(value)
    for alias, canonical in sorted(CANONICAL_ALIASES.items(), key=lambda item: len(item[0]), reverse=True):
        if alias in simplified:
            return canonical
    return simplified


def split_user_entries(value: str) -> list[str]:
    if not value.strip():
        return []
    entries = re.split(r"[,;\n]+", value)
    return [entry.strip() for entry in entries if entry.strip()]


def preprocess_image(image: Image.Image) -> Image.Image:
    grayscale = ImageOps.grayscale(image)
    high_contrast = ImageOps.autocontrast(grayscale)
    width, height = high_contrast.size
    scale = 2 if max(width, height) < 2000 else 1
    if scale > 1:
        high_contrast = high_contrast.resize((width * scale, height * scale))
    return high_contrast


def extract_text_from_image(image_source: str | Path | bytes) -> str:
    if pytesseract is None:
        raise RuntimeError("pytesseract is not installed in the project environment.")

    configure_tesseract()

    if isinstance(image_source, (str, Path)):
        image = Image.open(image_source)
    else:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
            temp_file.write(image_source)
            temp_path = Path(temp_file.name)
        try:
            image = Image.open(temp_path).copy()
        finally:
            temp_path.unlink(missing_ok=True)

    candidates = [image, preprocess_image(image)]
    outputs: list[str] = []
    for candidate in candidates:
        for config in ("--psm 6", "--psm 11", "--psm 4"):
            try:
                outputs.append(pytesseract.image_to_string(candidate, config=config))
            except Exception:
                continue

    best = max(outputs, key=lambda item: len(re.sub(r"\W+", "", item)), default="")
    if not best.strip():
        raise RuntimeError("OCR did not return readable text from the image.")
    return best


def extract_ingredient_block(raw_text: str) -> str:
    cleaned = unicodedata.normalize("NFKC", raw_text).replace("\r", "")
    header_match = re.search(r"(ingredients?|active ingredients?)\s*[:\-]\s*", cleaned, flags=re.IGNORECASE)
    block = cleaned[header_match.end():] if header_match else cleaned

    stop_positions = [block.lower().find(marker) for marker in INGREDIENT_STOP_MARKERS if marker in block.lower()]
    valid_stops = [position for position in stop_positions if position >= 0]
    if valid_stops:
        block = block[: min(valid_stops)]

    block = re.sub(r"\s+\n", "\n", block)
    block = re.sub(r"\n+", "\n", block).strip(" :\n\t.")
    return block


def split_ingredients(block: str) -> list[str]:
    if not block.strip():
        return []

    normalized_block = re.sub(r"\n+", "\n", block)
    newline_delimited = "," not in normalized_block and ";" not in normalized_block
    if not newline_delimited:
        normalized_block = re.sub(r"\s*\n\s*", " ", normalized_block)

    parts: list[str] = []
    current: list[str] = []
    depth = 0

    for char in normalized_block:
        if char == "(":
            depth += 1
        elif char == ")" and depth > 0:
            depth -= 1

        is_delimiter = char in ",;" or (newline_delimited and char == "\n")
        if is_delimiter and depth == 0:
            item = "".join(current).strip()
            if item:
                parts.append(item)
            current = []
            continue

        current.append(" " if char == "\n" else char)

    tail = "".join(current).strip()
    if tail:
        parts.append(tail)

    cleaned_parts: list[str] = []
    for part in parts:
        ingredient = re.sub(r"\s+", " ", part).strip()
        ingredient = re.sub(r"\*+[A-Za-z]*$", "", ingredient).strip(" .-")
        if not ingredient:
            continue
        lowered = ingredient.lower()
        if any(marker in lowered for marker in INGREDIENT_STOP_MARKERS):
            continue
        cleaned_parts.append(ingredient)

    seen: set[str] = set()
    unique_parts: list[str] = []
    for item in cleaned_parts:
        key = item.lower()
        if key in seen:
            continue
        seen.add(key)
        unique_parts.append(item)
    return unique_parts


def build_ingredient_rows(ingredients: list[str]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for ingredient in ingredients:
        canonical = canonicalize_label(ingredient)
        rows.append(
            {
                "ingredient": ingredient,
                "normalized": canonical or normalize_for_matching(ingredient),
            }
        )
    return rows


def detect_allergy_flags(ingredient_rows: list[dict[str, str]], allergies: list[str]) -> list[dict[str, str]]:
    flags: list[dict[str, str]] = []
    for allergy in allergies:
        allergy_key = canonicalize_label(allergy)
        aliases = ALLERGEN_GROUPS.get(allergy_key, [allergy_key])
        for row in ingredient_rows:
            haystack = f"{normalize_for_matching(row['ingredient'])} {row['normalized']}"
            if any(alias in haystack for alias in aliases):
                flags.append(
                    {
                        "allergy": allergy,
                        "ingredient": row["ingredient"],
                        "reason": f"Matched user allergy '{allergy}' against ingredient '{row['ingredient']}'.",
                    }
                )
    return flags


def detect_yellow_flags(ingredient_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    flags: list[dict[str, str]] = []
    for row in ingredient_rows:
        haystack = f"{normalize_for_matching(row['ingredient'])} {row['normalized']}"
        for keyword, explanation in YELLOW_FLAG_RULES.items():
            if keyword in haystack:
                flags.append(
                    {
                        "ingredient": row["ingredient"],
                        "reason": explanation,
                    }
                )
                break
    return flags


def score_risk(allergy_flags: list[dict[str, str]], yellow_flags: list[dict[str, str]]) -> dict[str, str]:
    if allergy_flags:
        return {
            "level": "Red",
            "summary": "Potential allergen or severe issue detected.",
            "color": "#b42318",
        }
    if yellow_flags:
        return {
            "level": "Yellow",
            "summary": "Potential sensitivity or caution ingredient found.",
            "color": "#b54708",
        }
    return {
        "level": "Green",
        "summary": "No direct allergy match or warning ingredient was detected.",
        "color": "#027a48",
    }


def analyze_ingredient_image(image_source: str | Path | bytes, allergies: str = "") -> dict[str, Any]:
    raw_text = extract_text_from_image(image_source)
    ingredient_block = extract_ingredient_block(raw_text)
    ingredients = split_ingredients(ingredient_block)
    ingredient_rows = build_ingredient_rows(ingredients)
    allergy_entries = split_user_entries(allergies)
    allergy_flags = detect_allergy_flags(ingredient_rows, allergy_entries)
    yellow_flags = detect_yellow_flags(ingredient_rows)
    risk = score_risk(allergy_flags, yellow_flags)

    return {
        "created_at": utc_now_iso(),
        "raw_text": raw_text,
        "ingredient_block": ingredient_block,
        "ingredients": ingredient_rows,
        "allergies": allergy_entries,
        "allergy_flags": allergy_flags,
        "yellow_flags": yellow_flags,
        "risk": risk,
    }


def export_scan_result(result: dict[str, Any], source_name: str) -> Path:
    ensure_directories()
    filename = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{slugify(Path(source_name).stem)}.json"
    export_path = SCAN_DIR / filename
    export_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return export_path


def build_profile_payload(
    name: str,
    age: int,
    sex: str,
    conditions: str,
    allergies: str,
    notes: str,
    user_id: str = "",
) -> dict[str, Any]:
    profile_id = user_id.strip() or slugify(name)
    return {
        "id": profile_id,
        "name": name.strip(),
        "age": age,
        "sex": sex,
        "existing_conditions": split_user_entries(conditions),
        "allergies": split_user_entries(allergies),
        "notes": notes.strip(),
        "updated_at": utc_now_iso(),
    }


def save_profile_locally(profile: dict[str, Any]) -> Path:
    ensure_directories()
    file_path = PROFILE_DIR / f"{profile['id']}.json"
    file_path.write_text(json.dumps(profile, indent=2), encoding="utf-8")
    return file_path


def save_profile_to_supabase(profile: dict[str, Any], config: StorageConfig) -> None:
    if not config.supabase_url or not config.supabase_key:
        raise ValueError("Supabase URL and anon key are required.")

    url = f"{config.supabase_url.rstrip('/')}/rest/v1/{config.supabase_table}?on_conflict=id"
    response = requests.post(
        url,
        headers={
            "apikey": config.supabase_key,
            "Authorization": f"Bearer {config.supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates,return=representation",
        },
        json=[profile],
        timeout=20,
    )
    response.raise_for_status()


def save_profile(profile: dict[str, Any], config: StorageConfig, auth_session: AuthSession | None = None) -> tuple[str, Path]:
    local_backup = save_profile_locally(profile)

    backend = config.backend.lower()
    if backend == "local json":
        return ("Saved locally.", local_backup)
    if backend == "supabase":
        save_profile_to_supabase_as_user(profile, config, auth_session)
        return ("Saved to Supabase and backed up locally.", local_backup)
    raise ValueError(f"Unsupported backend: {config.backend}")


def list_saved_profiles() -> list[Path]:
    ensure_directories()
    return sorted(PROFILE_DIR.glob("*.json"), reverse=True)


def build_supabase_headers(config: StorageConfig, bearer_token: str | None = None) -> dict[str, str]:
    if not config.supabase_key:
        raise ValueError("Supabase anon key is required.")

    token = bearer_token or config.supabase_key
    return {
        "apikey": config.supabase_key,
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


def parse_auth_session(payload: dict[str, Any]) -> AuthSession | None:
    access_token = payload.get("access_token") or payload.get("session", {}).get("access_token")
    refresh_token = payload.get("refresh_token") or payload.get("session", {}).get("refresh_token")
    user = payload.get("user") or payload.get("session", {}).get("user") or {}
    user_id = user.get("id", "")
    email = user.get("email", "")
    if not access_token or not user_id:
        return None
    return AuthSession(
        access_token=access_token,
        refresh_token=refresh_token or "",
        user_id=user_id,
        email=email,
    )


def sign_up_with_supabase(email: str, password: str, config: StorageConfig) -> tuple[AuthSession | None, str]:
    url = f"{config.supabase_url.rstrip('/')}/auth/v1/signup"
    response = requests.post(
        url,
        headers=build_supabase_headers(config),
        json={"email": email, "password": password},
        timeout=20,
    )
    data = response.json()
    if response.status_code >= 400:
        raise ValueError(data.get("msg") or data.get("message") or "Sign up failed.")

    session = parse_auth_session(data)
    if session is None:
        return None, "Account created. Check your email to confirm your account, then sign in."
    return session, "Account created and signed in."


def sign_in_with_supabase(email: str, password: str, config: StorageConfig) -> AuthSession:
    url = f"{config.supabase_url.rstrip('/')}/auth/v1/token?grant_type=password"
    response = requests.post(
        url,
        headers=build_supabase_headers(config),
        json={"email": email, "password": password},
        timeout=20,
    )
    data = response.json()
    if response.status_code >= 400:
        raise ValueError(data.get("msg") or data.get("message") or "Sign in failed.")

    session = parse_auth_session(data)
    if session is None:
        raise ValueError("Sign in failed.")
    return session


def sign_out_from_supabase(auth_session: AuthSession, config: StorageConfig) -> None:
    url = f"{config.supabase_url.rstrip('/')}/auth/v1/logout"
    response = requests.post(
        url,
        headers=build_supabase_headers(config, auth_session.access_token),
        timeout=20,
    )
    response.raise_for_status()


def fetch_profile_from_supabase(profile_id: str, config: StorageConfig, auth_session: AuthSession) -> dict[str, Any] | None:
    encoded_id = quote(profile_id, safe="")
    url = f"{config.supabase_url.rstrip('/')}/rest/v1/{config.supabase_table}?id=eq.{encoded_id}&select=*"
    response = requests.get(
        url,
        headers=build_supabase_headers(config, auth_session.access_token),
        timeout=20,
    )
    response.raise_for_status()
    rows = response.json()
    return rows[0] if rows else None


def save_profile_to_supabase_as_user(profile: dict[str, Any], config: StorageConfig, auth_session: AuthSession | None) -> None:
    if auth_session is None:
        save_profile_to_supabase(profile, config)
        return

    url = f"{config.supabase_url.rstrip('/')}/rest/v1/{config.supabase_table}?on_conflict=id"
    response = requests.post(
        url,
        headers={
            **build_supabase_headers(config, auth_session.access_token),
            "Prefer": "resolution=merge-duplicates,return=representation",
        },
        json=[profile],
        timeout=20,
    )
    response.raise_for_status()


load_local_env()
configure_tesseract()
