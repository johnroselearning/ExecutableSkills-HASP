"""OFFLINE ONLY: closed-world single-fault hypotheses and counterfactuals."""
HYPOTHESES = {
    'H1': 'Web serializer sends amount as string; current backend raises at checkout normalization. Mobile numeric amount succeeds.',
    'H2': 'Web omits auth scope header; middleware incorrectly converts scope rejection into 500. Mobile has scope and succeeds.',
    'H3': 'Shared backend amount-normalization regression rejects both numeric and string amounts. A harmless web string-format difference coexists.',
    'H4': 'Shared payment failure affects matched web and mobile checkout; request encoding and auth are valid.',
}
# Not given to policy or PF selector. Labels index public observations in oracle.py.
OUTCOMES = {
    'A': {'H1': 'internal', 'H2': 'internal', 'H3': 'internal', 'H4': 'downstream'},
    'B': {'H1': 'web_only', 'H2': 'web_only', 'H3': 'both', 'H4': 'both'},
    'C': {'H1': 'normalize', 'H2': 'scope', 'H3': 'normalize', 'H4': 'payment'},
    'D': {'H1': 'amount', 'H2': 'scope', 'H3': 'amount', 'H4': 'valid'},
    'E': {'H1': 'healthy', 'H2': 'healthy', 'H3': 'healthy', 'H4': 'failed'},
    'F': {h: h for h in HYPOTHESES},
}
