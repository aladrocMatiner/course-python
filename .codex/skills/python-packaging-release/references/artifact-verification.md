# Artifact verification

## Clean build topology

Use three independent temporary locations:

1. a source snapshot or clean checkout used only as build input;
2. a build/output area containing sdists and wheels;
3. a fresh install environment plus a foreign current working directory.

Disable source-tree import leakage. Confirm the imported module path belongs to the install environment, not the checkout.

## Source distribution inspection

Require the files needed to rebuild: project metadata, package sources, build configuration, declared license/notices, type information, native manifests/locks when applicable, and intended data files. Reject credentials, caches, virtual environments, build products, test-only rendezvous hooks, and unrelated local files.

Build a wheel from the produced sdist when the lesson promises that the sdist is complete.

## Wheel inspection

Check normalized project/version metadata, compatibility tags, package paths, import package, `RECORD`, license/notices, `py.typed` and stubs when promised, and expected native libraries. Inspect native runtime dependencies with platform-appropriate tools when making dependency claims.

Treat a tag as a declaration. Execute the wheel on each host/ABI before claiming that host verified.

## Installed behavior

Install the exact produced artifact into a fresh environment. From a directory containing a decoy module or no project source, verify:

- public import and version/metadata agreement;
- happy, boundary, invalid, and recovery behavior;
- CLI entry points when declared;
- type checker and `stubtest` surface when declared;
- absence of test-only APIs and undeclared native dependencies.

## Safe failure and cleanup

Name the phase that failed: metadata, isolated build, archive inspection, tag/dependency audit, installation, import, behavior, typing, or cleanup. Bound captured tool output and redact absolute paths/secrets. Delete all temporary environments/artifacts on every exit; verify the repository tree did not change.
