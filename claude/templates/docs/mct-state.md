# MCT State

The MCT CLI writes project-local state under:

```txt
.mct/
  state.json
  receipts/
```

`state.json` records recent runs. `receipts/` stores structured JSON receipts for completed MCT batches.

Do not commit `.mct/` unless the project intentionally wants shared automation history.
