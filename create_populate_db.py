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

Base.metadata.create_all(engine)

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
           Action(name='withdrawal')]

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
session.commit()

users = dict((user.first_name+'_'+user.last_name, user) for user in session.query(User).all())
domains = dict((domain.name, domain) for domain in session.query(Domain).all())
actions = dict((action.name, action) for action in session.query(Action).all())
resources = dict((resource.name, resource) for resource in session.query(Resource).all())
roles = dict((role.title, role) for role in session.query(Role).all())

perm1 = Permission(domain=domains['money'],
                   action=actions['write'],
                   resource=resources['bankcheck_19911109069']),

perm2 = Permission(domain=domains['money'],
                   action=actions['deposit']),

perm3 = Permission(domain=domains['money'],
                   action=actions['access'],
                   resource=resources['ransom']),

perm4 = Permission(domain=domains['leatherduffelbag'],
                   action=actions['transport'],
                   resource=resources['theringer']),

perm5 = Permission(domain=domains['leatherduffelbag'],
                   action=actions['open'],
                   resource=resources['theringer'])

perm6 = Permission(domain=domains['money'],
                   action=actions['withdrawal'])

bankcustomer = roles['bankcustomer']
courier = roles['courier']
tenant = roles['tenant']
landlord = roles['landlord']
thief = roles['thief']

bankcustomer.permissions.append(perm2)
courier.permissions.append(perm4)
tenant.permissions.append(perm1)
thief.permissions.append(perm3, perm4, perm5)
landlord.permissions.append(perm6)
session.commit()

thedude = users['Jeffrey_Lebowski']
thedude.roles.append(bankcustomer, courier, tenant)

walter = users['Walter_Sobchak']
walter.roles.append(bankcustomer, courier)

marty = users['Marty_Houston']
marty.roles.append(bankcustomer, landlord)

larry = users['Larry_Sellers']
larry.roles.append(bankcustomer, thief)  # yes, I know, it's not confirmed

jackie = users['Jackie_Treehorn']
jackie.roles.append(bankcustomer, thief)  # karl may be working for him, close enough

karl = users['Karl_Hungus']
karl.roles.append(bankcustomer, thief)

session.commit()
session.close()
