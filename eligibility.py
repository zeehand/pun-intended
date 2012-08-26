import csv
import pdb
import sys
import fnmatch

args = sys.argv[1:]

# files to import
alloc_file = args[0]
assortment_file = 'assortment_v8.csv'
box_constraints_file = 'boxconstraints_v8.csv' #
scores_table = 'soft_constraints_v2.csv'
already_purchased_file = 'purchasers.csv' # purchased the products list
# haters lists
output_file = args[1]


numboxes = 0
numsamples = 0
assortment = {} # <'box num'> : ['1', '8', '12' ... ]
all_samples = {}  # RESULTS IN A DICT OF ALL PRODUCTS: <sample num>: product
people = {}
inf = 1000000
fail_score = inf - 1000
box_history_field = 'birchbox_list'


class product:
	name = ''
	msrp = 0
	vendor = ''
	sampleval = 0
	sku = ''
	# sample_num =-1
	boxconstraints = {}
	# a box constraints dict should be of type '1':['34','235','236','237']
	purchasers = []
	# list of customer id's who have purchased the product before
	pointvals = {}
	# will be a dict of type {<trait name>: <score>}



# *********** READ IN THE ASSORTMENT ***********

file = open(assortment_file, 'rb')
myreader = csv.reader(file)

box = 1

for row in myreader:
	if row[0] != '':
		box = row[0]
		assortment[box] = []
		if int(row[0]) > numboxes: numboxes = int(row[0])
	assortment[box].append(row[1])
	if int(row[1]) > numsamples: numsamples = int(row[1])
#	if str(row[1]) not in all_samples: all_samples[str(row[1])] = 

file.close()
#sample_indices = [str(i) for i in range(1, numsamples +1)]
#box_indices = [str(i) for i in range(1, numboxes + 1)]

#print assortment
#print 'samples: ' + str(samples)
#print 'boxtypes: ' + str(boxtypes)

# ********* READ IN THE PRODUCTS AND BOX CONSTRAINTS ************

#pdb.set_trace()

file = open(box_constraints_file, 'rb')
myreader = csv.reader(file)
#header = myreader.next()
cur_prod = ''
tol = '1' # default threshold is any 1 box from list is a constraint
for row in myreader:
	if row[0] != '':
		cur_prod = str(row[0])
		new_prod = product()
		new_prod.boxconstraints = {}
		new_prod.boxconstraints[tol] = [] 
		new_prod.name = row[3]
		#print new_prod.name + '\n'
		new_prod.vendor = row[2]
		#print new_prod.vendor + '\n'
		all_samples[cur_prod] = new_prod
	#if row[4] not in all_samples[n].boxconstraints:
	all_samples[cur_prod].boxconstraints[tol].append(row[1])
	#print str(row[1]) + ' has been added to '+ all_samples[cur_prod].name + '\'s list of no-no boxes'
	#print all_samples[cur_prod].name + ' now has these boxes in it\'s list: ' + str(all_samples[cur_prod].boxconstraints)

#for i in all_samples:
	#cur_samp = all_samples[i]
	#print cur_samp.name + '\'s box constraints are ' + str(cur_samp.boxconstraints)

file.close()

#Multiple times

x3hairoil = ['119', '121', '179', '273', '286', '287', '288', '289', '290', '344', '436', '437', '438', '442', '447', '471', '473', '478', '479', '518', '519', '524', '525', '526', '530', '531', '541', '600', '608', '610', '613', '634', '637', '648', '650', '651', '652', '653', '681', '682', '683', '695', '735', '737', '742', '750', '758', '759', '802', '825', '865', '867', '868', '877', '878', '907', '937', '1035', '1051']

all_samples['43'].boxconstraints['3'] = x3hairoil

	

#  ************ SOFT CONSTRAINT POINTS  ************
#START BY MAKING A DICTIONARY OF ALL POSSIBLE ANSWERS

all_traits = {}
class trait:
	index = -1
	q = ''
	val = ''
	points = {} # will be an array of type <product>: score

