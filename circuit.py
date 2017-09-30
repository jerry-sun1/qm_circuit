import numpy as np
import math
import cmath
from fractions import gcd
import random
import time
import matplotlib.pyplot as plt
np.set_printoptions(linewidth = 300)
np.set_printoptions(threshold = np.nan)
def ReadInput(fileName):
    myInput_lines=open(fileName).readlines()
    myInput=[]
    numberOfWires=int(myInput_lines[0])
    for line in myInput_lines[1:]:
        myInput.append(line.split())
    return (numberOfWires,myInput) #returns tuple

'''
#example usage
myInput=ReadInput("myGateDescription")
firstGate=myInput[0][0]
secondGate=myInput[1][0]
firstWire=myInput[0][1]
'''

def phase(targetWire, phase, totalWires):
    phaseArray = np.array([[1, 0],[0, cmath.exp(1j*phase)]])
    identity = np.identity(2)
    arrlist = []
    for i in range(totalWires):
        if i == targetWire:
            arrlist.append(phaseArray)
        else:
            arrlist.append(identity)
    #print(arrlist)
    return kron_list(arrlist)


def hadamard(targetWire, totalWires):
    sq  = 1/math.sqrt(2)
    hadamardArray = np.array([[sq, sq],[sq, -1*sq]])
    arrlist = []
    for i in range(totalWires):
        if i == targetWire:
            arrlist.append(hadamardArray)
        else:
            arrlist.append(np.identity(2))
    return kron_list(arrlist)

def cnot(controller, totalWires):#will always assume the control is on top

    arrlist = []
    cnotArray = np.array([[1, 0, 0, 0],[0, 0, 0, 1],[0, 0, 1, 0],[0, 1, 0, 0]])
            
    for i in range(totalWires - 1): #minus one because two of the matrices have been condensed into one
        if i == controller:
            arrlist.append(cnotArray)
        else:
            arrlist.append(np.identity(2))
    arrlist.reverse()
    return kron_list(arrlist)

'''
def pauli_x():
    return np.array([[1,0],[0,-1]]) 

def pauli_y():

def pauli_z():
'''

def swapNN(wire1, wire2, totalWires):
    tokron = []
    identityMtx = np.identity(2)
    neighborswap = np.array([[1, 0, 0, 0],[0, 0, 1, 0],[0, 1, 0, 0],[0, 0, 0, 1]])
    for i in range(0,wire1):
        tokron.append(identityMtx)
    tokron.append(neighborswap)
    for i in range(wire2+1, totalWires):
        tokron.append(identityMtx)
    tokron.reverse()
    retgate = kron_list(tokron)
    return retgate


def rangedSwap(wire1, wire2, totalWires):
    list_to_swap = []
    for i in range(0, wire2-wire1):
        list_to_swap.append((wire1+i, wire1+i+1))
        
    for i in range(1, wire2 - wire1):
        list_to_swap.append((wire2 - i - 1 ,wire2-i))
    return doSwap(list_to_swap, totalWires)

def cphase(control, phase, totalWires): #assume that the control wire is always target-1 (above the target wire)
    tokron = []
    identityMtx = np.identity(2)
    neighborphase = np.array([[1, 0, 0, 0],[0, 1, 0, 0],[0, 0, 1, 0],[0, 0, 0, cmath.exp(1j*phase)]])
    for i in range(0,control):
        tokron.append(identityMtx)
    tokron.append(neighborphase)
    for i in range(control+2, totalWires):
        tokron.append(identityMtx)
    tokron.reverse()
    retgate = kron_list(tokron)
    return retgate

def doSwap(swaplist, totalWires):
    #print(swaplist)
    identityMtx = np.identity(2**totalWires)
    retMtx = identityMtx
    for i in range(len(swaplist)):
        wire1 = swaplist[i][0]
        wire2 = swaplist[i][1]
        #print("wire 1: " + str(wire1))
        #print("wire 2: " + str(wire2))
        #print(swapNN(wire1, wire2, totalWires))
        #print(retMtx)
        retMtx = np.dot(swapNN(wire1,wire2, totalWires),retMtx)
        
    return retMtx


def rangedcnot(control, target, totalWires):
    if(abs(control-target) == 1): #easy case, can just run the other cnot
        return cnot(control, target, totalWires)
    prelimSwap = np.identity(2**totalWires) #used if need to flip the control and targets size
    if control > target: #need to swap the two so that control is above
        prelimSwap = rangedSwap(control, target, totalWires)
        
    #control wire is now guaranteed to be the uppermost wire
    highest = min(control, target) #index of controlWire
    lowest = max(control, target) #index of targetWire
    #want to swap control above target
    swapgate = rangedSwap(highest, lowest-1, totalWires)
    print(swapgate.shape)

    cnotgate = cnot(lowest-1, totalWires)
    print(cnotgate.shape)
    #now build the unitary matrix that is composed from swap-cnot-swap
    innerSwap =  np.dot(swapgate,np.dot(cnotgate,swapgate))
    return np.dot(prelimSwap, np.dot(innerSwap, prelimSwap)) 


