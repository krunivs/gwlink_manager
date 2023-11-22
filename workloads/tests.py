from django.test import TestCase
import datetime


# Create your tests here.
class WorkloadsTests(TestCase):

	def test_timdelta(self):
		# s = 13420
		time_format = '%Y-%m-%d %H:%M:%S'
		s = datetime.datetime.now().timestamp() - datetime.datetime.strptime("2022-11-28 11:53:56", time_format).timestamp()
		print(s)
		hours, remainder = divmod(s, 3600)
		minutes, seconds = divmod(remainder, 60)
		print(f'{hours:02}:{minutes}:{seconds}')
		days = hours / 24
		hours %= 24
		print('{:02}days {:1}H {:02}M'.format(int(days), int(hours), int(minutes)))
