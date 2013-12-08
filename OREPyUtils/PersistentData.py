from os.path import isfile as Exists

import StringIO

from ast import literal_eval as Eval

def ReadDelim(f, delim, blocksize=1024):
	end = ''

	while True:
		block = f.read(blocksize)

		if not block:
			break

		parts = block.split(delim)

		if len(parts) == 1:
			end += parts[0]
		else:
			yield end + parts[0]

			for p in parts[1:-1]:
				yield p

			end = parts[-1]

	yield end

class DictBackend:
	def LoadDict(self, node, x):
		for item, value in x.iteritems():
			if isinstance(value, dict):
				node[item] = Node()

				self.LoadDict(node[item], value)		
			else:
				node[item] = value

	def FromStr(self, node, x):
		try:
			data = Eval(x)

		except:
			data = {}

	#	data = {}

	#	stream = StringIO.StringIO(x)

	#	for fNode in ReadDelim(stream, '}'):
	#		print fNode

		self.LoadDict(node, data)

	def ToStr(self, node, embed=0):
		toReturn = [(" " * embed) + "{\n"]

		for item, value in node.iteritems():
			if isinstance(value, Node):
				toReturn.append((" " * embed) + "'" + item + "' : " + self.ToStr(value, embed + 4) + ",\n")
			elif isinstance(value, str):
				toReturn.append((" " * embed) + "'" + item + "' : '" + value + "',\n")
			else:
				toReturn.append((" " * embed) + "'" + item + "' : " + str(value) + ",\n")

		toReturn.append((" " * embed) + "}")

		return ''.join(toReturn)

class NodeManager:
	def __init__(self, data=None, backend=DictBackend):
		self.backend = backend()
		self.node = Node()

		if isinstance(data, dict): 
			self.backend.LoadDict(self.node, data)
		elif isinstance(data, str):
			self.backend.FromStr(self.node, data)

	def __str__(self):
		return self.backend.ToStr(self.node)

	def Dict(self):
		return self.node.Dict()

class ExternalNodeManager(NodeManager):
	def __init__(self, node, data=None, backend=DictBackend):
		self.backend = backend()
		self.node = node
		self.backend.Load(self.node, data)

class NodeFile(NodeManager):
	def __init__(self, filename, backend=DictBackend, read=True):
		if Exists(filename) and read:
			data = open(filename).read()
		else:
			data = None

		self.filename = filename

		NodeManager.__init__(self, data, backend)

	def Dump(self):
		open(self.filename, 'w').write(str(self))

class Node:
	def iteritems(self):
		return self.__dict__.iteritems()

	def itervalues(self):
		return self.__dict__.itervalues()

	def iterkeys(self):
		return self.__iter__()

	def __iter__(self):
		return self.__dict__.iterkeys()

	def __contains__(self, item):
		return item in self.__dict__

	def __setitem__(self, Item, To):
		self.__dict__[str(Item)] = To

	def __getitem__(self, Item):
		return self.__dict__[Item]

	def __delitem__(self, Item):
		del self.__dict__[Item]

	def __len__(self):
		return len(self.__dict__)	

	def copy(self):
		new = Node()
		new.__dict__ = self.__dict__.copy()

		return new

        def Dict(self):
                toReturn = {}

                for item, value in self.iteritems():
                        if isinstance(value, Node):
                                toReturn[item] = value.Dict()

                        else:
                                toReturn[item] = value

                return toReturn
	
	def __add__(self, node):
		new = self.copy()

		if isinstance(node, Node):
			for item, value in node.iteritems():
				new[item] = value

		return new