#for row in new_rd:
#	cur_trait = trait()
#	cur_trait.index = row[2]
#	cur_trait.q = row[0]
#	cur_trait.val = row[1]
#	cur_trait.points = {}
	#all_traits[row[2]] = cur_trait

# THEN IMPORT THE TABLE OF POINT VALUES VS. TRAITS
# will be of type <name>: [array of products]



# ******* READ IN THE PEOPLE *********


class person:
	sub_id = -1
	traits = {} # raw text from all_alloc
	expanded_traits = {}  # binary vector for all attributes
	prod_elig = {} #dict(zip(sample_indices, [0] * numsamples))
	box_elig = {} #dict(zip(box_indices,[0] * numboxes))


file = open(alloc_file,'rb')
myreader = csv.reader(file)
profile_qs = myreader.next()


#make a dictionary of all people where the key is the sub_id and the the values is a dict of traits
print 'Reading in the source files (including profile data)...'
for row in myreader:
	cust = person()
	cust.traits = dict(zip(profile_qs, row))
	if cust.traits['beauty_age'].isdigit():
		cust_age = int(cust.traits['beauty_age'])
	else: cust_age = -1
	cust.traits['age_over'] = ''
	cust.traits['age_under'] = ''
	#add age constraints
	if cust_age in range (10,100):
		for i in range (10,60):
			if cust_age >= i: cust.traits['age_over'] = cust.traits['age_over'] + ',' + str(i)
			if cust_age <= i: cust.traits['age_under'] = cust.traits['age_under'] + ',' + str(i)

	cust.sub_id = row[2]
	people[row[2]] = cust

file.close()


# ******** CREATE SOFT CONSTRAINTS ***********


class soft_constraint:
	sample_id = '-1'
	question = ''
	option = ''
	value = ''
	num_affected = 0

def print_soft_constraint(con):
	print 'Sample: ' + con.sample_id + '; Question: ' + con.question + '; Option: ' + con.option + '; Earns ' + con.value + ' points'

def printing_on(sub):
	return False # sub == '3112'

all_soft_constraints = []

file = open(scores_table,'rb')
myreader = csv.reader(file)
header = myreader.next()
for row in myreader:
	attribute = row[0]
	#if attribute not in profile_qs:
		#print 'warning, ' + attribute + ' is not found in the alloc file'
	option = row[1]
	for i in range(3,len(row)):
		if row[i] != '0':
			cur_constraint = soft_constraint()
			cur_constraint.sample_id = header[i]
			cur_constraint.question = attribute
			cur_constraint.option = option
			cur_constraint.value = row[i]
			all_soft_constraints.append(cur_constraint)
			
#for con in all_soft_constraints:
#	print 'sample ' + con.sample_id + '; question-'+ con.question + '; option-' + con.option + '; value-' + con.value

file.close()

# ******* CREATE PURCHASED THE PRODUCT LIST ********

purchase_list = {} # dict of customer_id -> vector of products purchased

file = open(already_purchased_file,'rb')
myreader = csv.reader(file)
header = myreader.next()
cur_cust = 0
for row in myreader:
	if row[0] != '':
		cur_cust = row[0]
		purchase_list[cur_cust] = []
	purchase_list[cur_cust].append(row[1])
	#print 'customer ' + cur_cust + ' has purchased product ' + row[1]

file.close()


# ******** HARD CONSTRAINTS *************

print 'Running all subscribers through eligibility...'
subs_done = 0
for sub in people:
	cur_pers = people[sub]
	cur_pers.prod_elig = {}
	cur_pers.box_elig = {}
	# BOX HISTORY
	# if the count of boxes found in the person's history exceeds the threshold, set prod_elig to 'NULL'

	box_hist = ',' + cur_pers.traits[box_history_field][1:] + ','
	
	#print 'looking at new customer: ' + str(cur_pers.sub_id)
	#print 'customer\'s box history is: ' + str(box_hist)
	#print 'all_samples: ' + str(all_samples.keys())
	for sample in all_samples:	
		for tols in all_samples[sample].boxconstraints: # tols will be the tolerances, 1 or more
			
			bad_boxes = all_samples[sample].boxconstraints[tols] #bad_boxes is a vector of strings
			count = 0
			for box in bad_boxes:
				if fnmatch.fnmatch(box_hist, '*,' + box + ',*'):
					count = count + 1
					#print 'box ' + str(box) +' was found in '+ str(cur_pers.sub_id) +'\'s history'
			if count >= int(tols):
				cur_pers.prod_elig[sample] = inf
	

	#print 'subscriber ' + str(cur_pers.sub_id) + '\'s list of bad products is ' + str(cur_pers.prod_elig)

