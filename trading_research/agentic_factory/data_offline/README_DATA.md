# data_offline — offline CSV input ONLY

This is the **only** place the factory reads market data from.

## Rules

- **Offline CSV only.** Place files here manually. The module never fetches,
  downloads, streams, or connects to any API to obtain data.
- No broker, no exchange, no Databento API, no network of any kind.
- Files here are research inputs only. Nothing here is live or production data.

## Expected CSV format (NQ ORB)

Intraday bars, one row per bar, with at least these columns
(case-insensitive headers):

```
timestamp,open,high,low,close
2024-01-02 09:30:00,16800.00,16812.50,16795.00,16808.25
2024-01-02 09:31:00,16808.25,16815.00,16804.75,16810.00
...
```

- `timestamp` should be parseable by pandas (`YYYY-MM-DD HH:MM:SS`).
- Bars should be within / around the regular session so the opening range
  (first N minutes) can be computed.
- The default sample path expected by `config\factory_config.yaml` is
  `data_offline/nq_orb_sample.csv`. Provide your own file at that path.

No sample CSV is shipped in this phase — you supply it offline.
