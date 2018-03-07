set -e

SHA_FILE="ONELIFEDATA7_SHA"
OLD_SHA=$(cat $SHA_FILE || true)

echo "Updating git..."
(>/dev/null 2>&1 git clone -q --depth 1 https://github.com/jasonrohrer/OneLifeData7 || \
  git -C OneLifeData7 pull -q)
NEW_SHA=$(git -C OneLifeData7 rev-parse HEAD)

if [ "$OLD_SHA" = "$NEW_SHA" ]
then
  echo "No new commits, done!"
  exit
fi

DIST=${1:-dist}
rm -rf "$DIST"
mkdir -p "$DIST/sprites"
pipenv run python gen.py "$DIST"

# Successfully created a distribution for this SHA.
echo "$NEW_SHA" > "$SHA_FILE"
