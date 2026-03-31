# HITL Implementation TODO

## Phase 1: Core HITL Types (using real AgentTask/SharedState patterns)
- [ ] Create `core/hitl_types.py` with InterventionRequest, InterventionResponse, HITLDecision
  - Mirror AgentTask dataclass structure from base_agent.py
  - Use same patterns: dataclass, to_dict(), from_dict()

## Phase 2: HITL Middleware (integrates with _process_task_queue)
- [ ] Create `core/hitl_middleware.py` with HITLMiddleware class
  - Intercept tasks in _process_task_queue() flow
  - Add intervention gates after tool execution, before agent analysis
  - Support: NONE, ASYNC_REVIEW, BLOCKING_APPROVAL

## Phase 3: Policy Configuration
- [ ] Create `config/hitl_policy.py` with risk policies
  - Map to real task types: network_scan, vuln_scan, etc.
  - Critical: exploitation tasks → BLOCKING_APPROVAL

## Phase 4: Orchestrator Integration
- [ ] Modify `orchestrator/purple_lead.py`
  - Add HITL evaluation in _process_task_queue()
  - Gate after _execute_tool_for_task(), before agent.execute_task()
  - Handle blocking approval with timeout

## Phase 5: Dashboard API
- [ ] Create `dashboard/hitl_routes.py`
  - GET /api/hitl/pending
  - POST /api/hitl/respond
  - GET /api/hitl/status/<id>

## Phase 6: Dashboard UI
- [ ] Create `dashboard/templates/hitl_dashboard.html`
- [ ] Create `dashboard/static/js/hitl_dashboard.js`

## Phase 7: Integration
- [ ] Modify `dashboard/app.py` to register HITL blueprint
- [ ] Add HITL config to `config/settings.py`

## Phase 8: Testing
- [ ] Test with network_scan (should auto-approve)
- [ ] Test with exploitation (should block for approval)
