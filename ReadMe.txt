
Name: Gloria Gilbert Nazareth
Gator Link: gnazareth
Execution commands:
./pdollar.py -t <gestureFile> => for adding gestures
./pdollar.py => for help screen
./pdollar.py -r => to delete all existing gestures
./pdollar.py <eventfile> => to query a gesture


The pdollar algorithm implemented in python, takes various gesture files and event files as input. 
It stores each and every gesture file in a file name cloudPointFile.txt after converting it to cloudpoints. 
Everytime the program is executed, cloudPointFile.txt is read and all the cloudPoints are loaded in to the 
cloudpoint array. At the end, the cloud points are again written back to the file, to use these existing gestures 
for further recognition. 

The run time of the algorithm is O(n^(2.5)). It is much faster and accurate for both single and multistroke gestures.

The program behaves as follows on the below input:
./pdollar.py -t <gestureFile>:After receiving this input, the program will convert all the points in the gesture file
			 to a new set of points by resampling, scaling and translating and store the new set of 
			 points along with the name to the cloudPoint file.
./pdollar.py : On receiving this inout a help screen is displayed, stating all the different input commands available 
	  to the user and its effect.
./pdollar.py -r: This input will cause the program to delete all gesture files stored locally. i.e cloudPointFile.txt 
	    will be deleted.
./pdollar.py <eventFile>: This input will compare the points in the eventFile against the points in all the cloud points.
		     It will check if a particular eventFile matches a gesture and will display an output consisting of
                     the gesture name, match score and time taken to recognize the gesture. If no match is found it displays
                     the respective result.

 



