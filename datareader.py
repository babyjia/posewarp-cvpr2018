import numpy as np
import cv2
import scipy.io as sio
import os
import json

def getPersonScale(joints):
	torso_size = (-joints[0][1] + (joints[8][1] + joints[11][1])/2.0)
	peak_to_peak = np.ptp(joints,axis=0)[1]
	#rarm_length = np.sqrt((joints[2][0] - joints[4][0])**2 + (joints[2][1]-joints[4][1])**2)			
	#larm_length = np.sqrt((joints[5][0] - joints[7][0])**2 + (joints[5][1]-joints[7][1])**2)
	rcalf_size = np.sqrt((joints[9][1] - joints[10][1])**2 + (joints[9][0] - joints[10][0])**2)
	lcalf_size = np.sqrt((joints[12][1] - joints[13][1])**2 + (joints[12][0] - joints[13][0])**2)
	calf_size = (lcalf_size + rcalf_size)/2.0

	size = np.max([2.5 * torso_size,calf_size*5,peak_to_peak*1.1]) 
	return (size/200.0)

def makeWarpExampleList(param,n_train_examples,n_test_examples,entire_vid=False,class_id=0):

	vid_pth = param['vid_pth']
	info_pth = param['info_pth']
	n_test_vids = param['n_test_vids']
	img_sfx = param['img_sfx']
	test_vids = param['test_vids']

	vid_names = [each for each in os.listdir(vid_pth)
                if os.path.isdir(os.path.join(vid_pth,each))]

	n_vids = len(vid_names)

	np.random.seed(17)

	if(test_vids):
		test_vids = test_vids
		train_vids = list(set(range(n_vids)) - set(test_vids))	
	else:
		random_order = np.random.permutation(n_vids).tolist()
		test_vids = random_order[0:n_test_vids]
		train_vids = random_order[n_test_vids:]

	ex_train = []
	ex_test = []

	for i in xrange(n_train_examples+n_test_examples):

		if(i < n_test_examples):
			vid = test_vids[np.random.randint(0,n_test_vids)]	
		else:
			vid = train_vids[np.random.randint(0,n_vids-n_test_vids)]

		vid_name = vid_names[vid]

		info = sio.loadmat(os.path.join(info_pth, vid_name + '.mat'))		
		box = info['data']['bbox'][0][0]
		X = info['data']['X'][0][0]

		n_frames = X.shape[2]

		frames = np.arange(n_frames)
		if(entire_vid is False):
			frames = np.random.choice(n_frames,2,replace=False)
			while(n_frames > 100 and abs(frames[0] - frames[1]) <= 2):
				frames = np.random.choice(n_frames,2,replace=False)

		l = []
		for j in xrange(len(frames)):
			I_name_j = os.path.join(vid_pth,vid_name,str(frames[j]+1)+img_sfx)
			joints = X[:,:,frames[j]]-1.0
			box_j = box[frames[j],:]
			scale = getPersonScale(joints)
			pos = [(box_j[0] + box_j[2]/2.0), (box_j[1] + box_j[3]/2.0)] 
			lj = [I_name_j] + np.ndarray.tolist(joints.flatten()) + pos + [scale]
			if(entire_vid):
				l.append(lj)
			else:
				l += lj	

		if(i < n_test_examples):
			ex_test.append(l)
		else:	
			ex_train.append(l)

	return ex_train,ex_test


'''
def makePoseExampleList(json_path,n_test,n_joints,permute=True):

	data = []
	with open(json_path) as data_file:
		data = json.load(data_file)
		data = data['root']
		num_examples = len(data)

	if permute:
		np.random.seed(17)
		random_order = np.random.permutation(num_examples).tolist()
	else:
		random_order = np.arange(0,num_examples)

	ex_train = []
	ex_test = []

	mpii2cpm = [9,8,12,11,10,13,14,15,2,1,0,3,4,5]
	
	for i in xrange(num_examples):
		ri = random_order[i]

		img_name = str(data[ri]['img_name'])
		scale = data[ri]['scale_provided']

		if 'idx' in data[ri].keys():
			idx = data[ri]['idx']
		else:
			idx = 0
		obj_pos = np.asarray(data[ri]['objpos'])-1
		obj_pos = obj_pos.flatten().tolist()
		joints_cpm = np.zeros((n_joints,2))

		if 'joint_self' in data[ri].keys():
			joints = np.asarray(data[ri]['joint_self'])	
			for j in xrange(n_joints):
				joints_cpm[j,:] = joints[mpii2cpm[j],0:2]-1	
		
		joints_cpm = joints_cpm.flatten().tolist()
		example = [img_name] + joints_cpm + obj_pos + [scale]
		if(i < n_test):
			ex_test.append(example)	
		else:
			ex_train.append(example)


	return ex_train,ex_test
'''
