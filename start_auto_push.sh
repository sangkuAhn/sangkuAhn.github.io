#!/bin/sh



cd /usr/local/share/sangkuAhn.github.io/

echo "##################"
git pull
sleep 2
echo "##################"
echo "##################"
git add --all
sleep 1
echo "##################"
git commit -m "auto push"
sleep 2
git push origin