###	# PROFILE
	# when checking a hard constraint make sure that any hardcoded trait is in profile_qs

	p = cur_pers.traits
	eth = p['beauty_ethnicity']
	conc = p['beauty_skin_concerns']
	hair = p['beauty_hair']
	hairc = p['beauty_hair_color']
	inc = p['beauty_household_income']
	intel = p['beauty_intel_source']
	skinc = p['beauty_skin_coloring']
	skint = p['beauty_skin_type']
	cat = p['beauty_splurge']
	style = p['beauty_styles']
	other = p['other_special_interests']
	under = p['age_under']
	over = p['age_over']
	
	e = cur_pers.prod_elig

	for i in range(1,numsamples+1):
		if str(i) not in e:
			e[str(i)] = 0

	#AA/SA
	aa_sa = eth in ['African American', 'South Asian']
	
	if aa_sa:
		e['3'] = e['3'] + inf
		e['20'] = e['20'] + inf

	#DDF
#	if '23' in under:
#		e['9'] = e['9'] + inf
	if printing_on(sub):
		print sub + ' has ' + under +' as her \'under\', and e[9] is now ' + str(e['9'])


	#Osmotics
	if '34' in under and 'Aging' not in conc:
		e['10'] = e['10'] + inf

	#Wei
	if skint not in ['Normal', 'Combination', '', 'Please Select']:
		e['11'] = e['11'] + inf

	#eyerock
	if '31' in over or ( '26' in over and not ( 'Adventurous' in style or 'Trendy' in style)):
		e['17'] = e['17'] + inf


	#stila light
	if skinc != 'Light' or aa_sa:
		e['24'] = e['24'] + inf

	
	#stila medium
	if skinc != 'Medium' or aa_sa:
		e['25'] = e['25'] + inf
		
	#stila warm
	if skinc not in ['Medium','Tan/Olive'] or eth == 'African American':
		e['26'] = e['26'] + inf


	# stila deep
	deep_ok = False
	if skinc == 'Dark': deep_ok = True
	if skinc == 'Medium' and aa_sa:  deep_ok = True
	if not deep_ok: 
		e['27'] = e['27']+inf


	#Oribe
	if 'Color-Treated' not in hair:
		e['35'] = e['35'] + inf


	#blandi
	if eth == 'African American':
		e['36'] = e['36'] + inf	
		e['37'] = e['37'] + inf
		e['38'] = e['38'] + inf


	#Leonor	
	if 'Dry' not in hair and hair not in ['Please Select', 'Normal ', '']:
		e['39'] = e['39'] + inf


	#miss jesses
	if 'Curly' not in hair: # and hair not in ['Please Select','']:
		e['45'] = e['45'] + inf
		e['48'] = e['48'] + inf

	if 'Curly' not in hair and 'Frizzy' not in hair:
		e['46'] = e['46'] + inf

#curly meringue
	if eth not in ['African American', 'Hispanic/Latino'] or 'Chemically' in hair or 'Curly' not in hair: # and 'Frizzy' not in hair):
		e['47'] = e['47'] + inf


	#commodynes
	if aa_sa or skinc == 'Dark' or eth in ['', 'Please Select']:
		e['51'] = e['51'] + inf


	#whish
#	if '23' in under:
#		e['55'] = e['55'] + inf
#		e['56'] = e['56'] + inf

	#apothederm
	if 'Stretch' not in conc and 'mother' not in other:
		e['58'] = e['58'] + inf


