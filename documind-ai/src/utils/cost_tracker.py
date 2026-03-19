"""
DocuMind AI - Cost Tracker
Tracks and reports API costs across users, documents, and sessions.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
import json


@dataclass
class CostEntry:
    """Represents a single cost entry."""
    amount: float
    model: str
    operation: str
    document_id: Optional[str] = None
    user_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    tokens_in: int = 0
    tokens_out: int = 0


@dataclass
class CostBudget:
    """Budget configuration for cost tracking."""
    daily_limit: float = 100.0
    monthly_limit: float = 2000.0
    per_document_limit: float = 10.0
    alert_threshold_percent: float = 80.0


class CostTracker:
    """Track and manage API costs across the application."""
    
    def __init__(self, budget: Optional[CostBudget] = None):
        self.budget = budget or CostBudget()
        self.cost_entries: List[CostEntry] = []
        self.daily_costs: Dict[str, float] = defaultdict(float)
        self.monthly_costs: Dict[str, float] = defaultdict(float)
        self.document_costs: Dict[str, float] = defaultdict(float)
        self.user_costs: Dict[str, float] = defaultdict(float)
    
    def add_cost(
        self,
        amount: float,
        model: str,
        operation: str,
        document_id: Optional[str] = None,
        user_id: Optional[str] = None,
        tokens_in: int = 0,
        tokens_out: int = 0,
    ) -> CostEntry:
        """Add a new cost entry."""
        entry = CostEntry(
            amount=amount,
            model=model,
            operation=operation,
            document_id=document_id,
            user_id=user_id,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
        )
        
        self.cost_entries.append(entry)
        
        # Update aggregations
        date_key = entry.timestamp.strftime("%Y-%m-%d")
        month_key = entry.timestamp.strftime("%Y-%m")
        
        self.daily_costs[date_key] += amount
        self.monthly_costs[month_key] += amount
        
        if document_id:
            self.document_costs[document_id] += amount
        
        if user_id:
            self.user_costs[user_id] += amount
        
        return entry
    
    def get_daily_cost(self, date: Optional[datetime] = None) -> float:
        """Get total cost for a specific date (or today)."""
        if date is None:
            date = datetime.now()
        date_key = date.strftime("%Y-%m-%d")
        return round(self.daily_costs.get(date_key, 0.0), 4)
    
    def get_monthly_cost(self, year: Optional[int] = None, month: Optional[int] = None) -> float:
        """Get total cost for a specific month (or current month)."""
        if year is None or month is None:
            now = datetime.now()
            year = now.year
            month = now.month
        month_key = f"{year}-{month:02d}"
        return round(self.monthly_costs.get(month_key, 0.0), 4)
    
    def get_document_cost(self, document_id: str) -> float:
        """Get total cost for a specific document."""
        return round(self.document_costs.get(document_id, 0.0), 4)
    
    def get_user_cost(self, user_id: str) -> float:
        """Get total cost for a specific user."""
        return round(self.user_costs.get(user_id, 0.0), 4)
    
    def check_budget_alerts(self) -> List[str]:
        """Check if any budget thresholds are exceeded. Returns list of alerts."""
        alerts = []
        
        # Check daily budget
        today_cost = self.get_daily_cost()
        daily_percent = (today_cost / self.budget.daily_limit) * 100
        if daily_percent >= self.budget.alert_threshold_percent:
            alerts.append(
                f"Daily cost alert: ${today_cost:.2f} / ${self.budget.daily_limit:.2f} "
                f"({daily_percent:.1f}%)"
            )
        if today_cost > self.budget.daily_limit:
            alerts.append(
                f"Daily budget exceeded: ${today_cost:.2f} > ${self.budget.daily_limit:.2f}"
            )
        
        # Check monthly budget
        monthly_cost = self.get_monthly_cost()
        monthly_percent = (monthly_cost / self.budget.monthly_limit) * 100
        if monthly_percent >= self.budget.alert_threshold_percent:
            alerts.append(
                f"Monthly cost alert: ${monthly_cost:.2f} / ${self.budget.monthly_limit:.2f} "
                f"({monthly_percent:.1f}%)"
            )
        if monthly_cost > self.budget.monthly_limit:
            alerts.append(
                f"Monthly budget exceeded: ${monthly_cost:.2f} > ${self.budget.monthly_limit:.2f}"
            )
        
        return alerts
    
    def get_cost_summary(self) -> Dict:
        """Get comprehensive cost summary."""
        return {
            "today": {
                "cost": self.get_daily_cost(),
                "limit": self.budget.daily_limit,
                "remaining": round(max(0, self.budget.daily_limit - self.get_daily_cost()), 4),
                "percent_used": round(
                    (self.get_daily_cost() / self.budget.daily_limit) * 100, 2
                ),
            },
            "this_month": {
                "cost": self.get_monthly_cost(),
                "limit": self.budget.monthly_limit,
                "remaining": round(max(0, self.budget.monthly_limit - self.get_monthly_cost()), 4),
                "percent_used": round(
                    (self.get_monthly_cost() / self.budget.monthly_limit) * 100, 2
                ),
            },
            "total_all_time": round(sum(e.amount for e in self.cost_entries), 4),
            "total_operations": len(self.cost_entries),
            "alerts": self.check_budget_alerts(),
        }
    
    def get_top_documents(self, limit: int = 10) -> List[Dict]:
        """Get top N most expensive documents."""
        sorted_docs = sorted(
            self.document_costs.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
        
        return [
            {"document_id": doc_id, "cost": round(cost, 4)}
            for doc_id, cost in sorted_docs
        ]
    
    def get_top_users(self, limit: int = 10) -> List[Dict]:
        """Get top N highest spending users."""
        sorted_users = sorted(
            self.user_costs.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
        
        return [
            {"user_id": user_id, "cost": round(cost, 4)}
            for user_id, cost in sorted_users
        ]
    
    def get_cost_by_model(self) -> Dict[str, float]:
        """Get total cost broken down by model."""
        model_costs = defaultdict(float)
        for entry in self.cost_entries:
            model_costs[entry.model] += entry.amount
        
        return {model: round(cost, 4) for model, cost in model_costs.items()}
    
    def get_cost_by_operation(self) -> Dict[str, float]:
        """Get total cost broken down by operation type."""
        operation_costs = defaultdict(float)
        for entry in self.cost_entries:
            operation_costs[entry.operation] += entry.amount
        
        return {op: round(cost, 4) for op, cost in operation_costs.items()}
    
    def export_to_json(self, filepath: str) -> None:
        """Export cost data to JSON file."""
        data = {
            "summary": self.get_cost_summary(),
            "entries": [
                {
                    "amount": e.amount,
                    "model": e.model,
                    "operation": e.operation,
                    "document_id": e.document_id,
                    "user_id": e.user_id,
                    "timestamp": e.timestamp.isoformat(),
                    "tokens_in": e.tokens_in,
                    "tokens_out": e.tokens_out,
                }
                for e in self.cost_entries
            ],
            "by_model": self.get_cost_by_model(),
            "by_operation": self.get_cost_by_operation(),
            "top_documents": self.get_top_documents(),
            "top_users": self.get_top_users(),
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def reset_daily(self) -> None:
        """Reset daily cost tracking (for testing)."""
        today = datetime.now().strftime("%Y-%m-%d")
        if today in self.daily_costs:
            del self.daily_costs[today]
    
    def clear_all(self) -> None:
        """Clear all cost tracking data."""
        self.cost_entries = []
        self.daily_costs.clear()
        self.monthly_costs.clear()
        self.document_costs.clear()
        self.user_costs.clear()


# Singleton instance
_cost_tracker: Optional[CostTracker] = None


def get_cost_tracker(budget: Optional[CostBudget] = None) -> CostTracker:
    """Get the global cost tracker instance."""
    global _cost_tracker
    if _cost_tracker is None:
        _cost_tracker = CostTracker(budget)
    return _cost_tracker
