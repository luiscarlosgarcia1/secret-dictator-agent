# Prioritize fault resistance before tactical optimization

The agent will first guarantee one valid, timely response for every supported Secret Dictator decision from reconstructed visible history, then improve faction-specific strategy. This deliberately favors deterministic validation and conservative fallbacks over brittle tactics because an invalid or late response can abort an early match or surrender a later decision to the baseline, making raw strategic strength irrelevant.

## Considered Options

- Pursue more aggressive strategic behavior before completing protocol coverage.
- Validate all decision shapes, legal targets, and private-policy observations first, then layer tactical scoring on top.

The second option is adopted.
