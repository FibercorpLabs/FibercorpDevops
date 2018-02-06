def removeEmptyParams(params):
	keysToBeRemoved = []

	for key in params:
		if params[key] is None:
			keysToBeRemoved.append(key)

	for key in keysToBeRemoved:
		params.pop(key)

	return params


# def createDictionaryFromParams(**kwargs):

# 	for key, value in kwargs.items():
		

# 	return dictionary