cd /home/joe/python/investcop/investcop
touch start.me
echo starting summary
python /home/joe/python/investcop/investcop/summary.py
echo finishing summary
touch finish.me 
echo adding to git
git add summary.py
git commit -m  "summary update"
git push https://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@github.com/jplirani/investcop.git
rm start.me
echo done!
