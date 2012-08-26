#!/usr/bin/env python

import sys,optparse
import random, copy

MIN_SCORE = 1
count = 0

def main(argv):
	print argv
	args = sys.argv[1:]

	box_quants = [8,8,6,3,6,6,6,0]
	
	allsubs = readfile(args[0])
	print('\n')
	#print(allsubs)
	print str(len(allsubs)) + ' subs'
	
	avail_boxes = 0
	
	for box in box_quants:
		avail_boxes += box

	print  str(avail_boxes) + ' available boxes'
	raw_input()
	if len(allsubs) <= avail_boxes:
		if allocate(allsubs, box_quants):
			print 'yay'
	
		else: print 'didn\'t work'

	else: print'not enough boxes to go around'
	
	for sub in allsubs:
		print str(sub[0]) + ',' + str(sub[2]) + ',' + str(sub[4])
	#print allsubs
	#sortedsubs = sorted(allsubs, key=sortbyrand)
	#print sortedsubs
	return 1
	

def allocate(subs, box_amts):
	
	#if count >= 5000: return False
	
	#else: count += 1

	if len(subs) == 0: return True	

	cur_pers = subs.pop(0)
	temp_boxamts = copy.deepcopy(box_amts)
	
#	for i in box_amts:
#		temp_boxamts.append(box_amts[i])


	for personboxscore in cur_pers[3]:
		if personboxscore[1] < MIN_SCORE : 
			break

		box_num = personboxscore[0]
		print 'trying to assign box ' + str(box_num) + ' to person ' + str(cur_pers[0])
		#print box_amts
		if box_amts[box_num] > 0:
			#print 'box assigned'
			
			box_amts[box_num] = box_amts[box_num]-1
			#print box_amts
			if allocate(subs, box_amts):
			#	print str(cur_pers[0]) + ', box ' + str(box_num) +', score ' + str(personboxscore[1])
				#print box_num	
	
				cur_pers[2]=box_num
				cur_pers[4] = personboxscore[1]
				subs.insert(0,cur_pers)
				#print('this person\'s box will be %d\n' % box_num)
				return True
			else: 
				#print 'box ' + str(box_num) + ', taken away from person ' + str(cur_pers[0])
				box_amts[box_num] = box_amts[box_num] +1
				#box_num = box_num + 1
				#print box_amts

		#else: print ('not enough')
	subs.insert(0,cur_pers)
	box_amts = temp_boxamts
	del temp_boxamts
	#print 'looped through all boxes for person ' + str(cur_pers[0]) + ' none avail'
	return False

def sortbyrand(i):
	return i[1]


def sortbyboxscore(i):
	return i[1]*-1

def readfile(filename):
	
	people = []	

	f = open(filename, 'rU')


	for line in f:
		linelist = line.split()
		curpers = []		
		curpers.append(int(linelist.pop(0)))
		curpers.append(random.randint(0,10000000))
		curpers.append(-1)
		count = 0
		scores = []
		for num in linelist:
			scores.append((count,int(num)))
			count = count + 1
		curpers.append(sorted(scores, key=sortbyboxscore))
		curpers.append(-999)
		#print(curpers)
		people.append(curpers)

	f.close()
	return people




if (__name__ == "__main__"):
	sys.exit(main(sys.argv))
