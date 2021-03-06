from unittest import TestCase

from tests.utils import *
from api.credentials import init_credentials
from api.village import Village
from api.account import Account
from api.assets import Unit, Building
import api.actions as actions


class Test(TestCase):
    def test_move_units(self):
        credentials = init_credentials('../configs/credentials_dynamic_login.json')

        own_uid = credentials.get_own_uid()
        account = Account(own_uid)
        account.update_villages(credentials)

        village = account.get_village_by_vid(4007)
        village.force_update(credentials)

        target_village = Village(account=None, vid=3609, name="")

        actions.move_units(credentials, Unit.raid, village, target_village, units={Unit.imperatoris: 1000})

    def test_catapult_attack(self):
        credentials = init_credentials('../configs/credentials_dynamic_login.json')

        own_uid = credentials.get_own_uid()
        account = Account(own_uid)
        account.update_villages(credentials)

        village = account.get_village_by_vid(4007)
        village.force_update(credentials)

        target_village = Village(account=None, vid=3807, name="")

        try:
            actions.move_units(credentials, Unit.attack_normal, village, target_village,
                               units={Unit.imperatoris: 1000, Unit.roman_catapult: 10},
                               catapult_buildings=[Building.mainB, Building.warehouse])
            assert False
        except actions.ActionException as e:
            assert_str(e, "ActionException('Expected 1 catapult target(s) but got 2')")

        try:
            actions.move_units(credentials, Unit.attack_normal, village, target_village,
                               units={Unit.imperatoris: 1000, Unit.roman_catapult: 20},
                               catapult_buildings=[Building.mainB])
            assert False
        except actions.ActionException as e:
            assert_str(e, "ActionException('Expected 2 catapult target(s) but got 1')")

        try:
            actions.move_units(credentials, Unit.attack_normal, village, target_village,
                               units={Unit.imperatoris: 1000, Unit.roman_catapult: 10},
                               catapult_buildings=[])
            assert False
        except actions.ActionException as e:
            assert_str(e, "ActionException('Expected 1 catapult target(s) but got 0')")

        try:
            actions.move_units(credentials, Unit.attack_normal, village, target_village,
                               units={Unit.imperatoris: 1000, Unit.roman_catapult: 20})
            assert False
        except actions.ActionException as e:
            assert_str(e, "ActionException('Expected 2 catapult target(s) but got none')")

        return

        # TODO(@alexvelea) move troops does not provide a K. Find a way to get it

        # actions.move_units(credentials, Unit.raid, village, target_village,
        #                    units={Unit.imperatoris: 1000, Unit.roman_catapult: 30})
        #
        # actions.move_units(credentials, Unit.attack_normal, village, target_village,
        #                    units={Unit.imperatoris: 1000, Unit.roman_catapult: 20},
        #                    catapult_buildings=[Building.granary, Building.warehouse])
        #
        # actions.move_units(credentials, Unit.attack_normal, village, target_village,
        #                    units={Unit.imperatoris: 1000, Unit.roman_catapult: 15},
        #                    catapult_buildings=[Building.mainB])
        #
        # # Something is fishy here. Village had 2 buildings, an embassy(lvl 1) and a cranny(lvl 1) and only the embassy
        # # was destroyed. Is it a bug from the server side?
        # actions.move_units(credentials, Unit.attack_normal, village, target_village,
        #                    units={Unit.imperatoris: 1000, Unit.roman_catapult: 20},
        #                    catapult_buildings=[Building.random_target, Building.random_target])

    def test_train(self):
        credentials = init_credentials('../configs/credentials_dynamic_login.json')

        own_uid = credentials.get_own_uid()
        account = Account(own_uid)
        account.update_villages(credentials)

        village = account.get_village_by_vid(4007)
        village.force_update(credentials)

        try:
            actions.train(credentials, village,
                          units={Unit.imperian: 4})
            assert False
        except actions.ActionException as e:
            assert_str(e, """ActionException("Required building Barracks for training ['Imperian']")""")

        actions.train(credentials, village,
                      units={Unit.legati: 4, Unit.imperatoris: 5, Unit.caesaris: 6,
                             Unit.roman_ram: 7})

    # TODO(@alexvelea) find a way to test this!
    def test_research(self):
        credentials = init_credentials('../configs/credentials_dynamic_login.json')

        own_uid = credentials.get_own_uid()
        account = Account(own_uid)
        account.update_villages(credentials)

        village = account.get_village_by_vid(4007)
        village.force_update(credentials)

        actions.research_unit(credentials, village, Unit.praetorian)

    # TODO(@alexvelea) find a way to test this!
    def test_upgrades(self):
        credentials = init_credentials('../configs/credentials_dynamic_login.json')

        own_uid = credentials.get_own_uid()
        account = Account(own_uid)
        account.update_villages(credentials)

        village = account.get_village_by_vid(4007)
        village.force_update(credentials)

        actions.upgrade_attack(credentials, village, Unit.imperian)
        actions.upgrade_defence(credentials, village, Unit.imperian)
