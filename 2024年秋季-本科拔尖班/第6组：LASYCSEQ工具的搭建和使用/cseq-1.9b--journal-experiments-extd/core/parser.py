from __future__ import print_function
""" CSeq Program Analysis Framework
	parsing and symbol table module

Generate symbol-table and a few other data structures
(this module is always used at the beginning of a Translator module).

Credits:
    This module is built on top of
    pycparserext by Andreas Klockner, which extends
    pycparser by Eli Bendersky (BSD license), which in turn embeds
    PLY, by David M. Beazley.

Author:
    Omar Inverso

Changes:
    2020.03.28 (CSeq 2.0)
	2020.03.28  block-based lookup macros (isglobal(),ispointer(), etc.), etc.
    2019.11.27 [SV-COMP 2020]
    2019.11.26  initial implementation of the new symbol table (does not replace the old one for now)
    2019.11.24  bugfix: now tracking simple typedefs (e.g., typedef a b;)
    2019.11.15 (CSeq 1.9) pycparserext
    2019.11.15  no longer mapping pthread_xyz function identifiers
    2019.11.13  support for pycparswer 2.19 (backwards compatible)
    2019.11.13  no longer overriding pycparser's generate_type
    2019.03.09  line no. extraction for varReferenced, varOccurrence
    2018.11.23 [SV-COMP 2019] fixed counting of explicit function calls
    2018.11.19  tracking (over-approximated) sources of non-determinism (see varrange and nondetfound)
    2018.11.03  fix: threadcallcnt initialised to zero as soon as a new function is parsed (avoids exceptions)
    2018.11.02  counting the overall number of occurrences of each function identifier (see funcIdCnt)
    2018.11.02  comment to clarify threadIndex+threadCount mechanism
    2018.11.02  storing the stack of AST nodes currently being visited
    2018.05.26 (CSeq 1.5-parallel) first submissions for parallel cba
    2018.05.26  no longer storing the entire body of functions (self.funcBody)
    2018.05.26  added new data structs for extra reasoning, exp. useful for inlining (funcExitPointsCnt,lastStmtNode,lastFuncStmtNode)
    2018.01.24  disabled new symbol table bookkeeping (not needed for now)
    2018.01.24  removed funcBlock[] (inefficient and useless)
    2018.01.24  integrated changes (need to check them) from SVCOMP'16 version (see below):
    2016.11.21  add safe check for node.coord before extracting linenumber (merged change)
    2016.08.16  add self.varInAssignment and self.varNoNeedInit to track local variables (merged change)
    2015.06.23  re-implemented 3rd parameter extraction to  pthread_create()  call (fName)
    2015.01.07  bugfix: calculating when variables are referenced and referenced not working with arrays
    2014.10.29 (newseq-0.6c) (CSeq 1.0beta) [SV-COMP 2015]
    2014.10.29  more information on threads (threadindex map)
    2014.10.27 (newseq-0.6a)
    2014.10.27  improved symbol table about variables' details (exact line(s) where they are referenced, dereferenced, and where they occur)
    2014.03.16  amended the mechanism to calculate the list of functions (varNames)
    2014.03.16  introduced self.reset() for resetting all the data structs
    2014.03.09  anonymous structs no longer supported (they are assigned a name in merger.py)
    2014.03.04  symbol table: removed unused variables names in nested parameter declarations (e.g. parameters of a parameter, for example of a function)
    2014.02.25  bugfix: varNames
    2014.02.19  added  self.nodecoords[] to store the nodes' coords

To do:
  - urgent: simplify as much as possible
  - urgent: use simple and short method names, possibly all lowercase
  - urgent: block-based symbols
  - replace everything by extending the new symbol table,
    in particular varTypeUnexpanded (do we really need varType at all?)
  - get rid of _generate_decl() for populating the parserdata structures
   (see TODO in visit_FuncDef)

  - replace for good varReferenced, varDeReferenced, and varOccurrence, with
    simple counters instead similar to funcIdCnt. Use a uniform naming.
  - use more direct AST-based information fetching, such as
    len(self.Parser.funcASTNode[fref].decl.type.args.params)
    for checking the number of parameters of a function
   (see pycparser/c_ast.py for the fields)

 Things to handle here:
  - replace everything like this: if 'FuncDecl' in str(n.type)
    with something like this: if type(n) == pycparser.c_ast.FuncDecl, or
    isinstance(n.type,pycparser.c_ast.FuncDecl)
  - replace data such as self.funcIsVoid[] with macros that visit the AST only at need
   (would have to update all the modules accordingly)
  - new symbol table: the global scope (the global block, really) should be 0 (not ''), then
    the first one within it should be 0.0, the second 0.1, and so on.
  - typedef expansion
  - add extraction of any extra information about the code needed in later modules.

Prerequisites:
  - pycparser >= 2.18 (mostly because coords are in line:col format now)
  - input must be preprocessed (i.e., no # directives)
  - no linemarkers (pycparser does not handle them)
  - no anonymous structs (use merger.py first)
  - no expressions such as A->b,
    should be (*A).b instead (see workaround no. 4)

"""

import pycparserext.ext_c_parser, pycparser.c_ast, pycparserext.ext_c_generator
import core.utils


