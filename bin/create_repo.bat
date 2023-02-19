echo "git repo"
%1:
cd %2
git init
git add .
git commit -m "first commit"
git switch -c main
git remote add origin %3
git pull origin main --allow-unrelated-histories --no-edit
git push -u origin main

