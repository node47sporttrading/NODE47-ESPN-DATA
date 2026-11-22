import unittest
from node47_espn.multisport_decision import robot_stake

class RobotStakingParityTests(unittest.TestCase):
    def test_confidence_penalty_and_profile_cap(self):
        result=robot_stake("football",0.60,80,2.0,profile="STANDARD")
        self.assertAlmostEqual(result["p_cons"],0.59)
        self.assertAlmostEqual(result["f_star"],0.18)
        self.assertEqual(result["stake_u"],3.0)

    def test_push_probability_changes_kelly_fraction(self):
        self.assertEqual(robot_stake("football",0.50,100,2.0,profile="STANDARD")["decision"],"NO BET")
        self.assertEqual(robot_stake("football",0.50,100,2.0,p_push=0.10,profile="STANDARD")["stake_u"],2.5)

    def test_missing_confidence_gets_full_penalty(self):
        result=robot_stake("tennis",0.60,None,2.0,profile="STANDARD")
        self.assertAlmostEqual(result["p_cons"],0.55)

    def test_profile_caps_are_not_globally_clamped_to_one_unit(self):
        self.assertEqual(robot_stake("basketball",0.80,100,2.0,profile="PRUDENT")["stake_u"],2.0)
        self.assertEqual(robot_stake("basketball",0.80,100,2.0,profile="STANDARD")["stake_u"],3.0)

    def test_custom_requires_stake_max(self):
        with self.assertRaises(ValueError):
            robot_stake("corners_cartons",0.70,80,2.0,profile="CUSTOM")

if __name__ == "__main__": unittest.main()
