import openstack

conn = openstack.connect('otc')

images = list(conn.image.images())
servers = list(conn.compute.servers())

print(images)
