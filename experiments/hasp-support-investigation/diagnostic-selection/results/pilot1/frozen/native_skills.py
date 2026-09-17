"""Independent HASP PFs for synthetic checkout investigation evidence.

The harness supplies observed facts in ctx.raw['support_evidence']. These gates
check prerequisites, never compare PFs or infer evidence from a proposed action.
"""
from skills.pf_template import Anchor, inject, pf_skill


def _facts(ctx):
    return ctx.raw.get("support_evidence", {})


def _checkout_failure(f):
    return f.get("operation") == "checkout" and f.get("status") == 500


@pf_skill(
    "evidence_collection", domain="support",
    anchor=Anchor(level="step", evidence="deterministic",
                  trigger="Checkout failure lacks an endpoint, request ID, or captured request"),
    summary="Collect missing endpoint, request ID, and request capture for a checkout failure.",
)
class EvidenceCollection:
    def should_activate(self, ctx, action, arg):
        f = _facts(ctx)
        return _checkout_failure(f) and any(
            not f.get(k) for k in ("endpoint", "request_id", "request_captured")
        )

    def intervene(self, ctx, action, arg):
        f = _facts(ctx)
        missing = [k for k in ("endpoint", "request_id", "request_captured") if not f.get(k)]
        return inject(
            "[evidence_collection @step] Missing evidence: " + ", ".join(missing)
            + ". Capture the failing request with method, URL, headers, body, response, "
            "timestamp and correlation ID; redact credentials.",
            reason="request evidence incomplete",
        )


@pf_skill(
    "request_id_trace", domain="support",
    anchor=Anchor(level="step", evidence="deterministic",
                  trigger="Checkout failure has endpoint and request ID and its trace is not exhausted"),
    summary="Trace a failing checkout request ID through correlated logs when that trace remains unexplored.",
)
class RequestIdTrace:
    def should_activate(self, ctx, action, arg):
        f = _facts(ctx)
        return bool(_checkout_failure(f) and f.get("endpoint") and f.get("request_id")
                    and not f.get("trace_exhausted"))

    def intervene(self, ctx, action, arg):
        f = _facts(ctx)
        return inject(
            f"[request_id_trace @step] Trace request {f['request_id']} for {f['endpoint']} "
            "through gateway and application logs. Locate the first failing span and its "
            "error details; correlate by request ID and timestamp.",
            reason="unexplored correlated request available",
        )


@pf_skill(
    "comparison_experiment", domain="support",
    anchor=Anchor(level="step", evidence="deterministic",
                  trigger="Web checkout fails while mobile succeeds for the same account and operation"),
    summary="Compare failing web and successful mobile checkout requests for the same account and operation.",
)
class ComparisonExperiment:
    def should_activate(self, ctx, action, arg):
        f = _facts(ctx)
        return bool(_checkout_failure(f) and f.get("web_fails") and f.get("mobile_succeeds")
                    and f.get("same_account") and f.get("same_operation"))

    def intervene(self, ctx, action, arg):
        return inject(
            "[comparison_experiment @step] Compare the failing web request with a successful "
            "mobile request for the same account and operation. Hold account, cart, timing "
            "and backend constant; compare headers and payloads, then replay one changed "
            "factor at a time in a test environment to check whether the failure follows it.",
            reason="matched success and failure available",
        )


@pf_skill(
    "dependency_trace", domain="support",
    anchor=Anchor(level="step", evidence="deterministic",
                  trigger="Checkout failure has an endpoint and downstream dependencies remain unverified"),
    summary="Inspect checkout downstream calls for input-specific failures while dependency behavior is unverified.",
)
class DependencyTrace:
    def should_activate(self, ctx, action, arg):
        f = _facts(ctx)
        return bool(_checkout_failure(f) and f.get("endpoint")
                    and not f.get("dependencies_verified_successful"))

    def intervene(self, ctx, action, arg):
        return inject(
            "[dependency_trace @step] Inspect checkout calls to cart, inventory and payment "
            "services. Check per-request status, latency, routing and input propagation; "
            "a successful mobile checkout or unchanged backend version does not exclude "
            "a dependency failure caused by different web inputs.",
            reason="downstream behavior unverified",
        )


@pf_skill(
    "binary_isolation", domain="support",
    anchor=Anchor(level="step", evidence="deterministic",
                  trigger="Checkout failure has multiple differing headers or a frontend deployment change set"),
    summary="Bisect differing request headers or frontend changes between failing and successful checkout reproductions.",
)
class BinaryIsolation:
    def should_activate(self, ctx, action, arg):
        f = _facts(ctx)
        return bool(_checkout_failure(f) and (
            len(f.get("differing_headers", [])) >= 2 or f.get("frontend_deployment_precedes_failure")
        ))

    def intervene(self, ctx, action, arg):
        return inject(
            "[binary_isolation @step] In a test reproduction, bisect the differing header "
            "set or frontend deployment changes against a known-good control. Test both "
            "halves and their combination, allowing for interacting changes; retain the "
            "smallest set that reproduces the failure and verify by reintroduction.",
            reason="separable input or deployment changes available",
        )
