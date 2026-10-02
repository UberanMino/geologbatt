"""GEO recursive content-optimization agent.

A three-agent loop (Generator -> Judge -> Scorer -> Synthesizer -> Generator)
that iteratively rewrites a piece of content so that a generative search engine
is more likely to *name* the brand when it answers real prompts.

See README.md for the architecture and the design rationale.
"""

__version__ = "0.1.0"
