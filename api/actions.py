import assets
from .credentials import Page


class ActionException(Exception):
    pass


def throw_catapult_warnings(move_type, village, units, catapult_buildings):
    if move_type != assets.Unit.attack_normal:
        return

    if units.get(assets.Unit.roman_catapult, 0) == 0:
        if len(catapult_buildings):
            raise ActionException('Catapult buildings specified but no catapults found')

    if village.buildings.find(assets.Building.rally)[0].lvl == 20 and units.get(assets.Unit.roman_catapult) >= 20:
        num_targets = 2
    else:
        num_targets = 1

    if catapult_buildings is None:
        raise ActionException(f'Expected {num_targets} catapult target(s) but got none')

    if len(catapult_buildings) == num_targets:
        return

    raise ActionException(f'Expected {num_targets} catapult target(s) but got {len(catapult_buildings)}')


# TODO(@alexvelea) If the rally point is lvl 20 no K is present on the returned page.
def move_units(credentials, move_type, village, target_village, units, catapult_buildings=None):
    throw_catapult_warnings(move_type, village, units, catapult_buildings)

    params = {'vid': village.vid}
    data = {'s1.x': '0', 's1.y': '0', 'c': str(move_type), 'k': village.k, 'id': target_village.vid}
    t = [0] * 11
    for (unit, num) in units.items():
        t[unit.uid] = max(num, 0)
    for i in range(1, 11):
        data[f't[{i}]'] = str(t[i])

    if catapult_buildings is not None:
        for index, building in enumerate(catapult_buildings):
            data['dtg' + ('' if index == 0 else '1')] = building.bid

    assert village.k is not None
    soup = credentials.call(page=Page.move_troops, params=params, data=data)
    village.k = None
    village.update_from_soup(soup)


def simple_building_action(credentials, village, building, a):
    params = {'k': village.k, 'id': building.location_id, 'a': a}

    assert village.k is not None
    soup = credentials.call(page=Page.building, params=params)
    village.k = None
    village.update_from_soup(soup)


def upgrade_attack(credentials, village, unit):
    b = next(iter(village.buildings.find(assets.Building.blacksmith)), None)
    if b is None:
        raise ActionException(
            f'Required building {assets.Building.blacksmith} for upgrading the attack of {unit}')

    simple_building_action(credentials, village, b, unit.uid)


def upgrade_defence(credentials, village, unit):
    b = next(iter(village.buildings.find(assets.Building.armoury)), None)
    if b is None:
        raise ActionException(
            f'Required building {assets.Building.armoury} for upgrading the defence of {unit}')

    simple_building_action(credentials, village, b, unit.uid)


def research_unit(credentials, village, unit):
    b = next(iter(village.buildings.find(assets.Building.academy)), None)
    if b is None:
        raise ActionException(
            f'Required building {assets.Building.academy} for researching {unit}')

    simple_building_action(credentials, village, b, unit.uid)


# TODO(@alexvelea): Test if the units are researched
# TODO(@alexvelea): Test if the required number resources are met
def train(credentials, village, units):
    train_buildings = {}
    for unit, num in units.items():
        if num <= 0:
            continue

        train_buildings.setdefault(unit.train_building, []).append((unit, num))

    for building, units in train_buildings.items():
        b = next(iter(village.buildings.find(building)), None)
        if b is None:
            raise ActionException(f'Required building {building} for training {units}')

        params = {'vid': village.vid, 'id': b.location_id}
        data = {'s1.x': '1', 's1.y': '1'}
        for unit, num in units:
            data[f'tf[{unit.uid}]'] = str(num)

        soup = credentials.call(page=Page.building, params=params, data=data)
        village.update_from_soup(soup)


def upgrade_building(credentials, village, location_id):
    page = Page.overview if location_id <= 18 else Page.center

    building = village.buildings[location_id]
    old_lvl = building.lvl
    old_plus_lvl = building.lvl
    old_k = village.k

    assert village.k is not None
    soup = credentials.call(page=page, params={'vid': village.vid, 'id': location_id, 'k': village.k})
    village.update_from_soup(soup)

    if old_lvl + old_plus_lvl == building.lvl + building.plus_lvl:
        return False

    if village.k == old_k:
        village.k = None
    return True


def construct_building(credentials, village, location_id, building):
    # TODO(@alexvelea) Rethink this for granary/warehouse
    # Check if building is already constructed
    if len(village.buildings.find(building)):
        raise Exception

    # Make sure the spot it's empty
    if village.buildings[location_id].name != assets.Building.empty.name:
        raise Exception

    assert village.k is not None
    old_k = village.k
    soup = credentials.call(page=Page.center,
                            params={'vid': village.vid, 'id': location_id, 'b': building.bid, 'k': village.k})
    village.update_from_soup(soup)
    new_building = village.buildings[location_id]

    if new_building.plus_lvl == 1 and new_building.lvl == 0:
        if village.k == old_k:
            village.k = None
        return True

    return False


# demo does not use K
def demolish_building(credentials, village, location_id):
    main_building = next(iter(village.buildings.find(assets.Building.mainB)), None)
    if main_building is None:
        raise Exception

    if main_building.lvl < 10:
        raise Exception

    soup = credentials.call(page=Page.building, params={'vid': village.vid, 'id': main_building.location_id}, data={'drbid': location_id, 'ok.x': 0, 'ok.y': 0})
    village.update_from_soup(soup)

    return True


def host_celebration(credentials, village, celebration_type):
    town_hall = next(iter(village.buildings.find(assets.Building.hall)), None)
    if town_hall is None:
        raise Exception

    if celebration_type.cid == assets.Celebration.big.cid:
        if town_hall.lvl < 10:
            raise Exception

    simple_building_action(credentials, village, town_hall, celebration_type.cid)


def send_resources(credentials, village, target_village, resources):
    market = next(iter(village.buildings.find(assets.Building.marketplace)), None)

    if market is None:
        raise Exception

    params = {'id': market.location_id, 'vid': village.vid}
    data = {
        'act': '2',
        'vid2': target_village.vid,
        's1.x': '1',
        's1.y': '1'
    }

    for index, num_res in enumerate(resources):
        num_res = max(num_res, 0)
        data[f'r{index+1}'] = num_res

    soup = credentials.call(page=Page.building, params=params, data=data)
    village.update_from_soup(soup)