def rangedcphase(control, target, phase, totalWires): #takes in a 2x2 unitary and gives the matrix that describes this circuit element
    #need to swap so that control is above
    prelimSwap = np.identity(2**totalWires) #used if need to flip the control and targets size
    if control > target: #need to swap the two so that control is above
        prelimSwap = rangedSwap(control, target, totalWires)
    highest = min(control, target)
    lowest = max(control, target)
    
    swapgate = rangedSwap(highest, lowest-1, totalWires)
    cphasegate = cphase(highest, phase, totalWires)
    print(cphasegate.shape)
    print(swapgate.shape)
    innerSwap = np.dot(swapgate, np.dot(cphasegate, swapgate))
    return np.dot(prelimSwap, np.dot(innerSwap, prelimSwap))
    
    
        


def kron_list(arrlist):
    outarr = arrlist[0]
    for i in range(1,len(arrlist)):
        outarr = np.kron(outarr, arrlist[i])
    return outarr

def process_circuit(filename):
    myInput = ReadInput(filename)
    totalWires = myInput[0]
    numGates = len(myInput[1])
    #print(numGates)
    size = 2**totalWires
    gatesMatrix = np.identity(size)
    willMeasure = False
    for i in xrange(numGates-1, -1, -1): #process gates in reverse order
        if myInput[1][i][0] == 'H':
            #print(totalWires)
            #print(myInput[1][i][1])
            #print(hadamard(float(totalWires), float(myInput[1][i][1])))
            gatesMatrix = gatesMatrix.dot(hadamard(int(myInput[1][i][1]),int(totalWires)))
        elif myInput[1][i][0] == 'CNOT':
            gatesMatrix = gatesMatrix.dot(cnot(int(totalWires), int(myInput[1][i][1]), int(myInput[1][i][2])))
        
        elif myInput[1][i][0] == 'P':
            #print('read phase')
            gatesMatrix = gatesMatrix.dot(phase(int(totalWires), int(myInput[1][i][1]), float(myInput[1][i][2])))     
        
        elif myInput[1][i][0] == 'Measure':
            
            willMeasure= True
    if willMeasure:
        inputstate = np.array([[1.0],[0],[0],[0],[0],[0],[0],[0]])
        print("Measured the state corresponding to the decimal number: " + str(measure(inputstate, gatesMatrix)))
    return gatesMatrix

def measure(input, gatesMatrix): #given some input state and unitary matrix representing the circuit, this function 
    output =  np.dot(gatesMatrix, input)
    coefflist = []
    currSum = 0
    for i in range(len(output)):
        currSum += round(100000*(np.abs(output[i][0]))**2)/1000 #fix some floating point stuff, mostly trailing 9s
        coefflist.append(currSum)
    #roll a random float between 0 (inc) and 100 (exc) and return the first index s.t. coeff(index) > randomfloat
    randfloat = np.random.uniform(0, 100)
    idx = 0
    while randfloat > coefflist[idx]:
        idx+=1
    print coefflist
    return idx
    

def build_random(filename, length, numWires):
	#first create random circuit as a string, each element terminated with newline
	#can do phase, hadamard, nearest-neighbor CNOT
	description = str(numWires) + "\n"
	inverse = []
	for i in range(length):
		rnd = random.randint(1, 3)
		if rnd == 1: #hadamard
			addition = "H " + str(random.randint(0, numWires - 1))
                        description += addition + "\n"
                        inverse.append(addition) #hadamard is its own inverse
		elif rnd == 2: #phase
                        wire = random.randint(0, numWires-1)
                        phase = random.uniform(0, math.pi)
			addition = "P " + str(wire) + " " + str(phase)
                        invaddition = "P " + str(wire) + " " + str(-1*phase)
                        description += addition + "\n"
                        inverse.append(invaddition)
		elif rnd == 3: #CNot
			altWire = 0
			controlWire = random.randint(0, numWires - 1)
			if random.uniform(0, 1) > 0.5:
				altWire = 1
			else:
				altWire = -1
			addition = "CNOT " + str(controlWire) + " " + str(controlWire + altWire) 
                        description += addition + "\n"
                        inverse.append(addition) #cnot is its own inverse
                        
        #now inverse contains all of the information about the inverses of each matrix
        for i in range(len(inverse)):
            description += inverse[len(inverse) - i - 1] + '\n'
		
	with open(filename, 'w') as f:
		f.write(description)
        print description



