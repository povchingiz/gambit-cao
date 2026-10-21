"""cao_laya_router.py — Laya System-1 Intent, Model & Risk Routing Engine.

Acts as the fast, non-autoregressive decision reflex for CAO OneFleet:
1. Intelligent Task & Model Routing: Maps task descriptions directly to the
   optimal worker profile (claude, coder, codex, analyst, qa, copilot) and model,
   preventing "wrong task to wrong CLI agent" errors.
2. Anti-Babysitting Reflex Gate: Evaluates tool calls and commands into risk tiers
   (SAFE auto-approve vs CRITICAL human escalation) to stop permission spam.
"""
import json
import re
import sys
from typing import Any, Dict, List, Optional, Tuple


class LayaRouter:
    """Fast System-1 Decision Classifier for CAO Fleet."""

    # Keywords & intent rules for worker profile routing
    ROUTING_RULES: List[Dict[str, Any]] = [
        {
            "worker": "claude_worker",
            "provider": "claude_code",
            "recommended_model": "claude-3-7-sonnet",
            "category": "Architecture & Deep Reasoning",
            "patterns": [
                r"\b(architect(ure)?|design|contracts?|interfaces?|spec(ification)?)\b",
                r"\b(ddd|domain[- ]driven|refactor(ing)?|boundary|boundaries)\b",
                r"\b(hard reasoning|complex algorithm|system breakdown|threat model)\b",
                r"\b(abstract class|protocol definition|data model design)\b",
            ],
            "weight": 1.5,
        },
        {
            "worker": "codex_worker",
            "provider": "codex",
            "recommended_model": "gpt-4o",
            "category": "Frontend & UI Engineering",
            "patterns": [
                r"\b(react|vue|svelte|nextjs|tailwind|css|scss|html|jsx|tsx)\b",
                r"\b(frontend|ui|ux|component|modal|button|sidebar|layout|page|view)\b",
                r"\b(dom|responsive|styling|flexbox|grid|canvas|webgl)\b",
            ],
            "weight": 1.4,
        },
        {
            "worker": "antigravity_worker",
            "provider": "antigravity_cli",
            "recommended_model": "gemini-3.8-flash-high",
            "category": "QA, Tests & Security Audit",
            "patterns": [
                r"\b(tests?|pytest|unittest|jest|vitest|playwright|cypress)\b",
                r"\b(qa|audit|security review|vulnerabilit(y|ies)|edge cases?)\b",
                r"\b(coverage|assert(ions?)?|verify|verification|stress test)\b",
            ],
            "weight": 1.4,
        },
        {
            "worker": "analyst_worker",
            "provider": "antigravity_cli",
            "recommended_model": "gemini-4-argon",
            "category": "Whole-Repo Analysis & Big Context",
            "patterns": [
                r"\b(where is .* used|dependency map|trace (flow|calls))\b",
                r"\b(cross[- ]file impact|repo[- ]wide|large context|read(ing)? docs)\b",
                r"\b(multimodal|pdf|image analysis|audit codebase|overview)\b",
            ],
            "weight": 1.3,
        },
        {
            "worker": "copilot_worker",
            "provider": "copilot_cli",
            "recommended_model": "copilot-claude-3.5-sonnet",
            "category": "DevOps, CI/CD & Deployments",
            "patterns": [
                r"\b(ci/cd|github actions?|workflows?|docker(file)?|compose)\b",
                r"\b(deploy(ment)?|kubernetes|k8s|helm|terraform|ansible)\b",
                r"\b(pull request|pr|release|build pipeline)\b",
            ],
            "weight": 1.3,
        },
        {
            "worker": "coder_worker",
            "provider": "opencode_cli",
            "recommended_model": "zai-org/GLM-5.3",
            "category": "High-Throughput Bulk Code & Boilerplate",
            "patterns": [
                r"\b(boilerplate|schema|migration|crud|endpoints?|api route)\b",
                r"\b(helpers?|util(ities)?|scaffold(ing)?|implement(ation)?)\b",
                r"\b(sql|postgres|mysql|sqlite|orm|models?|dto|parser)\b",
                r"\b(write code|function|class|fix bug|patch|repetitive)\b",
            ],
            "weight": 1.0,  # Default fallback bucket
        },
    ]

    # Models available on the local bulk endpoint (Nitec / OpenRouter)
    ENDPOINT_MODELS = {
        "fast_bulk": "deepseek-ai/DeepSeek-V4.1-Flash",
        "standard_bulk": "zai-org/GLM-5.3",
        "reasoning_bulk": "deepseek-ai/DeepSeek-V4-Pro",
        "long_context": "moonshotai/Kimi-K3",
    }

    # Anti-Babysitting Reflex Rules
    CRITICAL_PATTERNS = [
        r"rm\s+(-[a-zA-Z]*r[a-zA-Z]*f|--recursive\s+--force)",
        r"git\s+(reset\s+--hard|push\s+--force|clean\s+-fdx)",
        r"(DROP\s+TABLE|DROP\s+DATABASE|TRUNCATE)",
        r"(\.env|LOCAL_API_KEY|id_rsa|private_key|secret)",
        r"chmod\s+777",
    ]

    SAFE_PATTERNS = [
        r"^(ls|cat|head|tail|grep|find|read_file|pwd|wc|echo)\b",
        r"^(git\s+(status|log|diff|branch|show))\b",
        r"^(pytest|python3?\s+-m\s+pytest|npm\s+test|cargo\s+test)\b",
        r"^(uv\s+run\s+pytest|black\s+--check|flake8|mypy)\b",
    ]

    @classmethod
    def route_task(cls, task_text: str, project_context: str = "") -> Dict[str, Any]:
        """Classify task and select the best worker profile and model."""
        combined = f"{task_text} {project_context}".lower()

        scores: Dict[str, float] = {}
        matched_details: Dict[str, List[str]] = {}

        for rule in cls.ROUTING_RULES:
            worker = rule["worker"]
            scores[worker] = 0.0
            matched_details[worker] = []

            for pat in rule["patterns"]:
                matches = re.findall(pat, combined, re.IGNORECASE)
                if matches:
                    weight = rule.get("weight", 1.0)
                    scores[worker] += len(matches) * weight
                    matched_details[worker].append(pat)

        # Pick highest scoring worker; default to coder_worker
        best_worker = "coder_worker"
        max_score = 0.0
        for w, sc in scores.items():
            if sc > max_score:
                max_score = sc
                best_worker = w

        # Find matching rule config
        chosen_rule = next(r for r in cls.ROUTING_RULES if r["worker"] == best_worker)

        # Refine model selection for coder_worker based on prompt characteristics
        model = chosen_rule["recommended_model"]
        if best_worker == "coder_worker":
            if any(w in combined for w in ["complex", "difficult", "hard", "math", "algorithm"]):
                model = cls.ENDPOINT_MODELS["reasoning_bulk"]
            elif any(w in combined for w in ["quick", "fast", "simple", "typo", "tiny"]):
                model = cls.ENDPOINT_MODELS["fast_bulk"]
            elif any(w in combined for w in ["long", "large", "huge", "paper", "entire"]):
                model = cls.ENDPOINT_MODELS["long_context"]
            else:
                model = cls.ENDPOINT_MODELS["standard_bulk"]

        confidence = min(0.99, max(0.55, 0.50 + (max_score * 0.15)))

        return {
            "worker": best_worker,
            "provider": chosen_rule["provider"],
            "model": model,
            "category": chosen_rule["category"],
            "confidence": round(confidence, 2),
            "matched_patterns": matched_details.get(best_worker, []),
            "rationale": (
                f"Selected '{best_worker}' ({chosen_rule['category']}) with model '{model}' "
                f"based on intent signals: {', '.join(matched_details.get(best_worker, [])[:2]) or 'standard task flow'}."
            ),
        }

    @classmethod
    def evaluate_risk(cls, tool_name: str, tool_args: str = "") -> Dict[str, Any]:
        """Anti-Babysitting Reflex: evaluate risk and decide auto-approve vs escalate."""
        target = f"{tool_name} {tool_args}".strip()

        # 1. Critical risk checks (Escalate to human immediately)
        for pat in cls.CRITICAL_PATTERNS:
            if re.search(pat, target, re.IGNORECASE):
                return {
                    "decision": "ESCALATE_TO_HUMAN",
                    "risk_tier": "CRITICAL",
                    "risk_score": 9,
                    "reason": f"Matches critical safety pattern: '{pat}'",
                    "auto_approved": False,
                }

        # 2. Safe read/test checks (Auto-approve with zero prompt)
        for pat in cls.SAFE_PATTERNS:
            if re.search(pat, target, re.IGNORECASE):
                return {
                    "decision": "AUTO_APPROVE",
                    "risk_tier": "SAFE",
                    "risk_score": 1,
                    "reason": f"Safe read/test operation: '{pat}'",
                    "auto_approved": True,
                }

        # 3. Standard workspace modifications
        return {
            "decision": "AUTO_APPROVE_AUTOPILOT",
            "risk_tier": "STANDARD",
            "risk_score": 4,
            "reason": "Standard workspace file/edit operation",
            "auto_approved": True,
        }
