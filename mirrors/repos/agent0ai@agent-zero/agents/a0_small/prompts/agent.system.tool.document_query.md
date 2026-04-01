### document_query
read local or remote documents or answer questions about them
args:
- `document`: url path or list of them
- `queries`: optional list of questions
- `query`: optional single-question alias
without `query` or `queries` it returns document content
for local files use full path; for web documents use full urls