#take in file name and give the inverse
def build_inverse(filename):
    #types of elements to invert:
    #CNot
    #CPhase
    #Phase
    #Hadamard
    newFileName = filename + "_inverse"
    input = ReadInput(filename)
    numWires = input[0]
    inputGates = input[1]
    numGates = len(inputGates)
    inverseDescription = []
    willMeasure = False
   
    #print(inputGates)
    for i in range(numGates):
        if inputGates[i][0] == 'H':
            inverseDescription.append(['H', str(inputGates[i][1])]) #just put it back in
        elif inputGates[i][0] == 'CNOT':
            inverseDescription.append(['CNOT', str(inputGates[i][1]), str(inputGates[i][2])])
        elif inputGates[i][0] == 'P':
            #print('read phase')
            inverseDescription.append(['P', str(inputGates[i][1]), str(-1*float(inputGates[i][2]))])
         
        elif inputGates[i][0] == 'Measure':
            willMeasure = True
    inverseDescription.append(numWires)
    inverseDescription.reverse()
    if willMeasure:
        inverseDescription.append(['Measure'])
    writeArrayToFile(newFileName, inverseDescription)


def buildsimpleQFT():
    description = "3\n" 
    description += "H 0\n"
    description += "CPHASE 1 0 " + str(math.pi/2) + "\n"
    description += "H 1\n"
    description += "CPHASE 2 0 " + str(math.pi/4) + "\n"
    description += "CPHASE 2 1 " + str(math.pi/2) + "\n"
    description += "H 2\n"
    description += "Measure"

    #description now has the full description of the QFT on 3 wires.
    with open("circuit/three_wire_QFT", 'w') as f:
	f.write(description)
    print description
    

     
##SHOR'S ALGORITHM AND UTILITY FUNCTIONS
    
def classical_shors(n, failures):
    a = random.randint(1, int(math.sqrt(n)))
    #print(x)
    r = 0
    retval = (-1, -1)
    if gcd(a, n) != 1: # we found a nontrivial factor
        #print("successful guess: a is " + str(a) + " and the gcd of a and n is " + str(gcd(a,n)))
        retval = [(gcd(a, n), n/gcd(a , n)), 0, failures]
    else: #need to complete rest of shor's
        r = 1
        while mod_mult(a,r,n) != 1:
            r += 1
        if r%2 == 1: #if r is odd try again
            #print("failed due to odd exponent")
            retval =  classical_shors(n, failures + 1)
            
        else: 
            prod = mod_mult(a, (r/2), n)
            first = gcd(prod - 1, n)
            second = gcd(prod + 1, n)
            #print("got into the prod block")
            if(first == 1 or second == 1):
                #print("failed due to trivial factor")
                retval =  classical_shors(n, failures + 1)
                
            else:
                retval = [(first, second), r, failures]
                #print("total failures: " + str(failures))
                
    #print("factored " + str(n) + " into " + str(retval))
    return retval

    

   


def mod_mult(base, exp, modulo):
    prod = 1
    for i in range(exp):
        prod = (prod * base)%modulo
    return prod

def time_function(myfnc, iterations,  param = None):
    timespent = 0
    for i in range(iterations):
        start = time.time()
        myfnc(param)
        end = time.time()
        timespent += end-start
    return float(timespent)/iterations

def is_exponent(n):
    ret = False
    for k in range(2, int(math.ceil(np.log(n)/np.log(2) + 1))):
        #print(k)
        if abs(round(n**(1.0/k)) - n**(1.0/k)) < 1*10**(-10):
            ret = True
            #print("one factor of the number " + str(n) + " is " + round(n**(1.0/k)))

    return ret
        
def plot_shors_guesses(domain, trialsperint, iterations):
    guesses = []
    for k in domain:
        total = 0
        for j in range(trialsperint):
            randomnumber = random.randint(2**k, 2**(k+1) - 1)
            #print("trying with number " + str(randomnumber))
            while(randomnumber%2 == 0 or is_prime(randomnumber) or is_exponent(randomnumber)):
                randomnumber = random.randint(2**k, 2**(k+1) - 1)
            print("testing with random number " + str(randomnumber))
            #print(time_function(myfnc, i))
            for it in range(iterations):
                ret = classical_shors(randomnumber, 0)
                total += ret[1]
                print("factored " + str(randomnumber) + " into " + str(ret))
        guesses.append(float(total)/iterations/trialsperint)
    writeArrayToFile('exponentspace.txt', domain)
    writeArrayToFile('guesses.txt', guesses)
    plt.plot(domain, guesses, 'ro')
    plt.show()

