#!/usr/bin/env bash
# Build one eval's sandbox: a learner data dir in the state its scenario needs,
# plus a `seba` wrapper that runs this checkout's CLI against that dir and logs
# every call the tutor makes.
#
#   skills/seba-tutor/evals/setup.sh SCENARIO DEST
#
# DEST/bin/seba   the tutor's `seba`; each call appends its argv to DEST/seba.log
#                 as one JSON array per line
# DEST/data/      SEBA_DATA_DIR for the run
# Fixture calls below bypass the wrapper, so the log holds the tutor's calls only.
set -euo pipefail
scenario="$1"
dest="$(mkdir -p "$2" && cd "$2" && pwd)"
repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
export SEBA_DATA_DIR="$dest/data"
rm -rf "$SEBA_DATA_DIR" "$dest/bin" "$dest/seba.log"
mkdir -p "$dest/bin"
: > "$dest/seba.log"

cat > "$dest/bin/seba" <<EOF
#!/usr/bin/env bash
python3 -c 'import json, sys; print(json.dumps(["seba", *sys.argv[1:]]))' "\$@" >> "$dest/seba.log"
SEBA_DATA_DIR="$SEBA_DATA_DIR" exec uv run --project "$repo" --quiet seba "\$@"
EOF
chmod +x "$dest/bin/seba"

s() { uv run --project "$repo" --quiet seba "$@" > /dev/null; }

# Probability goal. conditional-probability is unseen unless a scenario says
# otherwise; bayes-rule and independence both need it.
syllabus() {
  local cp_status="$1"
  cat > "$dest/syllabus.yaml" <<EOF
goal: Understand introductory probability
subject: probability
concepts:
  - {id: sample-spaces, name: Sample spaces and events, prereqs: [], soft_prereqs: [], confusable_with: [], kc_type: concept, sources: [], status: done, est_sessions: 1}
  - {id: conditional-probability, name: Conditional probability, prereqs: [sample-spaces], soft_prereqs: [], confusable_with: [], kc_type: concept, sources: [], status: $cp_status, est_sessions: 1}
  - {id: bayes-rule, name: Bayes' rule, prereqs: [conditional-probability], soft_prereqs: [], confusable_with: [], kc_type: procedure, sources: [], status: unseen, est_sessions: 2}
  - {id: independence, name: Independence of events, prereqs: [conditional-probability], soft_prereqs: [], confusable_with: [], kc_type: concept, sources: [], status: unseen, est_sessions: 1}
EOF
  s new-goal prob --subject probability --from-file "$dest/syllabus.yaml"
  rm "$dest/syllabus.yaml"
}

# Session 1 taught conditional-probability, minted two cards, left a hint.
session_one() {
  syllabus unseen
  s start prob
  s concept prob conditional-probability --status started \
    --note "MISCONCEPTION: treats P(A|B) and P(B|A) as equal"
  s mint prob --concept conditional-probability --type apply \
    --front "A fair die shows an even number. What is P(roll = 6 | even)?" \
    --back "1/3: knowing the roll is even shrinks the sample space to {2,4,6}"
  s mint prob --concept conditional-probability --type apply \
    --front "Two fair coins are tossed and at least one is heads. What is P(both heads | at least one head)?" \
    --back "1/3: the condition leaves {HH, HT, TH}, one of which is HH"
  s end prob --summary "Introduced conditional probability as restricting the sample space. Learner computed two die problems with help and reversed P(A|B) once." \
    --hint "Open on the reversed-conditional trap: ask for P(B|A) right after P(A|B); stop when they flag the difference unprompted."
}

item() { # id of the review card whose front contains $1
  uv run --project "$repo" --quiet seba start prob | grep -v "^(resuming" |
    uv run --project "$repo" --quiet python -c 'import sys,yaml; d=yaml.safe_load(sys.stdin); print(next(i["id"] for i in d["agenda"]["review_items"] if sys.argv[1] in i["front"]))' "$1"
}

case "$scenario" in
  opening) # session 1 done; learner is about to begin session 2
    session_one ;;
  review-pending) # session 2 started; both cards ungraded
    session_one
    s start prob ;;
  review-failed) # session 2 started; die card graded again
    session_one
    s start prob
    s grade prob "$(item die)" again --note "Answered 1/6: counted all six faces, ignoring the condition." ;;
  slipped) # conditional-probability done, its card failed two sessions running; session 4 not started
    syllabus done
    s start prob
    s mint prob --concept conditional-probability --type apply \
      --front "A fair die shows an even number. What is P(roll = 6 | even)?" \
      --back "1/3: knowing the roll is even shrinks the sample space to {2,4,6}"
    s end prob --summary "Reviewed conditional probability." --hint "Start bayes-rule."
    for n in 2 3; do
      s start prob
      s grade prob "$(item die)" again --note "Gave 1/6: did not restrict to the even faces."
      s end prob --summary "Card on conditioning failed again." --hint "Watch the die card."
    done ;;
  review-one-graded) # session 2 started; die card graded, coin card ungraded, teaching begun
    session_one
    s start prob
    s grade prob "$(item die)" good ;;
  steer-recorded) # conditional-probability done; session steered to bayes-rule, one review graded
    syllabus done
    s start prob
    s mint prob --concept conditional-probability --type apply \
      --front "A fair die shows an even number. What is P(roll = 6 | even)?" \
      --back "1/3: knowing the roll is even shrinks the sample space to {2,4,6}"
    s end prob --summary "Reviewed conditional probability." --hint "Move on to bayes-rule or independence."
    s start prob --concept bayes-rule
    s grade prob "$(item die)" good ;;
  first-teach) # session 1 started; conditional-probability started, no card minted yet
    syllabus unseen
    s start prob
    s concept prob conditional-probability --status started ;;
  *) echo "unknown scenario: $scenario" >&2; exit 2 ;;
esac
echo "sandbox ready: $dest (scenario $scenario)"
