import time
import json
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple, Any


@dataclass
class FxMemoryEntry:
    """
    Structured record representing a single FX pricing session for a given product and region.
    Stores full agent outputs together with meta-information and evaluation score.
    """
    
    created_at_ts: float
    product_name: str
    region: str
    reporting_currency: str
    manager_notes: str
    market_research_json: str
    competitive_pricing_json: str
    fx_impact_json: str
    margin_scenarios_json: str
    decision_brief_text: str
    structured_summary_json: str
    evaluation_json: str
    compacted_summary: Optional[str] = None
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    scenario_label: Optional[str] = None
    evaluation_overall_score: Optional[float] = None


class FxMemoryService:
    """
    In-memory store for FX pricing sessions, with consolidation and aggregate metrics
    per (product_name, region) key.
    """

    def __init__(self, max_sessions_per_key: int = 10):
        """
        Initialize the memory service with a maximum number of stored sessions per key.
        Older sessions beyond this limit are truncated.
        """
        self.max_sessions_per_key = max_sessions_per_key
        self._store: Dict[Tuple[str, str], List[FxMemoryEntry]] = {}
        self._consolidated: Dict[Tuple[str, str], str] = {}
        self._aggregate_metrics: Dict[Tuple[str, str], Dict[str, Any]] = {}

    def _key(self, product_name: str, region: str) -> Tuple[str, str]:
        """
        Build a normalized key (product_name, region) used to index all memory structures.
        """
        return (product_name.strip().lower(), region.strip().lower())

    @staticmethod
    def _safe_parse_json(value: Any) -> Optional[Dict[str, Any]]:
        """
        Safely parse a JSON-like value into a dict.
        Returns None if parsing fails or the result is not a dict.
        """
        if value is None:
            return None
        if isinstance(value, dict):
            return value
        if not isinstance(value, str):
            return None
        if not value.strip():
            return None
        try:
            obj = json.loads(value)
        except Exception:
            return None
        return obj if isinstance(obj, dict) else None

    def _update_aggregate_metrics(self, key: Tuple[str, str]) -> None:
        """
        Recompute aggregate metrics (session count, average scores and prices)
        for a given (product, region) key based on the current stored entries.
        """
        entries = self._store.get(key, [])
        if not entries:
            self._aggregate_metrics[key] = {
                "session_count": 0,
                "avg_evaluation_overall_score": None,
                "avg_recommended_price": None,
                "avg_target_margin_pct": None,
                "first_session_ts": None,
                "last_session_ts": None,
            }
            return

        session_count = len(entries)
        eval_scores: List[float] = []
        prices: List[float] = []
        margins: List[float] = []
        timestamps: List[float] = []

        for e in entries:
            if isinstance(e.evaluation_overall_score, (int, float)):
                eval_scores.append(float(e.evaluation_overall_score))

            struct_obj = self._safe_parse_json(e.structured_summary_json)
            if struct_obj:
                rp = struct_obj.get("recommended_price")
                tm = struct_obj.get("target_margin_pct")
                if isinstance(rp, (int, float)):
                    prices.append(float(rp))
                if isinstance(tm, (int, float)):
                    margins.append(float(tm))

            if isinstance(e.created_at_ts, (int, float)):
                timestamps.append(float(e.created_at_ts))

        avg_eval = sum(eval_scores) / len(eval_scores) if eval_scores else None
        avg_price = sum(prices) / len(prices) if prices else None
        avg_margin = sum(margins) / len(margins) if margins else None
        first_ts = min(timestamps) if timestamps else None
        last_ts = max(timestamps) if timestamps else None

        self._aggregate_metrics[key] = {
            "session_count": session_count,
            "avg_evaluation_overall_score": avg_eval,
            "avg_recommended_price": avg_price,
            "avg_target_margin_pct": avg_margin,
            "first_session_ts": first_ts,
            "last_session_ts": last_ts,
        }

    def add_session_to_memory(
        self,
        product_name: str,
        region: str,
        reporting_currency: str,
        manager_notes: str,
        market_research_json: str,
        competitive_pricing_json: str,
        fx_impact_json: str,
        margin_scenarios_json: str,
        decision_brief_text: str,
        structured_summary_json: str,
        evaluation_json: str,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        scenario_label: Optional[str] = None,
        evaluation_overall_score: Optional[float] = None,
    ) -> FxMemoryEntry:
        """
        Insert a new FX pricing session into memory for a given product and region.
        Also updates aggregate metrics for this key.
        """
        
        key = self._key(product_name, region)

        if evaluation_overall_score is None and evaluation_json:
            eval_obj = self._safe_parse_json(evaluation_json)
            if eval_obj is not None:
                raw_score = eval_obj.get("overall_score")
                if isinstance(raw_score, (int, float)):
                    evaluation_overall_score = float(raw_score)

        entry = FxMemoryEntry(
            created_at_ts=time.time(),
            product_name=product_name,
            region=region,
            reporting_currency=reporting_currency,
            manager_notes=manager_notes,
            market_research_json=market_research_json,
            competitive_pricing_json=competitive_pricing_json,
            fx_impact_json=fx_impact_json,
            margin_scenarios_json=margin_scenarios_json,
            decision_brief_text=decision_brief_text,
            structured_summary_json=structured_summary_json,
            evaluation_json=evaluation_json,
            session_id=session_id,
            user_id=user_id,
            scenario_label=scenario_label,
            evaluation_overall_score=evaluation_overall_score,
        )

        if key not in self._store:
            self._store[key] = []
        self._store[key].insert(0, entry)
        if len(self._store[key]) > self.max_sessions_per_key:
            self._store[key] = self._store[key][: self.max_sessions_per_key]

        self._update_aggregate_metrics(key)
        return entry

    def load_last_session(self, product_name: str, region: str) -> Optional[FxMemoryEntry]:
        """
        Return the most recent FXMemoryEntry for the given product and region,
        or None if no sessions are stored.
        """
        key = self._key(product_name, region)
        entries = self._store.get(key, [])
        if not entries:
            return None
        return entries[0]

    def search_memory(self, product_name: str, region: str, limit: int = 10) -> List[FxMemoryEntry]:
        """
        Return up to `limit` recent sessions for the given product and region,
        ordered from newest to oldest.
        """
        key = self._key(product_name, region)
        entries = self._store.get(key, [])
        return entries[:limit]

    def consolidate_recent_sessions(
        self,
        product_name: str,
        region: str,
        max_sessions: int = 5,
        max_chars_per_note: int = 160,
    ) -> str:
        """
        Build a compact, human-readable summary string describing recent sessions
        for the given product and region, and cache it as consolidated memory.
        """
        
        entries = self.search_memory(product_name=product_name, region=region, limit=max_sessions)
        key = self._key(product_name, region)
        if not entries:
            summary = (
                f"No stored FX sessions yet for product='{product_name}' in region='{region}'."
            )
            self._consolidated[key] = summary
            return summary

        lines: List[str] = []
        lines.append(
            f"FX memory summary for product='{product_name}' in region='{region}' "
            f"(last {len(entries)} sessions, max {self.max_sessions_per_key} stored):"
        )
        for idx, e in enumerate(entries, start=1):
            dt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(e.created_at_ts))
            notes = e.manager_notes.strip().replace("\n", " ")
            if len(notes) > max_chars_per_note:
                notes = notes[: max_chars_per_note].rstrip() + "..."
            line = (
                f"- #{idx} at {dt}, price decision context in {e.reporting_currency}, "
                f"manager_notes='{notes}'"
            )
            lines.append(line)

        summary = "\n".join(lines)
        self._consolidated[key] = summary

        if entries:
            entries[0].compacted_summary = summary

        return summary

    def get_consolidated_memory(self, product_name: str, region: str) -> Optional[str]:
        """
        Return the last computed consolidated memory summary for the given key,
        or None if consolidation has not been run yet.
        """
        key = self._key(product_name, region)
        return self._consolidated.get(key)

    def get_session_count(self, product_name: str, region: str) -> int:
        """
        Return the number of stored sessions for the given product and region.
        """
        key = self._key(product_name, region)
        entries = self._store.get(key, [])
        return len(entries)

    def get_aggregate_metrics(self, product_name: str, region: str) -> Optional[Dict[str, Any]]:
        """
        Return aggregate metrics (session_count, averages, timestamps)
        for the given product and region, if available.
        """
        key = self._key(product_name, region)
        return self._aggregate_metrics.get(key)

    def get_all_keys(self) -> List[Tuple[str, str]]:
        """
        Return a list of all (product_name, region) keys currently stored in memory.
        """
        return list(self._store.keys())

    def export_memory_snapshot(
        self,
        product_name: Optional[str] = None,
        region: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Export a snapshot of the memory store as a nested dict, optionally
        filtered to a single (product, region) pair.
        """
        
        snapshot: Dict[str, Any] = {}

        if product_name is not None and region is not None:
            keys = [self._key(product_name, region)]
        else:
            keys = list(self._store.keys())

        for key in keys:
            entries = self._store.get(key, [])
            label = f"{key[0]}|{key[1]}"
            snapshot[label] = [asdict(e) for e in entries]

        return snapshot

    def prune_sessions_older_than(self, age_seconds: float) -> int:
        """
        Remove all sessions older than the given age in seconds.
        Returns the number of deleted sessions and updates metrics accordingly.
        """
        cutoff_ts = time.time() - age_seconds
        removed = 0
        keys = list(self._store.keys())

        for key in keys:
            entries = self._store.get(key, [])
            new_entries = [e for e in entries if e.created_at_ts >= cutoff_ts]
            removed += len(entries) - len(new_entries)
            if new_entries:
                self._store[key] = new_entries
                self._update_aggregate_metrics(key)
            else:
                self._store.pop(key, None)
                self._consolidated.pop(key, None)
                self._aggregate_metrics.pop(key, None)

        return removed


FX_MEMORY = FxMemoryService(max_sessions_per_key=10)

print("✔️ FX Memory with consolidation and aggregate metrics has been installed!")
