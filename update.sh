SHA=$(git -C OneLifeData7 sha)
git clone --depth 1 https://github.com/jasonrohrer/OneLifeData7 || git -C OneLifeData7 pull

mkdir -p sprites
pipenv run python update.py
