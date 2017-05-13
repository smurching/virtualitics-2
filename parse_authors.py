def parse_authors():
	filename = 'linkedin/authors_milspec.txt'

	with open(filename, 'r') as f:
	    authors = f.readlines()

	for i, author in enumerate(authors):
	    temp = author[:-1].split(',')
	    if len(temp) != 2:
	        name = "".join(temp[:2])
	        temp = [name, temp[2]]
	    temp[1] = int(temp[1])
	    authors[i] = tuple(temp)
	return authors