#  PURHCASED THE PRODUCT
	if cur_pers.traits['customer_id'] in purchase_list:
		their_buys = purchase_list[cur_pers.traits['customer_id']]
		for prod in their_buys:
			cur_pers.prod_elig[prod] = inf
			#print 'customer ' + cur_pers.traits['customer_id'] + ' purchased product ' + prod


#  SOFT CONSTRAINT POINTS
	for con in all_soft_constraints:
		if con.sample_id not in cur_pers.prod_elig:
			cur_pers.prod_elig[con.sample_id] = 0
		if con.question in cur_pers.traits:
		
			profile_val = cur_pers.traits[con.question]
			has_attribute = False
			if con.question == 'beauty_ethnicity':
				has_attribute = ( profile_val == con.option )
			else: has_attribute = fnmatch.fnmatch(profile_val, '*' + con.option + '*')
			if has_attribute:
				cur_pers.prod_elig[con.sample_id] = cur_pers.prod_elig[con.sample_id] + int(con.value)
				#if printing_on(sub):
				#	print 'adding ' + con.value + ' to subscriber ' + sub + ' because of this constraint:'
				#	print_soft_constraint(con)
				#	print 'new total for that product is ' + str(cur_pers.prod_elig[con.sample_id])
				con.num_affected = con.num_affected + 1
		#else: print "Error: " + con.question + ' not found in traits'



# ******* ROLLING EVERYTHING UP *********

	elig_boxes = 0
	for box in assortment:
		
		cur_box = assortment[box]  # cur_box is a vector of product numbers, stored as strings

	 	if box not in cur_pers.box_elig: cur_pers.box_elig[box] = 0

		for product in cur_box: # loops through the integer product numbers for that box 
			if product not in cur_pers.prod_elig:
				cur_pers.prod_elig[product] = 0
			#print 'sub # ' + str(people[sub].sub_id) + ', box #' + str(
			#if cur_pers.prod_elig[product] > inf - 1:
			#	cur_pers.box_elig[box] = cur_pers.box_elig[box] + inf
					# using box as the index since that's the key

			cur_pers.box_elig[box] = cur_pers.box_elig[box] + cur_pers.prod_elig[product]
		#print sub + ' ' + box + ' score = ' + str(cur_pers.box_elig[box])
		
		if cur_pers.box_elig[box] < fail_score:
			elig_boxes = elig_boxes + 1

#	print sub + ' is eligible for ' + str(elig_boxes) + ' boxes'
	
#  MAKE BB1 THE ANYONE BOX

	#if cur_pers.box_elig['1'] > fail_score and elig_boxes <= 1:
	cur_pers.box_elig['1'] = 0


#  PRINT STATUS 
	subs_done = subs_done + 1
	if (subs_done % 1000 == 0): print 'Completed ' + str(subs_done) + ' subscribers'

# **********WRITE OUT RESULTS CSV ****************
# where first column is sub_id and remaining columns are sub.box_elig

# determine how many constraints were met
i = 0
for con in all_soft_constraints:
	i = i+1
	#print 'Soft constraint ' + str(i) + ' for sample ' + con.sample_id + ' affected ' + str(con.num_affected) + ' people. (' + con.question + '-' + con.option + ')'

write_file = open(output_file, 'wb')
output_writer = csv.writer(write_file)

#write the header
row = ['Customer_id','Sub_id']
#box_indices = assortment.keys()
row.extend(range(1,numboxes+1))
output_writer.writerow(row)

#write a row for each person
print 'Writing File...'
for pers in people:
	#print people[pers].box_elig
	cur_pers = people[pers]
	row = []
	row.append(cur_pers.traits['customer_id'])
	row.append(cur_pers.sub_id)
	for box in range (1, numboxes+1):
		if str(box) not in assortment: row.append('NULL')
		else:
			score = cur_pers.box_elig[str(box)]
			if score > fail_score:
				row.append('NULL')
			else: 
				row.append(cur_pers.box_elig[str(box)])
	output_writer.writerow(row)
#	print row
file.close()
print 'Done!'
