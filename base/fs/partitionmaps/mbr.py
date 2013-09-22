from abstract import AbstractPartitionMap
from ..partitions.mbr import MBRPartition
from ..partitions.mbr_swap import MBRSwapPartition
from common.tools import log_check_call


class MBRPartitionMap(AbstractPartitionMap):

	def __init__(self, data):
		self.boot = None
		self.swap = None
		self.mount_points = []
		if 'boot' in data:
			self.boot = MBRPartition(data['boot']['size'], data['boot']['filesystem'], None)
			self.mount_points.append(('/boot', self.boot))
		self.root = MBRPartition(data['root']['size'], data['root']['filesystem'], self.boot)
		self.mount_points.append(('/', self.root))
		if 'swap' in data:
			self.swap = MBRSwapPartition(data['swap']['size'], self.root)
			self.mount_points.append(('none', self.root))
		self.partitions = filter(lambda p: p is not None, [self.boot, self.root, self.swap])

		super(MBRPartitionMap, self).__init__()

	def _before_create(self, event):
		volume = event.volume
		log_check_call(['/sbin/parted', '--script', '--align', 'none', volume.device_path,
		                '--', 'mklabel', 'msdos'])
		for partition in self.partitions:
			partition.create(volume)

		boot_idx = self.root.get_index()
		if self.boot is not None:
			boot_idx = self.boot.get_index()
		log_check_call(['/sbin/parted', '--script', volume.device_path,
		                '--', 'set ' + str(boot_idx) + ' boot on'])
