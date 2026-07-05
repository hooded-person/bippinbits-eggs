python update.py --once
python parse.py --plain > current.txt
python parse.py
read -p "Press enter to continue"
git commit -m "Added today's egg count"
git push