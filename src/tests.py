from main import load
import unittest

class TestMySetupConfigurations(unittest.TestCase):
	def watch(self, a, b, c):
		DEVICES['monitor1'].watch(a)
		DEVICES['monitor2'].watch(b)
		DEVICES['monitor3'].watch(c)

	def check(self, a, b, c):
		self.assertEqual((a, b, c), (
			DEVICES['monitor1'].whats_displayed(DEVICES),
		 	DEVICES['monitor2'].whats_displayed(DEVICES),
			DEVICES['monitor3'].whats_displayed(DEVICES),
		))

	#### HDMI =====================================
	def test_hdmi_hdmi_hdmi(self):
		self.watch('hdmi', 'hdmi', 'hdmi')
		self.check(None, None, ('mac', 'mdp'))

	def test_hdmi_hdmi_dp(self):
		self.watch('hdmi', 'hdmi', 'dp')
		self.check(None, None, None)

	def test_hdmi_hdmi_mdp(self):
		self.watch('hdmi', 'hdmi', 'mdp')
		self.check(None, None, ('laptop', 'usb-c'))


	def test_hdmi_mdp_hdmi(self):
		self.watch('hdmi', 'mdp', 'hdmi')
		self.check(None, None, ('mac', 'mdp'))

	def test_hdmi_mdp_mdp(self):
		self.watch('hdmi', 'mdp', 'mdp')
		self.check(None, None, None)

	def test_hdmi_mdp_dp(self):
		self.watch('hdmi', 'mdp', 'dp')
		self.check(None, None, None)


	def test_hdmi_dp_hdmi(self):
		self.watch('hdmi', 'dp', 'hdmi')
		self.check(None, ('laptop', 'usb-c'), ('mac', 'mdp'))

	def test_hdmi_dp_mdp(self):
		self.watch('hdmi', 'dp', 'mdp')
		self.check(None, ('laptop', 'usb-c'), ('laptop', 'usb-c'))

	def test_hdmi_dp_dp(self):
		self.watch('hdmi', 'dp', 'dp')
		self.check(None, ('laptop', 'usb-c'), None)
	#### HDMI =====================================

	#### MDP =====================================
	def test_mdp_hdmi_hdmi(self):
		self.watch('mdp', 'hdmi', 'hdmi')
		self.check(('laptop', 'usb-c'), None, ('mac', 'mdp'))

	def test_mdp_hdmi_mdp(self):
		self.watch('mdp', 'hdmi', 'mdp')
		self.check(('laptop', 'usb-c'), None, ('laptop', 'usb-c'))

	def test_mdp_hdmi_dp(self):
		self.watch('mdp', 'hdmi', 'dp')
		self.check(None, None, None)


	def test_mdp_dp_hdmi(self):
		self.watch('mdp', 'dp', 'hdmi')
		self.check(('laptop', 'usb-c'), ('laptop', 'usb-c'), ('mac', 'mdp'))

	def test_mdp_dp_mdp(self):
		self.watch('mdp', 'dp', 'mdp')
		self.check(('laptop', 'usb-c'), ('laptop', 'usb-c'), ('laptop', 'usb-c'))

	def test_mdp_dp_dp(self):
		self.watch('mdp', 'dp', 'dp')
		self.check(None, ('laptop', 'usb-c'), None)


	def test_mdp_mdp_hdmi(self):
		self.watch('mdp', 'mdp', 'hdmi')
		self.check(None, None, ('mac', 'mdp'))

	def test_mdp_mdp_mdp(self):
		self.watch('mdp', 'mdp', 'mdp')
		self.check(None, None, None)

	def test_mdp_mdp_dp(self):
		self.watch('mdp', 'mdp', 'dp')
		self.check(None, None, None)

	#### MDP =====================================

	#### DP =====================================
	def test_dp_hdmi_hdmi(self):
		self.watch('dp', 'hdmi', 'hdmi')
		self.check(None, None, ('mac', 'mdp'))

	def test_dp_hdmi_mdp(self):
		self.watch('dp', 'hdmi', 'mdp')
		self.check(None, None, ('laptop', 'usb-c'))

	def test_dp_hdmi_dp(self):
		self.watch('dp', 'hdmi', 'dp')
		self.check(None, None, None)


	def test_dp_dp_hdmi(self):
		self.watch('dp', 'dp', 'hdmi')
		self.check(None, ('laptop', 'usb-c'), ('mac', 'mdp'))

	def test_dp_dp_mdp(self):
		self.watch('dp', 'dp', 'mdp')
		self.check(None, ('laptop', 'usb-c'), ('laptop', 'usb-c'))

	def test_dp_dp_dp(self):
		self.watch('dp', 'dp', 'dp')
		self.check(None, ('laptop', 'usb-c'), None)


	def test_dp_mdp_hdmi(self):
		self.watch('dp', 'mdp', 'hdmi')
		self.check(None, None, ('mac', 'mdp'))

	def test_dp_mdp_mdp(self):
		self.watch('dp', 'mdp', 'mdp')
		self.check(None, None, None)

	def test_dp_mdp_dp(self):
		self.watch('dp', 'mdp', 'dp')
		self.check(None, None, None)

	#### DP =====================================

if __name__ == '__main__':
	# Right now it tests my specific configuration, these should
	# be hard coded.
	CABLES, DEVICES, CONNECTIONS = load()
	unittest.main()