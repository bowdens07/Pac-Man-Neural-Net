from utilities.PathingNode import PathingNode
from operator import itemgetter


class PriorityQueue:
	def __init__(self):
		self.queue = []

	def set_priority(self, item, priority):
		for node in self.queue:
			if node[0] == item:
				self.queue.remove(node)
				break
		self.put(item, priority)

	def put(self, item, priority:int):
		node = [item,priority]
		self.queue.append(node)
		self.queue.sort(key=itemgetter(1))

	def get(self):
		if len(self.queue) == 0:
			return None
		node = self.queue.pop(0)
		return node[0]

	def empty(self):
		return len(self.queue) == 0