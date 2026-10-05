# Single mitigation diff

Exactly one mitigation was applied: a tighter agent planning/tool description.

```diff
- get_openapi_spec: Return the schema for an operation.
+ get_openapi_spec: Verify the selected operation's real path, API version,
+ required arguments, and deprecation flag before producing any final answer.
```

No argument validator, step limit, re-planning behavior, workflow replacement, or other mitigation was added in this experiment.
