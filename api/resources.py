class ResourceType:
    def __init__(self, res_id, name):
        self.id = res_id
        self.name = name

    def __str__(self):
        return self.name


class Resources:
    wood = ResourceType(0, 'Woodcutter')
    clay = ResourceType(1, 'Clay Pit')
    iron = ResourceType(2, 'Iron Mine')
    crop = ResourceType(3, 'Cropland')

    @classmethod
    def get_resource(cls, name):
        for res in [cls.wood, cls.clay, cls.iron, cls.crop]:
            if name == res.name:
                return res


class ResourceInstance:
    def __init__(self, resource, lvl, location_id):
        self.resource = resource
        self.lvl = lvl
        self.location_id = location_id

    def __str__(self):
        return "{0}\t{1} @ {2}".format(self.resource, self.lvl, self.location_id)


class VillageResources:
    def __init__(self):
        self.locations = []
        self.production = [0, 0, 0, 0]

        self.stored = [0, 0, 0, 0]
        self.capacity = [0, 0, 0, 0]
        self.wheat_consumption = 0

    def __str__(self):
        s = ""
        for location in self.locations:
            s = s + str(location) + "\n"
        s = s + "production: {0}\n".format(self.production)
        s = s + "stored: {0}\n".format(self.stored)
        s = s + "capacity: {0}\n".format(self.capacity)
        s = s + "wheat_consumption: {0}\n".format(self.wheat_consumption)
        return s


def parse_resources(soup):
    village = VillageResources()

    for index, raw_res in enumerate(soup.findAll('area', {'shape': 'circle'})[0:18]):
        [res_name, res_lvl] = str(raw_res.get('alt')).split(' level ')
        res = Resources.get_resource(res_name)

        instance = ResourceInstance(res, int(res_lvl), index + 1)
        village.locations.append(instance)

    for index, raw_res in enumerate(soup.find('table', {'id': 'production'}).findAll('td', {'class': 'num'})):
        prod_str = raw_res.string
        prod = 0
        for part in prod_str.split(','):
            prod = prod * 1000 + int(part)

        village.production[index] = prod

    [stored, consumption] = soup.find('div', {'id': 'resWrap'}).findAll('tr')
    for index, raw_prod in enumerate(stored.findAll('td')[1::+2]):
        [stored, capacity] = raw_prod.string.split('/')
        village.stored[index] = int(stored)
        village.capacity[index] = int(capacity)

    [wheat_consumption, wheat_production] = consumption.findAll('td')[2].string.split('/')
    village.wheat_consumption = int(wheat_consumption)
    return village