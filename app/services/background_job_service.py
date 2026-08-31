from sqlalchemy.orm import Session
from datetime import datetime
from app.repositories import AggregationRepository, TenantRepository
from app.services import CostService, QuotaService
from typing import Dict, Any, List
import logging
import time

logger = logging.getLogger(__name__)

class BackgroundJobService:
    @staticmethod
    def run_usage_aggregation(db: Session) -> Dict[str, Any]:
        start_time = time.time()
        results = {
            "status": "success",
            "tenants_processed": 0,
            "errors": [],
            "total_time_ms": 0
        }

        try:
            tenants = TenantRepository.get_all(db)
            if not tenants:
                return {
                    "status": "success",
                    "tenants_processed": 0,
                    "message": "No tenants found",
                    "total_time_ms": 0
                }

            for tenant in tenants:
                try:
                    cost_response = CostService.get_tenant_cost(db, tenant.id)
                    current_usage = QuotaService.get_current_usage(db, tenant.id)

                    agg_data = {
                        "api_calls": cost_response.api_calls,
                        "ai_tokens": current_usage["ai_tokens"],
                        "api_cost_cents": cost_response.api_cost_cents,
                        "token_cost_cents": cost_response.token_breakdown.total_cost_cents,
                        "total_cost_cents": cost_response.total_cost_cents
                    }

                    AggregationRepository.create_or_update(
                        db,
                        tenant.id,
                        cost_response.period,
                        agg_data
                    )

                    results["tenants_processed"] += 1

                except Exception as e:
                    error_msg = f"Error processing tenant {tenant.id}: {str(e)}"
                    logger.error(error_msg)
                    results["errors"].append(error_msg)

            results["total_time_ms"] = round((time.time() - start_time) * 1000, 2)

        except Exception as e:
            results["status"] = "error"
            results["errors"].append(f"Job failed: {str(e)}")
            logger.error(f"Usage aggregation job failed: {str(e)}")

        return results

    @staticmethod
    def run_cleanup_job(db: Session, days_to_keep: int = 30) -> Dict[str, Any]:
        results = {
            "status": "success",
            "deleted_usage_events": 0,
            "deleted_webhook_events": 0,
            "errors": []
        }

        try:
            results["deleted_usage_events"] = 0
            results["deleted_webhook_events"] = 0

        except Exception as e:
            results["status"] = "error"
            results["errors"].append(f"Cleanup failed: {str(e)}")
            logger.error(f"Cleanup job failed: {str(e)}")

        return results

    @staticmethod
    def run_stripe_reconciliation(db: Session) -> Dict[str, Any]:
        results = {
            "status": "success",
            "subscriptions_checked": 0,
            "mismatches": [],
            "errors": []
        }

        try:
            from app.models import Subscription
            subscriptions = db.query(Subscription).filter(
                Subscription.stripe_subscription_id.isnot(None)
            ).all()

            results["subscriptions_checked"] = len(subscriptions)

            for sub in subscriptions:
                if sub.stripe_subscription_id and sub.status == "active":
                    results["mismatches"].append({
                        "subscription_id": sub.stripe_subscription_id,
                        "tenant_id": sub.tenant_id,
                        "status": sub.status,
                        "note": "Mock mode: No Stripe API call made"
                    })

        except Exception as e:
            results["status"] = "error"
            results["errors"].append(f"Reconciliation failed: {str(e)}")
            logger.error(f"Reconciliation job failed: {str(e)}")

        return results
