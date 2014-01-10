#!/bin/sh

git config receive.denyCurrentBranch ignore
echo -n "#!/bin/sh
GIT_WORK_TREE=../ git checkout -f
" > .git/hooks/post-receive
chmod +x .git/hooks/post-receive
