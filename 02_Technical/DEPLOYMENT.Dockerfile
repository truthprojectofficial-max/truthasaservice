# Order Get It Right -- DEPLOYMENT.Dockerfile
#
# Clean-host verifier for F8-EXTENDED evaluation suite and D1-TRUE
# portability test. The image runs the project on a Python 3.12 base
# (the minimum the runtime supports; 3.14 also works) and exits with
# the verify_chain result. The chain volume is mounted from the host
# so the seal artefacts are written to the operator's actual 03_Vault.
#
# Build:    docker build -f 02_Technical/DEPLOYMENT.Dockerfile -t ogir:eval-2026-07-18 .
# Verify:   docker run --rm -v "$(pwd)/03_Vault:/app/03_Vault" ogir:eval-2026-07-18
#            python -m src.verify_chain
# Test:     docker run --rm -v "$(pwd)/03_Vault:/app/03_Vault" ogir:eval-2026-07-18
#            python -m pytest tests/ -q
#
# Notes:
#   - The runtime is pure stdlib Python + 10 third-party packages listed
#     in 02_Technical/requirements.txt. The Dockerfile pins them.
#   - The chain is mounted read-write so the verifier's block-count
#     SHUTDOWN writes go to the host's chain (matches the laptop).
#   - The 00-99 boundary test enforces that src/ cannot import from
#     03_Vault/ or 04_Validation/; mounting only 03_Vault is enough
#     to run the runtime + the test suite.
#   - For air-gap: pass --network=none to the docker run. The runtime
#     has no network calls in the audit path; the build downloads
#     pip packages once at build time only.

FROM python:3.12-slim

# Avoid writing .pyc files and force stdout/stderr to be unbuffered so
# the verify_chain output streams in the docker logs.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=0

WORKDIR /app

# Install the 10 third-party packages. The runtime is otherwise
# pure stdlib. We install first (separate layer) so the source copy
# below is a fast no-op when only the source changes.
COPY 02_Technical/requirements.txt /app/02_Technical/requirements.txt
RUN pip install --no-cache-dir -r /app/02_Technical/requirements.txt

# Copy the project tree. The Dockerfile is at 02_Technical/, so
# the COPY paths are relative to 02_Technical/. We add the parent
# directory so the conftest.py and tests/ at the project root are
# visible to pytest from /app.
COPY . /app/02_Technical/
COPY conftest.py /app/conftest.py
COPY pyproject.toml /app/pyproject.toml
COPY tests /app/tests

# Sanity: verify_chain must run without error. The actual match check
# requires the host's 03_Vault volume to be mounted; this is just a
# "does Python find the modules" check.
RUN cd /app/02_Technical && python -c "import src.utils.canonical; import src.io.vault_io; print('import_ok')"

# Default command: re-derive the Merkle root from the mounted chain.
# The operator runs `docker run -v $(pwd)/03_Vault:/app/03_Vault ogir:eval-2026-07-18`
# and reads the root from the output.
WORKDIR /app/02_Technical
CMD ["python", "-m", "src.verify_chain"]