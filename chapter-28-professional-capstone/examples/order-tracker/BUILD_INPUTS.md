# Artifact-verification build-input record

This record was checked against the linked primary release pages on
2026-07-15. It identifies the direct tools selected for the Chapter 28 local
artifact workflow; it is not a transitive dependency lock, an acquisition
command, a legal review, or permission to publish.

- `build==1.3.0`: selected artifact
  `build-1.3.0-py3-none-any.whl`; recorded SHA-256
  `7145f0b5061ba90a1500d60bd1b13ca0a8a4cebdd0cc16ed8adf1c0e739f43b4`;
  [PyPI release metadata](https://pypi.org/project/build/1.3.0/).
- `setuptools==80.9.0`: selected artifact
  `setuptools-80.9.0-py3-none-any.whl`; recorded SHA-256
  `062d34222ad13e0cc312a4c02d73f059e86a4acbfbdea8f8f76b28c99f306922`;
  [PyPI release metadata](https://pypi.org/project/setuptools/80.9.0/).
- `wheel==0.45.1`: selected artifact
  `wheel-0.45.1-py3-none-any.whl`; recorded SHA-256
  `708e7481cc80179af0e556bbf0cc00b8444c7321e2700b8d8580231d13017248`;
  [PyPI release metadata](https://pypi.org/project/wheel/0.45.1/).

Those release pages report MIT license metadata for the selected projects.
That observation does not replace inspection of the exact provisioned files
or competent license/provenance approval. The verifier checks the two isolated
backend-input wheel hashes; `build` is a separately provisioned frontend whose
executed version is reported. Its transitive runtime dependencies are not
captured here, which is one reason this record and `requirements-build.txt`
must not be described as a complete lock.

Technical behavior is based on the official
[`build` isolation explanation](https://build.pypa.io/en/stable/explanation/how-it-works.html),
[source-distribution specification](https://packaging.python.org/en/latest/specifications/source-distribution-format/),
and [wheel specification](https://packaging.python.org/en/latest/specifications/binary-distribution-format/).
These references explain formats and interfaces; they do not prove that this
project's artifacts pass. Only the local verifier can produce that bounded
host-specific evidence.
