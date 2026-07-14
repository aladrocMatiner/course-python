# Dependency evidence and terminology

## Classify inputs accurately

- A direct requirement names a project and an allowed version range.
- A direct pin selects one version for a direct requirement.
- A constraints file limits resolver choices but does not request installation by itself.
- A resolved environment snapshot such as basic `pip freeze` output describes one environment; it may omit hashes, markers, indexes, build inputs, and cross-platform intent.
- A complete lock must declare its resolver/tool, covered dependency groups, transitive versions, environment markers/tags, artifact or hash policy, indexes/sources, and update procedure strongly enough for its stated scope.

Do not call a file a lock merely because its filename ends in `.lock`.

## Reproducibility claim levels

Use the narrowest supported claim:

1. direct dependencies are pinned;
2. resolution is repeatable for a declared interpreter/platform/index snapshot;
3. artifacts are hash-selected for that scope;
4. clean builds and installs were repeated from declared inputs;
5. byte-for-byte reproducibility was measured.

Evidence for one level does not imply the next. Network indexes can change or remove artifacts, so record source/index assumptions and dates when relevant without saying “latest.”

## Build dependencies

Inspect `build-system.requires` separately from runtime and development/test dependencies. Build isolation must be able to obtain or use the declared build inputs. A runtime requirements file is not proof that an isolated sdist build has complete build requirements.

For offline-capable verification, pre-provision an exact local wheelhouse or explicitly state that initial dependency acquisition needs network access. Never silently reach a private index or use credentials from the maintainer environment.

## Update and recovery

Make updates deliberate: change the declared input, run the resolver for the stated matrix, inspect the diff, rebuild from clean state, and rerun artifact/import tests. Do not patch a generated lock by hand unless its owning tool explicitly supports that workflow.
