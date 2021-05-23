import json, pprint
import os, subprocess, re


DB_PATH = './data.json'
re_date = re.compile('Date.*(\d{2}-\w{3}-\d{4})')
digit_match = '\d{0,3}\,?\d{0,3}\.\d{2}'
date_match = '\d{2}-\w{3}-\d{4}'


###   Main Functions  ###

def getPdfFiles():
	return list(filter(lambda x: x.startswith('20'), os.listdir()))

def getShellOuput():
	pdf_files = getPdfFiles()
	return list(map(lambda x: runShell(x), pdf_files))

def runShell(file_path):
	output = subprocess.check_output(['pdf2txt.py', '-n', file_path ]).decode('utf-8')
	return output

def digitizeTuple(tupl):
	temp = list(tupl)
	for i in range(3, 6):
		temp[i] = str2NUm(temp[i])
	return tuple(temp)


# gets info transaction info
def textAndDigit(text, info):
	output = re.search(f'{info}.*?({digit_match})', text).groups()[0]
	return str2NUm(output)
	# return (output)	 # string

# sorts each transaction info into an array of strings
def testTextAndDigit(info, arr, length, show = True):
	test = list(map(lambda x: textAndDigit(x, info), arr))
	return testHelper(info, show, test, length) # array of strings

def testHelper(info, show, test, length):
	if show:
		print(info)
		pprint.pprint(test)
		print()
	assert len(test) == length
	return test 

# gets time period 
def period(text):
	output = re.search('Period:(.*)Currency', text)
	return output.groups()[0]

# gets date
def date(text):
	output = re.search('Date: *(.*)Address', text)
	return output.groups()[0].replace(' ', '')

# separates the text containing the transaction notifcations
def transactionText(text):
	output = re.search(f'DebitCreditBalance.*?{date_match}BF.*?{digit_match}(.*?)Closing Balance', text)
	return output.groups()[0]    # String

# get all transaction notification for each file
def eachTrans(text):
	t  = transactionText(text)
	output = re.findall(f'({date_match})(.*?)({date_match}).*?({digit_match}).*?({digit_match}).*?({digit_match})', t)
	
	temp = [len(each) == 6  for each in output]
	temp = list(filter(lambda x: x == False, temp))
	assert temp == []
	
	return output # Array of tuples containing transaction data

def str2NUm(text):
	return float(text.replace(',', ''))

def printAll(arr):
	for i in arr:
		print(i)
		print()

### Testing ###


def Test(show = True):
	shell_list = getShellOuput()
	Len = len(shell_list)


	def specialTransText(find):
		t = testEachTrans(False)
		temp = [each for each in t if each[0][0].find(find) != -1 ]
		printAll(temp)

	def testPeriod(show):
		info = 'Periods'
		test = list(map(lambda x: period(x), shell_list))
		return {
			info: testHelper(info , show, test, Len)
		}

	def testDate(show):
		info = 'Dates'
		test = list(map(lambda x: date(x), shell_list))
		return {
			info: testHelper(info , show, test, Len)
		}


	def testTransText(show):
		info  = 'Transactions'
		test = list(map(lambda x: transactionText(x), shell_list))
		printAll(test)
		return testHelper(info , False, test, Len)

	def testEachTrans(show):
		info = 'Each Transactions'
		test = list(map(lambda x: eachTrans(x), shell_list))
		return {
			info: testHelper(info , show, test, Len)
		}
	
	def testOpenBalance(show):
		info = 'Opening Balance'
		return {
			info: testTextAndDigit(info, shell_list, Len, show)
		}

	def testCloseBalance(show):
		info = 'Closing Balance'
		return {
			info: testTextAndDigit(info, shell_list, Len, show)
		}

	def testTotalDebit(show):
		info = 'Total Debit'
		return {
			info: testTextAndDigit(info, shell_list, Len, show)
		}

	def testTotalCredit(show):
		info = 'Total Credit'
		return {
			info: testTextAndDigit(info, shell_list, Len, show)
		}

	def testUnclearedEffects(show):
		info = 'Uncleared Effects'
		return {
			info: testTextAndDigit(info, shell_list, Len, show)
		}


	def testAll(show):
		return {
			**testPeriod(show),						  #array of strings
			**testDate(show),    						#array of strings
			**testOpenBalance(show),   		  #array of strings
			**testCloseBalance(show),  		  #array of strings
			**testTotalDebit(show),    			#array of strings
			**testTotalCredit(show),    		#array of strings
			**testUnclearedEffects(show),   #array of strings
			**testEachTrans(show)   				#array of arrays containing tuples
		}, Len


		return {
			'open': 3
		}

	# specialTransText('Feb')
	# testTransText(True)

	return testAll(show)
	# testTotalCredit(show)

def dictionaryParser(dictionary):
	dic, length = dictionary
	full_array = []

	for i in range(length):
		each_dictionary = {}
		for key, array in dic.items():
			each_dictionary[key] = array[i]

		full_array.append(each_dictionary)
	return full_array



def saveToDB(dictionary, output):
	json_object = json.dumps(dictionary, indent = 2)

	with open(output, "w") as outfile:
	  outfile.write(json_object)

def convertToText():
	dic = Test(False)
	db = dictionaryParser(dic)
	saveToDB(db, DB_PATH)
	# print(len(g))

def Main():
	convertToText()



if __name__ == '__main__':
	# Main()
	print(digitizeTuple(('asf', 'aa', 'ggggg', '124', '346', '346')))
	# Test()