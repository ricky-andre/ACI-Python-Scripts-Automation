# ACI_automate_scripts

Automation has always been a goal for me. For companies like Facebook or Google that are born as 'software companies', automation has been performed much before SDN marketing stuff became the new trendy thing to do. In most of the other cases, managers are usually concerned about money, and about jobs being done, it doesn't matter how. Even in service providers, where most of the activities are thought once and done many times around the country (swapping PEs, swapping CEs, software upgrades ...), automation is hard to be seen as a management choice: this would mean hiring people writing, developing, and managing software, apps and scripts, that need to be maintained during time because things always change ... i.e. hiring people whose skills do not have something to do with their core business. Usually consultants are hired to manage all the most boring jobs.
Automation is very often an advantage only for the people doing it: they can perform complex, boring, long tasks with a simple click, without doing any mistake (on live environments mistakes can be a real COST ... ), gaining a lot of time to do something else.

This is a collection of python scripts and classes, to automatically manage queries and configurations
for Cisco ACI data centers through REST APIs. The main class to perform queries has been copied from another
github project, together with the json template files:

https://github.com/carlmontanari/acipdt

The tool is quite straightforward, it is a collection of classes, one for each 'scope', each of them defining many functions for every 'atomic query'. Each function loads the json template file and replaces configuration variables with the passed parameters. A few contributors added some more fcuntions and template files, but 99% of the work was done by Carl (of course he's also the project's brain).

I have added a couple of query functions on my own (there's a pending pull request on his project), to retrieve useful information from the fabric. Everything is in this file:
<B>"Aci_Cal_Toolkit.py"</B>,

The script <B>"from_nexus_to_excel_vlan_list.py"</B> parses a few Nexus configuration files passed as parameters, and provides an excel file containing a lot of useful information about subents, vlans, vrf, hsrp groups and so on. The idea is that of using such a file to 'easily' produce another excel file containing the all the input data for ACI configuration (tenant, vrf, bd, epg, anp, ports to which an epg is binded). Excel files are useful because you can use the filter functions, and copy/paste rows/columns to obtain the desired new excel file. This can be very useful when migrations of big data centers need to be performed. A lot of time could be saved, to avoid creating manually hundreds or thousands of objects, which would be a boring, time cosuming and error-prone task. I have uploaded a picture just to give and idea of the output. Vrf names and data haave been changed for 'privacy reasons'.

The script <B>"from_vlan_list_to_aci.py"</B> is the 'heart' of the job. This is in my opinion very well commented and understandable, if you already have some python knowledge. Basicly it reads the data row by row, checks for possible, clear and trivial configuration mistakes or errors, and if necessary (i.e. if the object does not already exists) performs REST queries to the APIC. Based upon the response code (success/failure), it colors the excel cell foreground (green = ok, red = failure, yellow = no need to perform the query). The output is wrote on a new excel file with the "_out" suffix on the filename. You can find an example of the excel file uploaded here "ACI_vlan_list.xlxs" (it contains an example output of the previous mentioned script in the "Network" tab, and the input to this script in the "ACI translate" tab).

Obviously, use the scripts <B>at your own risk</B>. Remember that there is a PUSH_TO_APIC flag in the Aci_Cal_Toolkit.py file, the first time set it to False to test what happens without performing real queries.

The script <B>"create_switch_profiles.py"</B> retrieves all the leafs in the fabric, and automates the creation of:
- a switch profile using the node-ID for every switch
- a switch selector containing that single switch
- an interface profile with the node-ID
- a switch profile for every couple of consecutive switches
- a switch selector containing the two consecutive switches
- an interface profile with the two node-ID

For example, if the two nodes have id 141 and 142 the following objects will be created:

- "mo/uni/infra/accportprof-Leaf-141-142_IntProf"
- "mo/uni/infra/nprof-Leaf-141-142_LeafProf"
- "uni/infra/nprof-Leaf-141-142_LeafProf/leaves-Leaf-141-142_SwSel-typ-range"

(same objects for single node 141 and node 142)

This is useful in case the fabric is designed to have vpc only toward two consecutive switches: you would create interface selectors with vpc policies, associating it under the desired interface profile. For devices connected to single hosts, you can use the other profiles.
