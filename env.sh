# Source this before any phd command in this study.
#
# PHD_ENV points at an empty file on purpose (see phd.env) so the CLI resolves
# to the local SQLite database in ./data rather than a shared remote. Everything
# the study knows is therefore in this repository.
_LE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PHD_ENV="$_LE_ROOT/phd.env"
export EPT_DATA="$_LE_ROOT/data"
export LE_PROJECT_ID=1
export LE_TOPIC_ID=1
