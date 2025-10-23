""" CSeq Program Analysis Framework
    variable renaming module
    
This module performs variable renaming based on variable scope,
so that no two functions share a variable id after it.

to make function inlining easier:
(doing so avoids future problems with the inliner module, see regression/102,103 )

At the end of the renaming, the map of variable name changes
is available in newIDs (useful for counterexamples,
to translate back variable names to the corrisponding original name). 

Transformation:
	int f(int P) {
		int L;
	}

into:
	int f(int __cs_f_P) {
		int __cs_f_L;
	}

Author:
    Omar Inverso

Changes:
    2020.03.25 (CSeq 2.0)
    2019.11.13  module almost entirely rewritten from scratch (and got rid of _generate_type())
    2015.07.08  map with variable renames returned as an output parameter
    2014.12.24 (CSeq 1.0beta)
    2014.12.09  further code refactory to match the new organisation of the CSeq framework
    2014.10.27  different prefixes for local variables and function parameters
    2014.10.26 (CSeq Lazy-0.6, newseq-0.6a, newseq-0.6c) [SV-COMP 2015]
    2014.10.26  changed  __stack  to  stack  (to inherit stack handling from module.py)
    2014.10.15  removed visit() and moved visit call-stack handling to module class (module.py)
    2014.03.14  further code refactory to match  module.Module  class interface
    2014.03.08  first version (CSeq Lazy-0.2)

To do:
  - urgent: still need this?
  - block-based renaming (much more robust, and possible with new symbol table)
  - make sure the new variables do not shadow existing symbols

"""

import inspect, os, sys, getopt, time
import pycparserext.ext_c_parser, pycparser.c_ast, pycparserext.ext_c_generator
import core.module, core.parser, core.utils


class varnames(core.module.Translator):
	localprefix = '__cs_local_'   # prefix for local variables
	paramprefix = '__cs_param_'   # prefix for function params

	varmap = {}          # map from new to old variable names
	                     # (the scope is not an index, as the prefix guarantees the new id to be unique)

	varscope = {}        # scopes of new variable ids

	varmapreverse = {}   # map of old variable names and scopes to new variable names
	                     # (here the scope is an index as the id may not be unique)

	__debug = False
	__visitingStructRef = False   # to avoid considering struct fields as local variables
	__visitingParam = 0    # depth of params in a function prototype
	__visitFuncDef = 0


	def init(self):
		self.outputparam('varnamesmap')


	def loadfromstring(self, string, env):
		super(self.__class__, self).loadfromstring(string, env)
		self.setoutputparam('varnamesmap', self.varmap)
		self.setoutputparam('varscopesmap', self.varscope)


	''' Change the identifier in the sub-AST rooted at n to be newid.
	'''
	def changeid(self,n,newid):
		# In the base (i.e., int x) the loop below will
		# terminate immediately after one iteration.
		#
		# For more complex expressions,
		# go through any pointer declaration (e.g., int *x), or
		# array declaration (e.g., int a[][]), until
		# a c_ast.TypeDecl node is found.
		#
		scan = n

		while type(scan.type) != pycparser.c_ast.TypeDecl:
			#print (scanning... %s " % (type(boh.type)))
			scan = scan.type

		oldid = scan.type.declname
		scan.type.declname = newid

		return oldid


	def visit_Decl(self, n, no_type=False):
		# no_type is used when a Decl is part of a DeclList, where the type is
		# explicitly only for the first delaration in a list.
		#

		#if self.__debug: print("--> visiting decl:[%s]  scope:[%s]" % (n.name,self.currentFunct))
		#if self.__debug: print("     stack: "+  str(self.stack) + '   prev:' + str(self.stack[len(self.stack)-2]))

		# Detect declaration of function parameters
		if self.__visitFuncDef == True and self.__visitingParam > 0:
			newname = self.paramprefix + self.currentFunct + '_' + n.name
			self.varmap[newname] = n.name
			self.varscope[newname] = self.currentFunct
			self.varmapreverse[self.currentFunct,n.name] = newname

			oldid = self.changeid(n,newname)
			#print ("[%s] -> [%s]" %(oldid,newname))


		# Detect declaration of local variables
		if n.name and self.__visitFuncDef == True and self.__visitingParam == 0 and not self.currentFunct==n.name:
			#if self.__debug: print("    local variable")
			newname = self.localprefix + self.currentFunct + '_' + n.name
			self.varmap[newname] = n.name
			self.varscope[newname] = self.currentFunct
			self.varmapreverse[self.currentFunct,n.name] = newname

			oldid = self.changeid(n,newname)
			#if self.__debug: print ("[%s] -> [%s]" %(oldid,newname))

		#if self.__debug: print("")

		s = n.name if no_type else self._generate_decl(n)

		if n.bitsize: s += ' : ' + self.visit(n.bitsize)
		if n.init:
			if isinstance(n.init, pycparser.c_ast.InitList):
				s += ' = {' + self.visit(n.init) + '}'
			elif isinstance(n.init, pycparser.c_ast.ExprList):
				s += ' = (' + self.visit(n.init) + ')'
			else:
				s += ' = ' + self.visit(n.init)

		return s


	def visit_FuncDef(self, n):
		self.currentFunct = n.decl.name
		self.__visitFuncDef = True
		s = super(self.__class__, self).visit_FuncDef(n)
		self.__visitFuncDef = False
		self.currentFunct = ''
		return s


	def visit_ParamList(self, n):
		out = ''
		for i, p in enumerate(n.params):
			spacer = '' if i==0 else ', '
			self.__visitingParam += 1
			out += spacer + self.visit(p)
			self.__visitingParam -= 1

		#return ', '.join(self.visit(param) for param in n.params)
		return out


	def visit_StructRef(self, n):
		sref = self._parenthesize_unless_simple(n.name)
		oldvisitingStructRef = False
		self.__visitingStructRef = True
		#if self.__debug: print("------- ------- ------- ------- ------- ------- VISITING STRUCT REF START (%s)" % sref)
		retval = sref + n.type + self.visit(n.field)
		#if self.__debug: print("------- ------- ------- ------- ------- ------- VIITING STRUCT REF END")
		self.__visitingStructRef = 	oldvisitingStructRef	
		return retval


	def visit_ID(self, n):
		prefix = ''

		#if self.__debug: print("--> visiting id:[%s]  scope:[%s]" % (n.name,self.currentFunct))

		if (n.name in self.Parser.varNames[self.currentFunct] and
		    self.currentFunct != '' and 
		    not self.__visitingStructRef ):

			#if self.__debug: print("     local PARAMETER")
			#if self.__debug: print("     stack: "+  str(self.stack) + '   prev:' + str(self.stack[len(self.stack)-2]))
			#if self.__debug: print("")

			#print("--> visiting id:[%s]  scope:[%s]" % (n.name,self.currentFunct))
			varid = super(self.__class__, self).visit_ID(n)
			n.name = self.varmapreverse[self.currentFunct,n.name]

			
		return prefix + super(self.__class__, self).visit_ID(n)


