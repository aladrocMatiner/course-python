# Appendix C path migration

## Current path

The portable physical directory is:

```text
zz_Appendix C Software Design Patterns
```

The visible lesson title remains `Appendix C: Software Design Patterns in
Python`. The colon is intentionally absent from the directory name because a
Git checkout containing `:` is not portable to Windows.

The catalogue declares the machine-safe logical ID that publication and parity
will retain after the shared ownership gate is completed:

```text
appendix-software-design-patterns
```

This mapping is not active yet. Generic discovery still recognizes only the
currently published `chapter-` and `appendix-` units; Appendix C must remain out
of root navigation until the mapping, nested-page aggregation, translations,
and publication evidence are implemented together.

## Previous path

The previous repository path was:

```text
appendix-software-design-patterns
```

Update local commands, links, and source references to the current path and
quote it in shells and metadata because it contains spaces. For example:

```text illustrative
python3 -B -m unittest discover \
  -s "zz_Appendix C Software Design Patterns/tests" -v
```

GitHub and GitLab do not provide repository-controlled redirects for arbitrary
renamed blob paths or heading fragments. The project therefore records this as
an explicit breaking path migration; it does not claim that old file URLs keep
working. Root course navigation will point only to the current path once the
complete multilingual publication gate passes.

## Rollback boundary

Before public navigation and parity reconciliation, rollback means reverting
the complete organization change: physical move, catalogue, nested pages,
commands, source references, plugin constants, tests, and OpenSpec artifacts,
then rerunning the Appendix-local suites. Moving only the directory would leave
broken references. After publication, any further rename requires a new
approved migration, refreshed digests, and pending human review against the
changed inputs.