def plot_shors_failures(domain, trialsperint, iterations):
    numbers = []
    times = []
    failures = []
    for k in domain:
        for j in range(trialsperint):
            total = 0
            randomnumber = random.randint(2**k, 2**(k+1) - 1)
            #print("trying with number " + str(randomnumber))
            while(randomnumber%2 == 0 or is_prime(randomnumber) or is_exponent(randomnumber)):
                randomnumber = random.randint(2**k, 2**(k+1) - 1)
            print("testing with random number " + str(randomnumber))
            #print(time_function(myfnc, i))
            for it in range(iterations):
                start = time.time()
                ret = classical_shors(randomnumber, 0)
                end = time.time()
                total += ret[2]
                print("factored " + str(randomnumber) + " into " + str(ret))
                failures.append(float(total)/iterations)
                numbers.append(randomnumber)
                times.append(end-start)
    writeArrayToFile('failures.txt', failures)
    writeArrayToFile('times.txt', times)
    writeArrayToFile('numbers.txt', numbers)
    plt.plot(numbers, failures, 'ro')
    plt.figure()
    plt.plot(numbers, times, 'bo')
    plt.show()



def is_prime(n):
    isprime = True
    for i in range(2,int(math.sqrt(n))+1):
        if n%i == 0:
            isprime = False

    return isprime

def gen_primes(numPrimes):
    primelist = []
    counter = 0
    n = 2
    while(counter < numPrimes):
        if is_prime(n):
            primelist.append(n)
            counter+=1
        n += 1
    return primelist

def gen_product_primes(numPrimes):
    primeproductlist = []
    primelist = gen_primes(numPrimes)
    for i in range(len(primelist)):
        for j in range(i, len(primelist)):
            primeproductlist.append(primelist[i]*primelist[j])
    primeproductlist.sort()
    return primeproductlist


def readArrayFromFile(filename):
    retArray = []
    with open(filename, 'r') as f:
        lines = f.readlines()
        for i in range(len(lines)):
            retArray.append(float(lines[i]))
    return retArray

def writeArrayToFile(filename, array):
    with open(filename, 'wb') as f:
        for i in range(len(array)):
            f.write(str(array[i]) + "\n")

##TEST SWAP
#print(swapNN(1,2,4))
#print(rangedSwap(0,3, 4))
#print(rangedcnot(0, 2,3))
#print(cnot(1,3))
#print(rangedcphase(0, 1, 1, 2))

##Testing circuit building
#print(build_inverse("circuit/ex1"))
#print(readArrayFromFile("circuit/ex1"))
buildsimpleQFT()
process_circuit("circuit/three_wire_QFT")
#print(gen_product_primes(30))
#print(classical_shors(71*53*11, 0))
#print(mod_mult(71, 10, 15))

##PLOTTING SHORS FAILURES vs log(n) (AND TIME COMPLEXITY)
#plot_shors_failures(range(3,14), 100, 5)

##PLOT OF GUESSES REQUIRED (r) VS log(n)
#plot_shors_guesses(range(3, 14), 100, 5)



##PLOTTING STUFF AFTER BINNING BY BINARY EXPONENT
'''
numbers = readArrayFromFile("numbers.txt")
guesses = readArrayFromFile("guesses.txt")
failures = readArrayFromFile("failures.txt")
karr = []
failuresperexp = []
sum = 0
counter = 0
for k in range(3, 14):
    karr.append(k)
    for i in range(len(numbers)):
        if numbers[i] < 2**(k+1) and numbers[i] > 2**k:
            sum += failures[i]
            counter += 1
    failuresperexp.append(float(sum)/counter)
    sum = 0

plt.plot(karr, failuresperexp, 'ro')
plt.plot(karr, guesses, 'bo')
plt.show()

#print(is_prime(6))
#print(is_prime(71))
#print(ReadInput('circuit/ex1'))   
#print(hadamard(3,0))
#print(np.identity(8).dot(hadamard(3, 1)))

#writeArrayToFile('saveExample.txt', [1,2,3,4,5])
#print(readArrayFromFile('saveExample.txt'))
#build_random("circuit/random", 4, 3)
'''

##PROCESS EX1 WITH MEASURE
#process_circuit('circuit/ex1')


##HISTOGRAMMING MEASUREMENT OF AN OUTPUT STATE GIVEN SOME INPUT STATE
'''
inputState = np.array([[1.0],[0],[0],[0],[0],[0],[0],[0]])
mydict = {}
for i in range(len(inputState)):
    mydict[i] = 0
for i in range(1000):
    mydict[measure(inputState, process_circuit('circuit/ex1'))] += 1
print mydict
'''
