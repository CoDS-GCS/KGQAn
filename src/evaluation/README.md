Evaluation
===========
To evaluate the system on QALD dataset.

QALD 6 or Later (Ubuntu)
------------------
`sudo apt-get remove --purge ruby-full`

`sudo apt-get update`

`sudo apt-get install git-core curl zlib1g-dev build-essential libssl-dev libreadline-dev libyaml-dev libsqlite3-dev sqlite3 
libxml2-dev libxslt1-dev libcurl4-openssl-dev software-properties-common libffi-dev`

`cd`

`git clone https://github.com/rbenv/rbenv.git ~/.rbenv`

`echo 'export PATH="$HOME/.rbenv/bin:$PATH"' >> ~/.bashrc`

`echo 'eval "$(rbenv init -)"' >> ~/.bashrc`

`exec $SHELL`

`git clone https://github.com/rbenv/ruby-build.git ~/.rbenv/plugins/ruby-build`

`echo 'export PATH="$HOME/.rbenv/plugins/ruby-build/bin:$PATH"' >> ~/.bashrc`

`exec $SHELL`

`rbenv install 2.7.0`

`rbenv global 2.7.0`

`gem install bundler`

`rbenv rehash`

`gem install nokogiri mustache multiset`

`git clone https://github.com/ag-sc/QALD.git`

Rename `QALD/6/data/qald-6-test-multilingual.json` into `QALD/6/data/dbpedia-test.json`

`cd projects/QALD/6/scripts/`

`ruby evaluation.rb dir/output/KGQAn_result_20200325-163649.json`


MacOS
------------------
`brew install rbenv`

`rbenv install 2.7.0`

`rbenv global 2.7.0`

`gem install bundler --user-install`

`gem install nokogiri mustache multiset --user-install`

------------------
`git clone https://github.com/ag-sc/QALD.git`

Rename `QALD/6/data/qald-6-test-multilingual.json` into `QALD/6/data/dbpedia-test.json`

`cd projects/QALD/6/scripts/`

`ruby evaluation.rb dir/output/KGQAn_result_20200325-163649.json`
