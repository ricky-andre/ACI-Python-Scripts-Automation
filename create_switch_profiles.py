from Aci_Cal_Toolkit import FabLogin, Query, FabAccPol
from credentials import apic_ip, apic_pwd, apic_user

# to avoid using Acitoolkit
apic = FabLogin (apic_ip, apic_user, apic_pwd)
cookies = apic.login()
print('Logged into apic ...')

print('Retrieving existing leafs ...')
req = Query(apic_ip, cookies)
[status, payload] = req.query_url('/api/node/class/fabricNode.json?'
            'query-target-filter=eq(fabricNode.role,"leaf")')

leafs = {}
if (status == 200):
    for node in payload['imdata']:
        leafs[node['fabricNode']['attributes']['id']] = node['fabricNode']['attributes']['name']
else:
    print ('Error for query response code :' + status)

fabric = FabAccPol (apic_ip, cookies)

# checking for existent interface profiles
print('Retrieving interface profiles ...')
int_prof = {}
[status, payload] = req.query_class('infraAccPortP')
if (status == 200):
    for obj in payload['imdata']:
        name = obj['infraAccPortP']['attributes']['name']
        int_prof[name] = 'uni/infra/accportprof-' + name

print('Checking for single-switch interface profile missing ... ')
for node_id in leafs:
    if not 'Leaf-'+node_id+'_IntProf' in int_prof:
        print ('Switch interface profile for leaf '+node_id+' has to be created')
        status = fabric.int_profile(name='Leaf-'+node_id+'_IntProf', 
                                    status='created')
        if (status==200):
            print('Missing single switch interface profile has been created')
        else:
            print('Error creating missing profile switch')

print('Checking for double-switch interface profile missing ... ')
new_couple = 0
old_id = 0
for node_id in sorted(leafs):
    if not new_couple:
        old_id = node_id
        new_couple = 1
    else:
        new_couple = 0
        if not 'Leaf-'+old_id+'-'+node_id+'_IntProf' in int_prof:
            print ('Switch interface profile "Leaf-'+old_id+'-'+node_id+'_IntProf" has to be created')
            status = fabric.int_profile(name= 'Leaf-'+old_id+'-'+node_id+'_IntProf',
                                       status= 'created')
            if (status==200):
                print('Missing vpc switch interface profile has been created')
            else:
                print('Error creating missing vpc interface profile switch')


print('Retrieving switch profiles ...')
sw_prof = {}
[status, payload] = req.query_class('infraNodeP')
if (status == 200):
    for obj in payload['imdata']:
        name = obj['infraNodeP']['attributes']['name']
        sw_prof[name] = 'uni/infra/nprof-' + name

# we now create with a post, a switch profile with a switch selector,
# then we add the interface profile.
print('Checking for single switch profile missing ... ')
for node_id in leafs:
    sw_prof_name = 'Leaf-'+node_id+'_LeafProf'
    sw_sel_name = 'Leaf-'+node_id+'_SwSel'
    sw_int_prof = 'Leaf-'+node_id+'_IntProf'
    if not sw_prof_name in sw_prof:
        print ('Switch profile for '+leafs[node_id]+' has to be created')
        status = fabric.swPro_swSel_single(name = sw_prof_name,
                                           swSelName = sw_sel_name,
                                           status='created', 
                                           sw1=str(node_id))
        if (status==200):
            print('Missing single switch profile has been created')
            status = fabric.int_prof_to_sw_profile(name = sw_prof_name,
                                                    status = 'created',
                                                    int_profile = sw_int_prof)
            if (status==200):
                print('Interface profile added to switch profile')
            else:
                print('Error adding interface profile to switch profile')
        else:
            print('Error creating missing profile switch')

# we now create with a post, a switch profile with a switch selector,
# then we add the interface profile.
print('Checking for "pair" switch profile missing ... ')
new_couple = 0
old_id = 0
for node_id in sorted(leafs):
    if not new_couple:
        old_id = node_id
        new_couple = 1
    else:
        new_couple = 0
        sw_prof_name = 'Leaf-'+old_id+'-'+node_id+'_LeafProf'
        sw_sel_name = 'Leaf-'+old_id+'-'+node_id+'_SwSel'
        sw_int_prof = 'Leaf-'+old_id+'-'+node_id+'_IntProf'
        if not 'Leaf-'+old_id+'-'+node_id+'_LeafProf' in sw_prof:
            print ('Switch profile for "Leaf-'+old_id+'-'+node_id+'_LeafProf" has to be created')
            status = fabric.swPro_swSel_vpc(name = sw_prof_name,
                                            swSelName = sw_sel_name,
                                            status = 'created,modified',
                                            sw1 = old_id,
                                            sw2 = node_id)
            if (status==200):
                print('Missing "pair" switch profile and selector has been created')
                status = fabric.int_prof_to_sw_profile(name = sw_prof_name,
                                                       status = 'created',
                                                       int_profile = sw_int_prof)
                if (status==200):
                    print('Interface profile added to switch profile')
                else:
                    print('Error adding interface profile to switch profile')
            else:
                print('Error creating missing vpc profile switch')
