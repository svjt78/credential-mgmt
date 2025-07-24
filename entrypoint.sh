#!/usr/bin/env sh
# entrypoint.sh

# 1) Create DB tables
python - <<'EOF'
from database import engine, Base
import models
Base.metadata.create_all(bind=engine)
EOF

# 2) Delegate to whatever CMD was specified in the Dockerfile
exec "$@"
