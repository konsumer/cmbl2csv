#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2

from xml.dom.minidom import parseString
import sys
import os

"""
Simple convert function
"""
def ga3(data):
	contents = data.replace("&","&amp;")
	dom = parseString(contents)
	texts = dom.getElementsByTagName('TextText')
	out = ""
	
	for el in texts:
		out += "\""+fixtext(textContent(el.childNodes))+"\"\n"

	functions = dom.getElementsByTagName('FunctionModel')
	if len(functions)>0:
		out += "---Functions---\n"
		for function in functions:
			for el in function.childNodes:
				if (el.nodeName == "DataObjectName"):
					out+="Name:\n\""+fixtext(textContent(el.childNodes))+"\"\n"
				elif (el.nodeName == "FunctionModelString"):
					out+="Function:\n"+textContent(el.childNodes)+"\n"
				elif (el.nodeName == "FunctionCoefficientArray"):
					coeff = textContent(el.childNodes).split()
					coeff.pop(0) #First number is count of the coefficients.
					out+="Coefficient Numbers:," + ",".join(coeff) + "\n"
				elif (el.nodeName == "FunctionCoefficientUncertaintyArray"):
					coeff = textContent(el.childNodes).split()
					coeff.pop(0) #First number is count of the coefficients.
					out+="Coefficient Uncertainty:," + ",".join(coeff) + "\n"
			out+="\n"
	out+="---Data---\n"

	columns = dom.getElementsByTagName('DataColumn')
	columnArr = [['Data Table: -->']] #first column of data table
	for col in columns:
		coltext = "" #this one column
		for el in col.childNodes:
			if (el.nodeName == "DataObjectName"):
				coltext += fixtext(textContent(el.childNodes)) # Column label
			elif (el.nodeName == "ColumnUnits"):
				if (textContent(el.childNodes) != ''):
					coltext += " ("+fixtext(textContent(el.childNodes))+")" # Units
			elif (el.nodeName == "ColumnCells"):
				txt = textContent(el.childNodes) # Data
				if (txt.find("\nZ")>-1):
					txt=txt[:txt.find("\nZ")] # trim the Z1 Z1 Z2 Z2 etc.
				coltext += txt
		columnArr.append(coltext.split("\n"))

	# add csv columns.
	max=0;
	for col in columnArr:
		if (len(col)>max):
			max=len(col)
	
	#put columns together in csv format:
	for i in range(max):
		out+="\n"
		for col in columnArr:
			if (i<len(col)):
				out += col[i]
			out += ","

	return out


class MainHandler(webapp2.RequestHandler):
    def post(self):
        self.response.headers["Content-Type"] = "text/csv"
        self.response.headers["Content-Disposition"]="attachment;filename=data.csv"
        self.response.out.write(ga3(self.request.get("file")))

app = webapp2.WSGIApplication([('/convert', MainHandler)], debug=True)
