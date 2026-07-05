python update.py --once
python parse.py > current.txt
cat current.txt
read -p "Press enter to continue"
git commit -m "Added today's egg count"
git push