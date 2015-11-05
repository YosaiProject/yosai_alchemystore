from yosai_alchemystore import (
    engine,
    Base,
    Session,
    User,
    Domain,
    Action,
    Resource,
    Permission,
    Role,
)

Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
import pprint
pp = pprint.PrettyPrinter(indent=1)

# Please watch 'The Big Lebowski' so that you may understand the following data.
users = [User(first_name='Jeffrey', last_name='Lebowski', identifier='thedude'),
         User(first_name='Walter', last_name='Sobchak', identifier='walter'),
         User(first_name='Larry', last_name='Sellers', identifier='larry'),
         User(first_name='Jackie', last_name='Treehorn', identifier='jackie'),
         User(first_name='Karl', last_name='Hungus', identifier='karl'),
         User(first_name='Marty', last_name='Houston', identifier='marty')]

domains = [Domain(name='money'),
           Domain(name='leatherduffelbag')]

actions = [Action(name='write'),
           Action(name='deposit'),
           Action(name='transport'),
           Action(name='access'),
           Action(name='withdrawal'),
           Action(name='bowl'),
           Action(name='run')]

resources = [Resource(name='theringer'),
             Resource(name='ransom'),
             Resource(name='bankcheck_19911109069')]

roles = [Role(title='courier'),
         Role(title='tenant'),
         Role(title='landlord'),
         Role(title='thief'),
         Role(title='bankcustomer')]

session = Session()
session.add_all(users + roles + domains + actions + resources)

users = dict((user.first_name+'_'+user.last_name, user) for user in session.query(User).all())
domains = dict((domain.name, domain) for domain in session.query(Domain).all())
actions = dict((action.name, action) for action in session.query(Action).all())
resources = dict((resource.name, resource) for resource in session.query(Resource).all())
roles = dict((role.title, role) for role in session.query(Role).all())

perm1 = Permission(domain=domains['money'],
                   action=actions['write'],
                   resource=resources['bankcheck_19911109069'])

perm2 = Permission(domain=domains['money'],
                   action=actions['deposit'])

perm3 = Permission(domain=domains['money'],
                   action=actions['access'],
                   resource=resources['ransom'])

perm4 = Permission(domain=domains['leatherduffelbag'],
                   action=actions['transport'],
                   resource=resources['theringer'])

perm5 = Permission(domain=domains['leatherduffelbag'],
                   action=actions['access'],
                   resource=resources['theringer'])

perm6 = Permission(domain=domains['money'],
                   action=actions['withdrawal'])

perm7 = Permission(action=actions['bowl'])

perm8 = Permission(action=actions['run'])  # I dont know!?

session.add_all([perm1, perm2, perm3, perm4, perm5, perm6, perm7, perm8])

bankcustomer = roles['bankcustomer']
courier = roles['courier']
tenant = roles['tenant']
landlord = roles['landlord']
thief = roles['thief']

bankcustomer.permissions.extend([perm2, perm7, perm8])
courier.permissions.extend([perm4, perm7, perm8])
tenant.permissions.extend([perm1, perm7, perm8])
thief.permissions.extend([perm3, perm4, perm5, perm7, perm8])
landlord.permissions.extend([perm6, perm7, perm8])

thedude = users['Jeffrey_Lebowski']
thedude.roles.extend([bankcustomer, courier, tenant])

walter = users['Walter_Sobchak']
walter.roles.extend([bankcustomer, courier])

marty = users['Marty_Houston']
marty.roles.extend([bankcustomer, landlord])

larry = users['Larry_Sellers']
larry.roles.extend([bankcustomer, thief])  # yes, I know, it's not confirmed

jackie = users['Jackie_Treehorn']
jackie.roles.extend([bankcustomer, thief])  # karl may be working for him-- close enough

karl = users['Karl_Hungus']
karl.roles.extend([bankcustomer, thief])

session.commit()

pp.pprint(karl.permissions)

session.close()
