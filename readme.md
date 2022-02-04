* My python version is 3.8.10
* No external library is used.
* You can run the indexer using the following command: <code> python3 preprocess_and_index.py</code>. 
  * It will generate a json file named <code> myindex_unique.json</code>. 
  * It is approximately 10 MB and query evaluator program uses it as a source.
* You can run the query evaluator using the following command: <code> python3 query_eval.py</code>.
  * It is an interactive program. It expects you to type the input to stdin.
  * It writes the output of the query to a file named <code> result_{timestamp}.json</code>.
  * You should close the program with input <code> q </code>to see the outputs.

* Datased used in this project is [Reuters-21578](https://archive.ics.uci.edu/ml/datasets/reuters-21578+text+categorization+collection) dataset.

**Adalet Veyis Turgut**
