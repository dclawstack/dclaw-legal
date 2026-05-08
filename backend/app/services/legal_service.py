"""AI legal contract review service."""

import httpx

from app.core.config import settings

_TIMEOUT = httpx.Timeout(60.0, connect=10.0)

# Keyword-based fallback analysis
_RISK_PATTERNS = {
    "high": [
        "unlimited liability", "sole discretion", "waive", "indemnify", "hold harmless",
        "no limitation", "perpetual", "irrevocable", "exclusive remedy",
    ],
    "medium": [
        "termination for convenience", "auto-renew", "governing law", "assignment",
        "confidentiality", "non-compete", "non-solicit", "liquidated damages",
    ],
    "low": [
        "notice", "force majeure", "severability", "entire agreement", "waiver",
    ],
}

_CLAUSE_TYPES = {
    "Indemnification": ["indemnif", "hold harmless", "defend"],
    "Limitation of Liability": ["limitation of liability", "cap liability", "liability cap"],
    "Termination": ["termination", "terminate", "expiration", "renewal"],
    "Confidentiality": ["confidential", "non-disclosure", "nda"],
    "Intellectual Property": ["intellectual property", "ip rights", "ownership", "work for hire"],
    "Payment Terms": ["payment", "invoice", "fees", "compensation", "remuneration"],
    "Governing Law": ["governing law", "jurisdiction", "venue", "arbitration"],
    "Non-Compete": ["non-compete", "non-competition", "non-solicit"],
    "Force Majeure": ["force majeure", "act of god", "beyond control"],
    "Warranty": ["warranty", "warranties", "guarantee", "represent"],
}

_RECOMMENDATIONS = {
    "Indemnification": "Clarify indemnification scope and ensure mutual obligations.",
    "Limitation of Liability": "Cap liability at 12 months of fees or contract value.",
    "Termination": "Add 30-day cure period and specify data return obligations.",
    "Confidentiality": "Define confidential information and set survival period.",
    "Intellectual Property": "Ensure IP ownership is clearly assigned per engagement.",
    "Payment Terms": "Include net-30 terms and late payment interest.",
    "Governing Law": "Choose neutral jurisdiction acceptable to both parties.",
    "Non-Compete": "Limit scope to reasonable geography and duration.",
    "Force Majeure": "Include notice requirements and obligation to mitigate.",
    "Warranty": "Limit warranties to material compliance and exclude consequential damages.",
}


async def _call_ollama(prompt: str) -> str | None:
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.post(
                f"{settings.ollama_base_url}/api/generate",
                json={
                    "model": "llama3.1",
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.2, "num_predict": 512},
                },
            )
            resp.raise_for_status()
            return resp.json().get("response", "")
    except Exception:
        return None


async def _call_openrouter(prompt: str) -> str | None:
    if not getattr(settings, "openrouter_api_key", ""):
        return None
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.openrouter_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "meta-llama/llama-3.1-8b-instruct",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2,
                    "max_tokens": 512,
                },
            )
            resp.raise_for_status()
            choices = resp.json().get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content", "")
            return None
    except Exception:
        return None


async def _generate(prompt: str) -> str:
    result = await _call_ollama(prompt)
    if result:
        return result
    result = await _call_openrouter(prompt)
    if result:
        return result
    return ""


def _analyze_contract(text: str) -> tuple[int, list[dict], list[str]]:
    """Keyword-based contract analysis fallback."""
    text_lower = text.lower()
    risk_score = 0
    findings = []
    seen_types = set()

    for risk_level, keywords in _RISK_PATTERNS.items():
        for kw in keywords:
            if kw in text_lower:
                score = {"high": 25, "medium": 10, "low": 3}[risk_level]
                risk_score += score

    for clause_type, keywords in _CLAUSE_TYPES.items():
        for kw in keywords:
            if kw in text_lower:
                if clause_type not in seen_types:
                    seen_types.add(clause_type)
                    risk_level = "medium"
                    for high_kw in _RISK_PATTERNS["high"]:
                        if high_kw in text_lower and any(h in kw for h in ["indemnif", "liability", "waive"]):
                            risk_level = "high"
                    findings.append({
                        "clause_text": f"Detected {clause_type} clause",
                        "clause_type": clause_type,
                        "risk_level": risk_level,
                        "recommendation": _RECOMMENDATIONS.get(clause_type, "Review carefully."),
                    })
                break

    # Deduplicate recommendations
    recommendations = list({f["recommendation"] for f in findings})
    risk_score = min(risk_score, 100)
    return risk_score, findings, recommendations


async def review_contract(contract_text: str) -> dict:
    """Review a contract and return analysis."""
    prompt = (
        "Analyze the following contract text. "
        "Return a JSON object with keys: risk_score (0-100 integer), "
        "key_clauses (list of strings), and recommendations (list of strings).\n\n"
        f"Contract text:\n{contract_text[:4000]}"
    )

    ai_response = await _generate(prompt)

    if ai_response:
        # Try to extract structured data from AI response
        risk_score = 50
        key_clauses = []
        recommendations = []
        try:
            # Simple heuristic extraction
            if "risk_score" in ai_response.lower():
                import re
                match = re.search(r'["\']?risk_score["\']?\s*[:=]\s*(\d+)', ai_response)
                if match:
                    risk_score = int(match.group(1))
        except Exception:
            pass
        key_clauses = [line.strip("-* ") for line in ai_response.splitlines() if line.strip().startswith(("-", "*"))][:5]
        if not key_clauses:
            key_clauses = ["AI analysis completed — see full response for details."]
        recommendations = ["Review AI-generated analysis carefully before making decisions."]
        return {
            "risk_score": min(risk_score, 100),
            "key_clauses": key_clauses,
            "recommendations": recommendations,
        }

    # Fallback to keyword analysis
    risk_score, findings, recommendations = _analyze_contract(contract_text)
    key_clauses = [f"{f['clause_type']} ({f['risk_level']} risk)" for f in findings]
    if not key_clauses:
        key_clauses = ["No specific clause patterns detected."]
    if not recommendations:
        recommendations = ["Consider professional legal review."]

    return {
        "risk_score": risk_score,
        "key_clauses": key_clauses,
        "recommendations": recommendations,
    }
