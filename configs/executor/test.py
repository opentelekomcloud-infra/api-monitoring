import openstack

conn = openstack.connect('otc')

images = list(conn.image.images())

print(images)
