
![GitHub Logo](/logo/logo.png)


* KGQAn has been developed using Python 3.7
* Make sure you create a virtual environment, activated it and the thin pip install the requirement.txt file comes with the project. 
* Make sure the file `wiki-news-300d-1M.txt` is under `word_embedding` directory
* Start the Word Embedding server using the command `python word_embedding/server.py 127.0.0.1 9600`.

KGQAn Project is work under development; expect some abnormality during installing and using the software.

License: Not determined yet!

Documentation: http://cods.encs.concordia.ca/kgqan

Usage
-----
First you need to import kgqan 

``from kgqan import KGQAn``

and then create an instance as following:

``my_kgqan = KGQAn()``

and then
 
 ``answers = my_kgqan.ask("Who was the doctoral supervisor of Albert Einstein?")``