class Parser(pycparserext.ext_c_generator.GnuCGenerator):
	__sourcecode = ''
	__stack = []
	__stacknodes = []


	""" Uses the same visitor pattern as c_ast.NodeVisitor, but modified to
		return a value from each visit method, using string accumulation in
		generic_visit.
	"""
	def __init__(self):
		self.reset()


	def reset(self):
		###### NEW PARSING TABLE START #####
		self.blockid = '0'    # current blockid, as a string '0.y.z'
		self.block = [0]      # current blockid, list of integers
		self.blockd = 0       # current block depth
		self.blockcount = 0   # block no. at the current depth

		self.var = {}         # AST node for variable definitions [blockid,id]
		self.type = {}        # AST node for typedefs [blockid,id]
		self.struct = {}      # AST node for stucture definitions [blockid,id]
		self.union = {}       # AST node for unions [blockid,id]

		self.blocknode = {}   # blockid for a given AST compound block node

		self.blockidf = None  # block of the function body currently being visited
		self.visitingfparams = False

		## _all_ the symbols (function names, variables, struct names, .... ) TODO this needs to be checked & finished properly
		#self.symbols = []
		#self.blocks = {}
		#self.__symbolsstack = []
		#self.__symbolscount = 0
		#self.blocks.append('0')
		##self.symbolsparents[n.name]# the symbol's full parents stack
		##self.__symbolsblock[n.name] = # the symbol's full block/compound stack (e.g. 0:1:20:2 - block 0: is the global scope)
		###### NEW PARSING TABLE END #####

		self.currentFunct = ''         # name of the function being parsed ('' = none)
		self.visitingField = False     # needed to differentiate between variables and fields during the visit

		self.funcName = ['']           # all functions names (consider '' to be a special function to model global scope)
		self.funcParams = {}
		#####self.funcReferenced = []  # all functions whose id are used in anything else than just function calls (e.g. they are used as pointer-to-functions..)
		self.funcCallCnt = {}          # number of calls to a function identifier
		self.funcIdCnt = {}            # number of occurrences of each function identifier (including calls and excluding declarations)
		self.threadName = []           # all threads names (i.e. functions used as argument to pthread_create())
		self.threadCallCnt = {}        # number of times a function is used to generate a thread (by calling pthread_create())

		self.threadCount = 0           # pthread create()s found so far (not counting duplicates, i.e. when the same function is used to create multiple threads)
		self.threadIndex = {}          # index of the thread = value of threadcount when the pthread_create to that thread was discovered

		self.lastStmt = ''             # last statement generated (as a string)
		self.lastStmtNode = ''         # last statement generated (as an AST node)
		self.lastFuncStmt = {}         # last statement for each function
		self.lastFuncStmtNode = {}     # last statement for each function (as an AST node)

		self.funcBlockIn = {}          # input parameters for each function
		self.funcBlockOut = {}         # return value for each function
		self.funcDecl = {}             # function declarations, only for functions declared and defined in different statements, or not defined at all.
		self.funcASTNode = {}          # the AST node for the function definitions, by function
		self.funcIsVoid = {}
		self.funcExitPointsCnt = {}    # Number of return statements in the function
		self.funcLabels = {}           # set of labels defined in a given function, by function

		self.currentVarAssign = ''     # name of the current variable used as lvalue in an assignment statement

		self.currentStruct = ''        # note! this
		self.structName = []

		self.mainParametersDecl = ''     # parameters of the main() function to be transferred to thread 0.


		""" The following are indexed either using
			(struct, variable)  for struct fields, or
			(function, variable) local variables and function parameters, or
			('', variable) for global variables.

			See _generate_decl(self, n) below for details.

			TODO: to make the parsing more robust,
			      the stack of blocks enclosing a variable's scope
			      should rather be used for indexing (each block should have a unique ID)
		"""
		self.varNames = {}           # names of all the variables (global, local, parameters) + variables in structs
		self.varNames[''] = []       # initialisation for global var names ('' is the global scope)

		self.varType = {}            # int, char, ....
		self.varTypeUnExpanded = {}  # same as .varType, but with unexpanded typedefs
		self.varArity = {}           # 0 for scalar, k for k-dimensional arrays
		self.varSize = {}            # [] for scalars, [n1,...,k] for k-dimensional arrays
		#self.varKind = {}            # g, l, p, s
		self.varID = {}              # unique IDs for variables, as they are found while parsing, starting with 0
		self.varCount = 0            #
		self.extraGlovalVarCount = 0 # Count global variables introduced in the above data structures, but not from original input.
		self.varInitExpr = {}        # set when a declared variable has an init expression
		self.varPtrToFunct = {}

		self.varrange = {}           # a constant value if constant, or * if nondet
		self._nondetfound = False    # a nondeterministic expression has been visited since last re-set
		                             #(i.e. a variable previously known to be non-deterministic or call to nondet init)

		# patch for handling pointer-to-function etc. (TODO move with the new symbol table)
		#self.__varIsPointer = {}
		#self.__varIsArray = {}
		#self.__varIsFunction = {}

		# list of line no. where an occurrence, referencing, or dereferencing  happened
		self.varOccurrence = {}      # any occurrence (does not include the very first time a variable occurs, i.e. on the left hand side of its own declaration)
		self.varReferenced = {}      # &var
		self.varDeReferenced = {}    # *var

		# Handling of typedefs.
		# We put in the first variable below the last part of a typedef statement,
		# and in the second variable its correspondent expansion.
		#
		# Anonymous typedefs are no exception, as they are assigned an internal name to be used as described.
		#
		self.typedefs = []          # contains last the part of a typedef stmt, e.g. typedef struct struct_name {.... } last_part;
		self.typedefExpansion = {}  # e.g. typedefs['field'] = struct { int a; int b; ... }  from the original typedef statement

		# Statements start with indentation of self.indent_level spaces, using
		# the _make_indent method
		#
		self.indent_level = 0		# to keep track of the depth of the block {}
		self.INDENT_SPACING = '   '	# ....

		# = True while parsing the subtree for a function declaration
		self.parsingFuncDecl = False

		# = True while parsing the subtree for a struct (or union) declaration
		self.parsingStructOrUnion = False

		# this will set to True after parsing the first function definition (not declaration!)
		self.firstFunctionDefinitionDone = False    # for the old Lal-Reps schema

		# set to True while parsing void functions
		#self.parsingVoidFunction = False

		# set to True while parsing typedef blocks
		self.parsingTypedef = False

		#
		self.currentInputCoord = ''
		self.currentinputlineno = -1
		self.currentOutputLineNumber = -1
		#self.currentAnonStructsCount = 0

		# coords for each node in the AST
		# (when the input is loaded from a string rather than a file,
		#  the coords only contain the line and column number)
		####self.nodecoords = {}

		self.lines = []

		# keep track of variables involved into assignment statements, and
		# of those which ones are always initialised at the next access after their declaration.
		#
		# TODO: need to carefully review these.
		# TODO: this would probably better be module-specific.
		self.varInAssignment = {}
		self.varNoNeedInit = {}


	'''
	def load(self, filename):
		self.__inputfilename = filename
		# Load the input source file to build the AST, then generate the symbol table
		self.ast = pycparser.parse_file(self.__inputfilename, use_cpp=True, cpp_args=r'-Iinclude -E -C ')
		self.__sourcecode = self.visit(self.ast)
		self.ast.show()
	'''


	def loadfromstring(self, string):
		#self.ast = pycparser.parse_file(self.__inputfilename, use_cpp=True, cpp_args=r'-Iinclude -E -C ')
		#self.ast = pycparser.c_parser.CParser().parse(string)
		self.ast = pycparserext.ext_c_parser.GnuCParser().parse(string)   # pycparserext
		self.__sourcecode = self.visit(self.ast)
		###self.ast.show()


	def show(self):
		#print utils.strip(self.__sourcecode)
		print(self.__sourcecode)


	def save(self, filename):
		outfile = open(filename,"w")
		outfile.write(self.__sourcecode)
		outfile.close()


	def string(self):
		return(self.visit(self.ast))


	def printsymbols(self):
		print("list of functions:")

		for f in self.funcName:
			if f == '': continue
			s = "   %s" % f
			####if f in self.funcReferenced: s += '   referenced'
			print(s, end=" ")

			if f != '':
				print("  call count %s" % self.funcCallCnt[f])
			else:
				print('')

		print('')

		print("list of thread functions:")

		for f in self.threadName:
			print("   %s  call count %s" % (f, self.threadCallCnt[f]))

		print('')

		print("parameters for main():\n   "+ '(no params)' if not self.mainParametersDecl else self.mainParametersDecl)
		print('')

		# List of all variables
		print("Variables:")
		for f in self.funcName:
			if not f == '':	print("   " + f)
			else: print("   (global)")

			for v in self.varNames[f]:
				# detailed var description
				s = "      "
				s += "id" + str(self.varID[f,v]) + "  "
				s += "'" + str(v) + "'  "
				s += "\n         "
				s += "type '" + self.varType[f, v] + "'  "
				#s += "kind '" + self.varKind[f, v] + "'  "\
				s += "arity '" + str(self.varArity[f, v]) + "'  "
				s += "\n         "
				s += "size '" + str(self.varSize[f, v]) + "'  "
				s += "\n         "
				s += "ref '" + str(self.varReferenced[f, v]) + "'  "
				s += "\n         "
				s += "deref '" + str(self.varDeReferenced[f, v]) + "'  "
				s += "\n         "
				s += "occurs '" + str(self.varOccurrence[f, v]) + "'  "

				if (f,v) in self.varPtrToFunct: s += "ptr-to-f '" + str(self.varPtrToFunct[f,v]) + "'"

				print(s)

		print('\n')

		# List of all fields
		print("Fields:")
		for f in self.structName:
			if not f == '':	print("   " + str(f))
			else: print("   (global)")

			for v in self.varNames[f]:
				# detailed var description
				s = "      "
				s += "id" + str(self.varID[f,v]) + "  "
				s += "'" + v + "'  "
				s += "type '" + self.varType[f, v] + "'  "
				#s += "kind '" + self.varKind[f, v] + "'  "
				s += "arity '" + str(self.varArity[f, v]) + "'  "
				s += "size '" + str(self.varSize[f, v]) + "'  "

				print(s)

		print('\n')

		print("Typedefs:")
		for x in self.typedefs:
			print(x + " -> " + self.typedefExpansion[x])

		print('\n')

		print("Pointer variables:")
		for f in self.funcName:
			if not f == '':	print("   " + f)
			else: print("   (global)")

			for v in self.varNames[f]:
				if self.varType[f,v].endswith('*'):
					s = "       "
					s += "var '" + v + "'   "
					s += "type '" + self.varType[f, v] + "'   "
					#s += "kind '" + self.varKind[f, v] + "'   "
					s += "arity '" + str(self.varArity[f, v]) + "'   "
					s += "size '" + str(self.varSize[f, v]) + "'   "

					print(s)

		print('\n')

		'''
		print "Function blocks:"
		for f in self.funcName:
			if f != '':
				print "function '%s' ----------------------------------:" % f
				print self.funcBlock[f] + '\n'
				print self.funcBlockIn[f] +'\n'
				print self.funcBlockOut[f] +'\n'

		print "Last statement, by function:"
		for f in self.funcName:
			if f != '':
				print "function: %s   stmt: %s" % (f, self.lastFuncStmt[f])

		print '\n'
		'''

		'''
		print "All symbols (new symbol table - work in progress):"
		for s in self.symbols:
			##print "   %s    [%s]" % (s, self.symbolshierarchy[s, blockstack])
			print "   %s  " % str(s)
		'''

		print("(new symbol table) Variables:")
		for f in self.var:
			print("  %s" % str(f))




	def shownodes(self):
		from optparse import OptionParser
		import inspect
		print([entry for entry in dir(pycparser.c_generator.CGenerator) if not entry[0].startswith('_')])


	def _make_indent(self, delta=0):
		return (self.indent_level+delta) * self.INDENT_SPACING


	def _getmarker(self, item):   # was: _getCurrentCoords
		### return '/*cseq:coords '+ str(item.coord) +' */\n'
		return ''


	def visit(self, node):
		method = 'visit_' + node.__class__.__name__

		# This is to update the current coord (= filename+line number) of the input file being parsed,
		# considering that:
		#
		# - on the same line of input, there may be more AST nodes (shouldn't enter duplicates)
		# - compound statement and empty statements have line number 0 (shouldn't update the current line)
		# - the same line of input may correspond to many lines of output
		#
		lineCoords = ''

		#if not isinstance(node, pycparser.c_ast.FileAST) and str(node) != 'None' and self.indent_level == 0 and node.coord is not None:
		if not isinstance(node, pycparser.c_ast.FileAST) and node is not None and self.indent_level == 0 and node.coord is not None:
			####linenumber = str(node.coord)
			####linenumber = linenumber[linenumber.rfind(':')+1:]
			####self.currentinputlineno = int(linenumber)
			linenumber = node.coord.line
			self.currentinputlineno = linenumber

			# Each line of the output is annotated when
			# either it is coming from a new input line number
			# or the input line has generated many output lines,
			# in which case the annotation needs to be repeated at each line..
			#
			if linenumber not in self.lines and linenumber != '0':
				### print "      adding line number %s" % linenumber
				self.lines.append(linenumber)
				lineCoords = self._getmarker(node)

		self.__stack.append(node.__class__.__name__)
		self.__stacknodes.append(node)

		retval = lineCoords + getattr(self, method, self.generic_visit)(node)

		self.__stack.pop()
		self.__stacknodes.pop()

		return retval


	def generic_visit(self, node):
		#~ print('generic:', type(node))
		if node is None: return ''
		else: return ''.join(self.visit(c) for c in node.children())


	def visit_Label(self, n):
		self.funcLabels[self.currentFunct].append(n.name)
		return n.name + ':\n' + self._generate_stmt(n.stmt)


	def visit_FuncCall(self, n):
		fref = self._parenthesize_unless_simple(n.name)

		# Tracks sources of non-determinism (needs refinement TODO)
		if fref.startswith('__VERIFIER_nondet') or fref.startswith('__CSEQ_nondet'):
			self._nondetfound = True

		# Counts function calls etc.
		if fref not in self.funcCallCnt: self.funcCallCnt[fref] = 1
		else: self.funcCallCnt[fref] += 1

		# Note: only add the key here,
		# as the overall occurrences are already counted in visit_ID....
		if fref not in self.funcIdCnt: self.funcIdCnt[fref] = 0

		if fref not in self.threadCallCnt: self.threadCallCnt[fref] = 0

		args = self.visit(n.args)

		# When a thread is created, extract its function name
		# based on the 3rd parameter in the pthread_create() call:
		#
		# pthread_create(&id, NULL, f, &arg);
		#                          ^^^
		#
		#if fref == 'pthread_create' or fref == core.common.changeID['pthread_create']:
		if fref == 'pthread_create':
			fName = self.visit(n.args.exprs[2])
			fName = fName[1:] if fName.startswith('&') else fName  # TODO detect proper AST pattern
			#print("- -  -- new thread detected! %s at line %s " % (fName, self.currentinputlineno))

			if fName not in self.threadCallCnt: self.threadCallCnt[fName] = 0

			if self.threadCallCnt[fName] == 0:
				self.threadName.append(fName)
				self.threadCallCnt[fName] = 1;
				self.threadCount = self.threadCount + 1
				self.threadIndex[fName] = self.threadCount
			else:
				self.threadCallCnt[fName] += 1

			# Adjust the overall occurrence count for fName
			# as now this node has been visited twice.
			if fName in self.funcIdCnt: self.funcIdCnt[fName] -=1

		return fref + '(' + args + ')'


	def visit_Typedef(self, n):
		s = ''
		if n.storage: s += ' '.join(n.storage) + ' '

		self.parsingTypedef = True
		typestring = self._generate_type(n.type)
		self.parsingTypedef = False

		#print ("-=-=-=->   typedef <%s> <%s>" % (n.name,typestring))
		self.typedefs.append(n.name)
		self.typedefExpansion[n.name] = typestring

		name = '?'
		if n.storage: name = ' '.join(n.storage)
		#print ("= - > new typedef             [%s,%s,%s]  ===============" % (self.blockid,n.name,name))
		self.type[self.blockid,n.name] = n

		if isinstance(n.type.type,pycparser.c_ast.Struct):
			if n.type.type.decls:
				#print ("= - > new structure declared             [%s,%s,%s]  ===============" % (self.blockid,n.type.type.name,n.type.type.decls))
				#print ("= - >                                    [%s]  ===============" % (self.visit(n.type.type)))
				self.struct[self.blockid,n.type.type.name] = n.type.type
		elif isinstance(n.type.type,pycparser.c_ast.Union):
			if n.type.type.decls:
				#print ("= - > new union declared             [%s,%s,%s]  ===============" % (self.blockid,n.type.type.name,n.type.type.decls))
				#print ("= - >                                    [%s]  ===============" % (self.visit(n.type.type)))
				self.union[self.blockid,n.type.type.name] = n.type.type


		s += typestring
		return s


	# Note: function definition = function declaration + body.
	# This method is not called when parsing simple declarations of function (i.e., function prototypes).
	#
	def visit_FuncDef(self, n):
		# TODO: this should be used to replace varNames[] for function parameters
		# EDIT: we don't need this, as already captured by visit_Decl!
		#fpcnt = len(n.decl.type.args.params)
		#for cnt in range(0,fpcnt):
		#	print ("-=-=> new function argument discovered [%s,%s]" % (n.decl.name,n.decl.type.args.params[cnt].name))

		if n.decl.name not in self.funcCallCnt: self.funcCallCnt[n.decl.name] = 0
		if n.decl.name not in self.funcIdCnt: self.funcIdCnt[n.decl.name] = 0
		if n.decl.name not in self.threadCallCnt: self.threadCallCnt[n.decl.name] = 0

		self.currentFunct = n.decl.name

		# Index of the compound block
		# where the body is going to be defined
		# later in this function.
		self.blockidf = self.blockid + '.%s' % self.blockcount
		#print("fdefblockid = %s" % (self.blockidf))

		# New scope detected (for now a function body is a scope)
		if n.decl.name not in self.funcName:
			self.funcName.append(n.decl.name)
			self.funcParams[self.currentFunct] = []
			self.varNames[self.currentFunct] = []
			self.funcLabels[self.currentFunct] = []
			self.varInAssignment[self.currentFunct] = {}
			self.varNoNeedInit[self.currentFunct] = {}
			self.funcExitPointsCnt[self.currentFunct] = 0

		self.funcASTNode[n.decl.name] = n

		# Note: the function definition is in two parts:
		#       one is 'decl' and the other is 'body'
		self.visitingfparams = True
		decl = self.visit(n.decl)
		self.visitingfparams = False

		if decl.startswith("void") and not decl.startswith("void *"):
			#self.parsingVoidFunction = True
			self.funcIsVoid[self.currentFunct] = True
		else:
			#self.parsingVoidFunction = False
			self.funcIsVoid[self.currentFunct] = False

		body = self.visit(n.body)
		funcBlock = decl + '\n' + body + '\n'

		# Store the return type of the functionq
		returnType = decl[:decl.find(self.currentFunct+'(')]
		returnType = returnType[:-1] if returnType.endswith(' ') else returnType
		self.funcBlockOut[self.currentFunct] = returnType

		# Store the function input parameter list
		# TODO need AST-based extraction
		self.funcBlockIn[self.currentFunct] = decl[decl.find(self.currentFunct+'(')+len(self.currentFunct)+1:decl.rfind(')')]

		self.lastFuncStmt[self.currentFunct] = self.lastStmt
		self.lastFuncStmtNode[self.currentFunct] = self.lastStmtNode

		self.currentFunct = ''
		self.blockidf = None

		return funcBlock


	def visit_Compound(self,n):
		# block-based parsing start
		oldblockcount = None

		self.blockd += 1

		# Visiting a nested block, or
		# a block at the same depth.
		if self.blockd >= len(self.block):
			oldblockcount = self.blockcount
			self.block.append(self.blockcount)
			self.blockid = '.'.join(str(self.block[i]) for i in range(0,len(self.block)))
			self.blockcount = 0
			#print ("A block[%s] blockd[%s] blockcount[%s] " % (self.block,self.blockd,self.blockcount))
		else:
			self.block.pop()
			self.block.append(self.blockcount+1)
			self.blockid = '.'.join(str(self.block[i]) for i in range(0,len(self.block)))
			self.blockcount +=1
			#print ("B block[%s] blockd[%s] blockcount[%s] " % (self.block,self.blockd,self.blockcount))
		# block-based parsing stop

		# Actual visit.
		#######print ("- block[%s] blockd[%s] blockcount[%s] " % (self.block,self.blockd,self.blockcount))

		self.blocknode[n] = self.blockid   # stores blockid for AST node n

		s = self._make_indent() + '{\n'
		self.indent_level += 1

		if n.block_items:
			for stmt in n.block_items:
				newStmt = self._getmarker(stmt) + self._generate_stmt(stmt)
				s += newStmt
				self.lastStmt = newStmt
				self.lastStmtNode = stmt

		self.indent_level -= 1
		s += self._make_indent() + '}\n'

		# block-based parsing start
		# Visiting a nested block, or
		# a block at the same depth.
		if oldblockcount is not None:
			self.blockcount = oldblockcount+1
			self.block.pop()
			self.blockid = '.'.join(str(self.block[i]) for i in range(0,len(self.block)))
			#print ("C block[%s] blockd[%s] blockcount[%s] " % (self.block,self.blockd,self.blockcount))
		else:
			#print ("D block[%s] blockd[%s] blockcount[%s] " % (self.block,self.blockd,self.blockcount))
			pass
		#
		self.blockd -= 1
		# block-based parsing stop

		return s


	def visit_ID(self, n):
		# Note:
		# line no. extraction to populate varOccurrence[] has been disabled
		# (not a big problem for now as current modules only consider the number of elements rather than its content)
		#
		if not self.visitingField:
			# if n.coords: # ifself.nodecoords[n]:
			if n.name in self.varNames[self.currentFunct]:
				#self.varOccurrence[self.currentFunct,n.name].append(int(self.nodecoords[n][1:self.nodecoords[n].rfind(':')]))
				self.varOccurrence[self.currentFunct,n.name].append(0)  # disable line no. for robustness
			elif n.name in self.varNames['']:
				#self.varOccurrence['',n.name].append(int(self.nodecoords[n][1:self.nodecoords[n].rfind(':')]))
				self.varOccurrence['',n.name].append(0)   # disable line no. for robustness

		# Detecting pointer-to-function references (i.e.: when a function name is used for anything else than a function call)
		#
		'''
		if n.name in self.funcName:
			prev = str(self.__stack[len(self.__stack)-2])
			prevnode = str(self.__stack[len(self.__stack)-2])
			#print "visiting function : %s (prev:%s)" % (n.name, prev)
			#print str(self.__stack) + '   prev:' + str(self.__stack[len(self.__stack)-2])

			##if prev != 'FuncCall':    # TODO this is too simple
			if 'FuncCall' not in self.__stack:    # TODO need a proper AST pattern
			#######if type(prevnode) == pycparser.c_ast.funcCall:
				self.funcReferenced.append(n.name)
				# TODO: inline function from pointer (n.name)
		'''

		if n.name in self.funcName:
			if n.name not in self.funcIdCnt: self.funcIdCnt[n.name] = 1
			else: self.funcIdCnt[n.name] += 1

		if (self.currentFunct != '' and n.name in self.varInAssignment[self.currentFunct]):
			self.varInAssignment[self.currentFunct][n.name] += 1

		if (self.currentFunct,n.name) in self.varrange and self.varrange[self.currentFunct,n.name] == '*':
			#print "A propagating non-determinism due to variable (%s,%s)" % (self.currentFunct,n.name)
			self._nondetfound = True
		elif ('',n.name) in self.varrange and self.varrange['',n.name] == '*':
			#print "B propagating non-determinism due to variable (%s,%s)" % (self.currentFunct,n.name)
			self._nondetfound = True

		return n.name


	def visit_Case(self, n):
		s = 'case ' + self.visit(n.expr) + ':\n'
		self.indent_level += 2
		for stmt in n.stmts:
			s += self._generate_stmt(stmt)
		self.indent_level -= 2
		return s


	def visit_Default(self, n):
		s = 'default:\n'
		self.indent_level += 2
		for stmt in n.stmts:
			s += self._generate_stmt(stmt)
		self.indent_level -= 2
		return s


	def visit_Decl(self, n, no_type=False):
		#if n.name not in self.symbols and n.name is not None:
		#TODO in order to replace varNames[] based on _generate_type(), start from the following:
		#print("DECL name:%s  type:%s" % (n.name,type(n.type)))

		if 1: #n.name is not None:
			if isinstance(n.type,pycparserext.ext_c_parser.FuncDeclExt):
				#print ("- - > new function declared       [%s,%s] ===============" % (self.blockid,n.name))
				pass
			#elif isinstance(n.type,pycparser.c_parser.FuncDecl):
			#	pass
			elif isinstance(n.type,pycparser.c_ast.Struct):
				if 1: #n.type.decls:
					#print ("= - > new structure declared             [%s,%s,%s]  ===============" % (self.blockid,n.type.name,n.type.decls))
					self.struct[self.blockid,n.type.name] = n.type
			elif isinstance(n.type,pycparser.c_ast.Union):
				#print ("- - > new union declared             [%s,%s]  ===============" % (self.blockid,n.type.name))
				self.union[self.blockid,n.type.name] = n.type
			elif isinstance(n.type,pycparser.c_ast.TypeDecl): ## and not self.parsingStructOrUnion: # and not self.visitingfparams and self.blockidf:
				#print ("- - > new variable declared             [%s,%s]  ===============" % (self.blockid,n.name))
				self.var[self.blockid,n.name] = n
				if isinstance(n.type.type,pycparser.c_ast.Struct):
					if n.type.type.decls:
						#print ("- - > new structure declared            [%s,%s,%s]  ===============" % (self.blockid,n.type.type.name,n.type.type.decls))
						self.struct[self.blockid,n.type.type.name] = n.type.type
				if isinstance(n.type.type,pycparser.c_ast.Union):
					if n.type.type.decls:
						#print ("- - > new union declared            [%s,%s,%s]  ===============" % (self.blockid,n.type.type.name,n.type.type.decls))
						self.union[self.blockid,n.type.type.name] = n.type.type
			elif isinstance(n.type,pycparser.c_ast.PtrDecl) and not self.parsingStructOrUnion and not self.visitingfparams and self.blockidf:
				#print ("- - > new variable declared (pointer)   [%s,%s]  ===============" % (self.blockid,n.name))
				self.var[self.blockid,n.name] = n
			elif isinstance(n.type,pycparser.c_ast.ArrayDecl) and not self.parsingStructOrUnion and not self.visitingfparams and self.blockidf:
				#print ("- - > new variable declared (array)     [%s,%s]  ===============" % (self.blockid,n.name))
				self.var[self.blockid,n.name] = n
			elif self.parsingStructOrUnion:
				#print ("- - > new field discovered             [%s,%s]  %s===============" % (self.blockid,n.name,n.type))
				pass
			elif self.visitingfparams:   # only function definitions, exclude function declarations
				#print ("- - > new function parameter discovered         [%s,%s]  %s===============" % (self.blockidf,n.name,n.type))
				self.var[self.blockidf,n.name] = n
				pass
			else:
				pass

		#if n.name not in self.symbols and n.name is not None:
		# new symbol table (TODO)
		#self.__symbolsstack.append(n.name)
		#self.symbols.append( (self.__symbolscount,n.name) )
		#self.__symbolscount += 1
		######self.decl[symbol] = AST node where the symbol is defined!
		##self.symbolsparents[n.name] = self....  # the symbol's full parents stack
		##self.symbolsblock[n.name] = self.....   # the symbol's full block/compound stack (e.g. 0:1:20:2 - block 0: is the global scope)
		#### self.symbolshierarchy[n.name, <currentblock/currentscope>]
		'''
		print "NEW SYMBOL"
		print "     %s" % n.name
		print "    [%s]" % self.__symbolsstack[-1]
		print "    [%s]" % self.__symbolsstack
		print "    is a pointer? %s" % ('c_ast.PtrDecl' in str(n.type))
		print "    is a pointer? %s" % (n.children())
		'''
		#### generate_type(n.type)

		# no_type is used when a Decl is part of a DeclList, where the type is
		# explicitly only for the first delaration in a list.

		#
		s = n.name if no_type else self._generate_decl(n)

		if self.currentFunct != '':   # Inside a function
			self.varInAssignment[self.currentFunct][n.name] = 0   # Just a declaration

		if n.bitsize: s += ' : ' + self.visit(n.bitsize)

		if n.init:
			if isinstance(n.init, pycparser.c_ast.InitList):
				s += ' = {' + self.visit(n.init) + '}'
			elif isinstance(n.init, pycparser.c_ast.ExprList):
				s += ' = (' + self.visit(n.init) + ')'
			else:
				s += ' = ' + self.visit(n.init)

		#if 'FuncDecl' in str(n.type) and self.currentFunct == '':
		if ((isinstance(n.type,pycparser.c_ast.FuncDecl) or
			isinstance(n.type,pycparserext.ext_c_parser.FuncDeclExt)) and
			self.currentFunct == ''):
			self.funcDecl[n.name] = s

		#if n.name is not None and len(self.__symbolsstack) > 0:
		#	self.__symbolsstack.pop()

		return s


	def visit_Struct(self, n):
		# NO
		#if (self.blockid,n.name) not in self.struct:
		#	print ("- - > new structure discovered             [%s,%s]===============" % (self.blockid,n.name))
		#	self.struct[self.blockid,n.name] = n

		# Assign a name to anonymous structs
		#if n.name == None:
		#	n.name = '__CS_anonstruct_' + str(self.currentAnonStructsCount)
		#	self.currentAnonStructsCount += 1

		# This method is called more than once on the same struct,
		# the following is done only on the first time.
		#
		if n.name not in self.structName:
			self.currentStruct = n.name
			self.structName.append(n.name)
			self.varNames[self.currentStruct] = []

		oldParsingStruct = self.parsingStructOrUnion
		self.parsingStructOrUnion = True
		# s = self._generate_struct_union(n, 'struct')   # pycparser <= 2.18
		#s = self._generate_struct_union_enum(n, 'struct')  # pycparser 2.19
		s = super(self.__class__, self).visit_Struct(n)

		self.parsingStructOrUnion = oldParsingStruct

		# Parsing  typedef struct
		'''
		if self.parsingTypedef:
			print "    PARSING TYPEDEF STRUCT!!!!!!"
			print "       s: " + s
			print "    name: " + str(n.name)
		'''

		return s


	def visit_StructRef(self, n):
		sref = self._parenthesize_unless_simple(n.name)

		oldVisitingField = self.visitingField
		self.visitingField = True

		field = self.visit(n.field)

		self.visitingField = oldVisitingField

		return sref + n.type + field


	def visit_UnaryOp(self, n):
		operand = self._parenthesize_unless_simple(n.expr)
		oper = operand[:operand.find('[')] if '[' in operand else operand # could be an array: remove indexes

		if n.op == 'p++': return '%s++' % operand
		elif n.op == 'p--': return '%s--' % operand
		elif n.op == 'sizeof': return 'sizeof(%s)' % self.visit(n.expr)
		elif n.op == '*':
			#print "DEREFERENCING %s (line:%s)" % (operand, self.nodecoords[n]);
			#if n.coords: #self.nodecoords[n]:
			if oper in self.varNames[self.currentFunct]:
				#self.varDeReferenced[self.currentFunct,oper].append(int(self.nodecoords[n][1:]))
				self.varDeReferenced[self.currentFunct,oper].append(0)
			elif oper in self.varNames['']:
				#self.varDeReferenced['',oper].append(int(self.nodecoords[n][1:]))
				self.varDeReferenced['',oper].append(0)

			return '%s%s' % (n.op, operand)
		elif n.op == '&':
			#print "REFERENCING %s / %s (line:%s)" % (operand, oper, self.nodecoords[n]);

			# Note:
			# line no. extraction to populate varReferenced[] has been disabled
			# (not a big problem for now as current modules only consider the number of elements rather than its content)
			#
			#if n.coords: #self.nodecoords[n]:
			if oper in self.varNames[self.currentFunct]:  # local variable
				#self.varReferenced[self.currentFunct,oper].append(int(self.nodecoords[n][1:self.nodecoords[n].rfind(':')]))
				self.varReferenced[self.currentFunct,oper].append(0)
			elif oper in self.varNames['']:               # global variable
				#self.varReferenced['',oper].append(int(self.nodecoords[n][1:self.nodecoords[n].rfind(':')]))
				self.varReferenced['',oper].append(0)

			return '%s%s' % (n.op, operand)
		else: return '%s%s' % (n.op, operand)


	def visit_Union(self, n):
		oldParsingStruct = self.parsingStructOrUnion
		self.parsingStructOrUnion = True
		s = self._generate_struct_union(n, 'union')
		# s = self._generate_struct_union_enum(n, 'union')   # pycparser 2.19
		self.parsingStructOrUnion = oldParsingStruct

		return s


	def visit_Assignment(self, n):
		lval_str = self.visit(n.lvalue)

		# Tracks non-nondeterminism, only for scalar variables at the moment TODO
		oldnondetfound = self._nondetfound   # probably useless?!
		self._nondetfound = False

		rval_str = self._parenthesize_if(n.rvalue, lambda n: isinstance(n, pycparser.c_ast.Assignment))

		if self._nondetfound and type(n.lvalue) == pycparser.c_ast.ID:
			# Resolve variable scope 
			variablecontext = ''

			#if self.currentFunct != '':
			if lval_str in self.varNames[self.currentFunct]:
				#print "variable %s is local to function %s" % (lval_str,self.currentFunct)
				variablecontext = self.currentFunct
			#else: print "variable %s is global" % (lval_str)

			self.varrange[variablecontext,lval_str] = '*'

		self._nondetfound = oldnondetfound

		#
		if (self.currentFunct != '' and
			lval_str in self.varInAssignment[self.currentFunct] and
			self.varInAssignment[self.currentFunct][lval_str] == 1):

			if self.currentFunct in self.varNoNeedInit:
				self.varNoNeedInit[self.currentFunct][lval_str] = True

		return '%s %s %s' % (lval_str, n.op, rval_str)


	def visit_Return(self,n):
		self.funcExitPointsCnt[self.currentFunct] += 1

		s = 'return'
		if n.expr: s += ' ' + self.visit(n.expr)

		return s + ';'


	def _generate_decl(self,n):
		#print("DECL %s, %s, %s parsingstruct:%s" % (n.name, self.currentFunct, self.currentStruct, self.parsingStructOrUnion))

		""" Generation from a Decl node.
		"""
		s = ''

		# use flags to keep track through recursive calls of what is being parsed (START)
		###if 'FuncDecl' in str(n.type):
		if (isinstance(n.type,pycparser.c_ast.FuncDecl) or
			isinstance(n.type,pycparserext.ext_c_parser.FuncDeclExt)):
			oldParsingFuncDecl = self.parsingFuncDecl
			self.parsingFuncDecl = True
			###self.varNames[self.currentFunct] = []

		#if 'Struct' in str(n.type): self.parsingStructOrUnion = True
		if isinstance(n.type,pycparser.c_ast.Struct): self.parsingStructOrUnion = True

		if n.funcspec: s = ' '.join(n.funcspec) + ' '
		if n.storage: s += ' '.join(n.storage) + ' '

		s += self._generate_type(n.type)

		# use flags to keep track through recursive calls of what is being parsed (END)
		#if 'FuncDecl' in str(n.type):
		if (isinstance(n.type,pycparser.c_ast.FuncDecl) or
			isinstance(n.type,pycparserext.ext_c_parser.FuncDeclExt)):
			self.parsingFuncDecl = oldParsingFuncDecl

		#if 'Struct' in str(n.type): self.parsingStructOrUnion = False
		if isinstance(n.type,pycparser.c_ast.Struct): self.parsingStructOrUnion = False


		""" Handling of struct declarations.
		"""
		#if 'Struct' in str(n.type):
		if isinstance(n.type,pycparser.c_ast.Struct):
			# new structure declaration
			1
			if self.parsingStructOrUnion:
				# new field in a structure
				1

		""" Handling of variable declarations.

			Each variable has the following info associated with it:

				name, type, kind, arity, size

			name
		    	varName[''] = list of global variables
		    	varName['x'] = list local variables in function or struct 'x'
				              (incl. input params for functions)

			type
				the type as declared in the original code (e.g. 'unsigned int', 'char *', ...)

			kind
				'g'  for global variables
				'l'  for local variables
				'p'  for function input parameters
				'f'  for struct fields

			arity
				0  for scalar variables
				k  for for k-dimensional arrays

			size
				[] for scalar variables
				[size1, ..., sizek] for k-dimensional arrays

		"""
		# Whatever is not a function or a struct here, is a variable declaration
		# TODO: see what else should be excluded to only have var declarations after the if
		#
		#if 'FuncDecl' not in str(n.type) and 'Struct' not in str(n.type) and 'Union' not in str(n.type):
		if (not isinstance(n.type,pycparser.c_ast.FuncDecl) and
			not isinstance(n.type,pycparserext.ext_c_parser.FuncDeclExt) and
			not isinstance(n.type,pycparser.c_ast.Struct) and
			not isinstance(n.type,pycparser.c_ast.Union)):
			# Variable name (for variables) or field name (for structs fields).
			#
			# At this point,
			# any variable declaration can occur (a) in the global scope,
			# or (b) in a function or (c) in a struct.
			#
			# Each of those will have a name, apart from the global scope,
			# for which name we use the empty string. We call it Context. 
			#
			# For example,
			#   if a variable V is declared in a function F, its Context is F.
			#   if a variable V is declared in a struct S, its Context is S.
			#   if a variable V is declared globally, its Context is ''.
			#
			# We use the context to index the arrays:
			# (1) to index the array name
			# (2) to index the arrays type, kind, arity, size,
			# in this case with the tuple (context, variable)
			#
			if not self.parsingStructOrUnion: variableContext = self.currentFunct
			else: variableContext = self.currentStruct

			#self.varPtrToFunct[variableContext,n.name] = None
			##print "appending var  [%s]\n          from context [%s]\n          type [%s]\n          string [%s]\n\n\n" % (n.name, variableContext, n.type, s)  

			if (not n.name in self.varNames[variableContext] and    # avoid duplicates
				self.__stack.count('ParamList') <= 1):              # do not consider nested declarations (example: int f1(int (f2(int a, int b)))
				#print("***** appending var  [%s]\n          from context [%s]\n          type [%s] type [%s]\n          string [%s]" % (n.name, variableContext, n.type, type(n), s)  )
				### print "***** " + str(self.__stack) + '   prev:' + str(self.__stack[len(self.__stack)-2])
				### print "***** PARAMLIST COUNT " + str(self.__stack.count('ParamList')) + '\n\n'

				# new variable or field discovered
				self.varNames[variableContext].append(n.name)       #
				#print( "----> new variable or field discovered [%s,%s]" % (variableContext,n.name))
				self.varID[variableContext,n.name] = self.varCount  # associate each new variable with a unique IDs
				self.varReferenced[variableContext,n.name] = []
				self.varDeReferenced[variableContext,n.name] = []
				self.varOccurrence[variableContext,n.name] = []

				if n.init: self.varInitExpr[variableContext,n.name] = True
				else: self.varInitExpr[variableContext,n.name] = False

				self.varCount += 1

			# Variable or field type
			if s.count('[') > 0: s2 = s[ :s.find('[')]
			else: s2 = s

			if n.name:
				if s2.endswith(n.name): s2 = s2[:-len(n.name)]
				else: s2 = s2.replace(n.name, '')
			if s2.endswith(' '): s2 = s2[:-1]

			# Typedef expansion:
			# when some type of variable is found for which there is an entry in the list of typedefs,
			# expands directly in the symbol table the corresponding string.
			#
			self.varTypeUnExpanded[variableContext,n.name] = s2

			for x in self.typedefs:
				#print ("found %s ---> %s" % (x, self.typedefExpansion[x]))

				if s2 == x: s2 = self.typedefExpansion[x]
				if s2.startswith(x+ ' '): s2 = s2.replace(x+' ', self.typedefExpansion[x]+' ', 1)

				s2 = s2.replace(' '+x+' ', ' '+self.typedefExpansion[x]+' ')

			s2 = s2.replace('\n', '')
			s2 = s2.replace('\t', ' ')
			self.varType[variableContext,n.name] = s2.rstrip()
			#print( "     new variable or field discovered [%s,%s] type:%s" % (variableContext,n.name,s2.rstrip()))
			#print( "     new variable or field discovered [%s,%s] type:%s" % (variableContext,n.name,self.varTypeUnExpanded[variableContext,n.name]))
			### self.varType[variableContext,n.name] = n.type
			###print "variable added %s %s" % (n.name, n.type)
			###print str(self.__stack) + '   prev:' + str(self.__stack[len(self.__stack)-2]) + '\n\n'

			# Variable kind
			if self.parsingFuncDecl:    # parameter (from a function declaration)
				#self.varKind[variableContext, n.name] = 'p'
				if variableContext != '': self.funcParams[variableContext].append(n.name)

				## print "FOUND MAIN PARAMETER %s, DECL %s\n\n" % (n.name, s)
				if variableContext == 'main':
					varDecl = s;
					varDecl = varDecl.replace(' '+n.name, ' __CS_main_arg_'+n.name)
					varDecl = varDecl.replace(' *'+n.name, ' *__CS_main_arg_'+n.name)
					varDecl = varDecl.replace(' *__CS_main_arg_'+n.name+'[]', ' **__CS_main_arg_'+n.name)

					self.mainParametersDecl += '\t' + varDecl + ';\n'   ### TODO
			#elif self.parsingStructOrUnion:    # field in a struct (this are not really variables, but we handle them using the same data structures)
			#	self.varKind[variableContext, n.name] = 'f'
			#elif self.indent_level < 1:  # global variable
			#	self.varKind[variableContext, n.name] = 'g'
			#else:                       # local variable
			#	self.varKind[variableContext, n.name] = 'l'

			# Variable arity (scalars have arity 0, vectors 1, etc.)
			self.varArity[variableContext,n.name] = int(s.count('['))   # TODO this needs to be properly calculated

			# Variable size(s) (for scalars this is an empty array)
			self.varSize[variableContext,n.name] = []

			tmp_s = s
			i = self.varArity[variableContext,n.name]

			while i > 0:
				tmp = tmp_s[tmp_s.find("[")+1:tmp_s.find("]")]
				if tmp == '': ithSize = -1              # Unbounded array. This is equivalent to declare a pointer. TODO
				###elif not tmp.isdigit(): ithSize = -2    # Array size given by a complex expression. This is like dynamically allocated blocks. TODO
				elif not tmp.isdigit(): ithSize = tmp   # Array size given by a complex expression. This is like dynamically allocated blocks. TODO
				else: ithSize = int(tmp)                # Array size given by a constant expression

				self.varSize[variableContext,n.name].append(ithSize)
				tmp_s = tmp_s[tmp_s.find("]")+1:]
				i = i-1

		return s


	#
	def blockdefid(self,block,variable):
		b = block
		v = variable

		i = 0

		while (b,v) not in self.var and b != '0':
 			b = b[:b.rfind('.')]  # search within enclosing block
			#print("[%d] going up %s" % (i,b))
 			i += 1

		if (b,v) in self.var and b == '0': # global variable
			return b

		if (b,v) in self.var and b != '0': # local variable
			return b

		# Then v is not a variable, e.g., may be a enum field, a function identifier, etc.
		#self.warn("unable to calculate scope for identifier '%s', block:%s" % (v,b))

		return None

	# Checks whether there is a global variable v visible from block b.
	def isglobal(self,b,v):
		return True if self.blockdefid(b,v) is '0' else False

	# Checks whether there is a pointer variable v visible from block b.
	def ispointer(self,b,v):
		c = self.blockdefid(b,v)

		if c:
			# no linemarks from core.Parser
			t = self._generate_type(self.var[c,v].type)
			return True if '*' in t else False

		return False  # not found anyway

	# Checks if there is variable v visible from block b, and
	# returns its type if so.
	def buildtype(self,b,v):
		c = self.blockdefid(b,v)

		if c:
			# no linemarks from core.Parser
			t = self._generate_type(self.var[c,v].type)
			return t

		return None  # not found




