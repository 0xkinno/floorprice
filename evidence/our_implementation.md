# Our implementation (neutral description for coding (a))

Every technique implements one interface: `score(source)` in [0, 1], `threshold()`, and `receipt(source)`.
A receipt is canonical JSON with fields source, technique, version, inputs_digest, score, threshold, verdict, recompute (a command),
generated_at, and a SHA-256 digest over every field except generated_at and digest.
All inputs: the Lin et al. dataset (public), the prompts in `floorprice/prompts.py`, parameters in `floorprice/config.py`, all committed.
Model responses are cached by SHA-256 of the full request and replayable offline with `FLOORPRICE_OFFLINE=1`.
T2 and T3 use hosted models at temperature 0; the stability of repeated calls is measured separately (E4) and is not assumed.
T4 to T7 are deterministic given a seed. No appeal or contest mechanism exists in the repository.
