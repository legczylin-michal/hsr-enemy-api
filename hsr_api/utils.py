import hashlib
import urllib.request


def uid_from_name(p_name: str) -> str:
	"""  """
	
	assert isinstance(p_name, str)
	
	m = hashlib.md5()
	m.update(p_name.encode('utf-8'))
	
	return m.hexdigest()[0:16]


def get_all_contents(p_url: str) -> str:
	"""  """
	
	assert isinstance(p_url, str)
	
	file_pointer = urllib.request.urlopen(p_url)
	read_bytes = file_pointer.read()
	
	contents = read_bytes.decode("utf-8")
	file_pointer.close()
	
	return contents
