# check if value is float
def isfloat(value):
	try:
		float(value)
		return True
	except ValueError:
		return False
