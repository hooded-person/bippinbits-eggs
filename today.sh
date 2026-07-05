python update.py --once
python analyse.py
python parse.py
read -p "Press enter to continue"
git add eggs.csv images/ GRAPHS.md
git commit -m "Added today's egg count"
git push