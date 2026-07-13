# faststats-cpp companion project

This source tree is the tested implementation used by chapter 24. Build outputs
belong in temporary directories; do not build in this directory.

The public package is `faststats_cpp`. Its compiled module `_native` is private.
The optional `_faststats_test` target is a deterministic concurrency test hook
and is never installed in a wheel.
