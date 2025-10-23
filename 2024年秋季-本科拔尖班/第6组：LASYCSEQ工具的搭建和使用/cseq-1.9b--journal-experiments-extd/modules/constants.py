""" CSeq Program Analysis Framework
    concurrency-aware constant propagation module

Transformation 1 (binary operations, including nested expressions):
e.g. 4 + 3*2  --->  10

Transformation 2:
Simple workaround for expressions that contains global (and thus potentially shared) variables

Author:
    Omar Inverso

Changes:
    2020.03.25 (CSeq 2.0)
    2019.11.27 [SV-COMP 2020] this module uses the new symbol table in Parser()
    2019.11.27  evaluation of sizeof() (only 32-bit architecture for now)
    2019.11.20 (CSeq 1.9 pycparserext)
    2019.11.20  statement expression workaround to avoid breaking the syntax
    2019.11.16  moved internal parser to pycparserext
    2019.11.15  using __VERIFIER_xyz() primitives rather than __CSEQ_xyz()
    2018.10.28  merged binaryop handling from [ICCPS 2018] constantfolding module
    2018.05.26  handling integer division (when possible) and multiplication
    2017.07.21  started from scratch
    2015.11.07 (CSeq 1.0) [SV-COMP 2016]
    2014.12.24 (CSeq 1.0beta)
    2014.12.09  further code refactory to match the new organisation of the CSeq framework
    2014.10.26 (CSeq Lazy-0.6,newseq-0.6a,newseq-0.6c) [SV-COMP 2015]
    2014.10.26  removed dead/commented-out/obsolete code
    2014.10.15  removed visit() and moved visit call-stack handling to module class (module.py)
    2014.03.14 (CSeq Lazy-0.4)
    2014.03.14  further code refactory to match module.Module class interface
    2014.02.25 (CSeq Lazy-0.2) switched to module.Module base class for modules

To do:
  - urgent: need full code review
  - urgent: need to move transformation 2 (non-atomicity of binary operations)
            of the sequentialisation stage.
  - only works on integer constants
  - transformation 2 uses int for temporary variables
  - transformation 2 only considers binary operations on the RHS

"""
import pycparserext.ext_c_parser, pycparser.c_ast, pycparserext.ext_c_generator
import core.module, core.parser, core.utils
import re


#class MyParser(pycparserext.ext_c_generator.GnuCGenerator):
#	def __init__(self):
#		self.__considervar = ''
#		self.__hasConsidervar = False
#		self.indent_level = 0
#
#	def setConsidervar(self, string):
#		self.__considervar = string
#
#	def getHasConsidervar(self):
#		return self.__hasConsidervar
#
#	def setHasConsidervar(self, value):
#		self.__hasConsidervar = value
#
#	def visit(self, node):
#		method = 'visit_' + node.__class__.__name__
#		ret = getattr(self, method, self.generic_visit)(node)
#		if ret == self.__considervar:
#			self.__hasConsidervar = True
#		return ret


class constants(core.module.Translator):
	deeppropagation = False    # evaluate sizeof (experimental)
	visitingfunction = False   # true while vising a function definition
	visitingcompound = False   # true while visiting a compound

	_tmpvarcnt = 0
	__globalMemoryAccessed = False
	__currentFunction = ''
	__atomicSection = False

	_ids = []   # list of variables potentially accessing the global memory


	def init(self):
		self.inputparam('deep-propagation', 'deep constant folding and propagation (exp)', '', default=None, optional=True)


	def loadfromstring(self, string, env):
		self.deeppropagation = True if self.getinputparam('deep-propagation') is not None else False

		a = super(self.__class__, self).loadfromstring(string, env)
		#print  ("VARS: %s" % self.Parser.var)
		#print  ("STRUCTS: %s" % self.Parser.struct)
		#print  ("UNIONS: %s" % self.Parser.union)
		#print  ("TYPES: %s\n\n" % self.Parser.type)


	def visit_FuncDef(self, n):
		self.__currentFunction = n.decl.name
		decl = self.visit(n.decl)

		self.__atomicSection = False
		if n.decl.name.startswith("__VERIFIER_atomic_"):
			self.__atomicSection = True

		self.indent_level = 0

		body = self.visit(n.body)

		self.__currentFunction = ''

		if n.param_decls:
			knrdecls = ';\n'.join(self.visit(p) for p in n.param_decls)
			return decl + '\n' + knrdecls + ';\n' + body + '\n'
		else:
			return decl + '\n' + body + '\n'


	def visit_Assignment(self, n):
		# The original code below breaking statement expressions?!
		#rval_str = self._parenthesize_if(n.rvalue,lambda n: isinstance(n, pycparser.c_ast.Assignment))
		#return '%s %s %s' % (self.visit(n.lvalue), n.op, rval_str)

		oldids = self._ids
		lids = []
		rids = []

		self._ids = []		
		lval_str = self.visit(n.lvalue)
		lids = self._ids

		self._ids = []		
		rval_str = self._parenthesize_if(n.rvalue, lambda n: isinstance(n, pycparser.c_ast.Assignment))
		rids = self._ids

		commonids = [value for value in lids if value in rids] 

		# TODO still wrongly detecting that
		#      the b in a.b and
		#      the b at the right of the assignment are the same identifier
		#     (a weird way of over-approximating..)
		if len(commonids) > 0 and n.op == '=':    # TODO handle +=, ...
			if type(self.stacknodes[-2]) == pycparser.c_ast.Assignment:
				self.warn("nested assignment statements involving potentially unsafe memory accesses")
			else:
				v = commonids[0]

				#self.warn("!!!! %s %s (%s)" % (lval_str, n.op, rval_str))
				#self.warn("!!!! left:[%s] right:[%s] common:[%s]" % (lids,rids,commonids))
				t = self.Parser.buildtype(self.blockid,v)

				if t.endswith(v): t = t[:t.rfind(v)]
				else:
					self.warn("storing temporary expression for '%s' as 'int'" % (t))
					t = 'int'  # TODO (but might still work fine for pointers &co.)

				# Declare a temporary variable for this statement
				semicolon = ';'  # TODO only when visiting a labelled statement
				ret = semicolon  
				ret += ' %s __cs_temporary_%s = 0; __cs_temporary_%s = %s; ' % (t,self._tmpvarcnt,self._tmpvarcnt,rval_str)
				ret += '%s %s %s' % (lval_str, n.op, '__cs_temporary_%s' % self._tmpvarcnt)
				self._tmpvarcnt += 1

				#self.warn("[[[ %s ]]]\n\n\n" % ret)
				return ret

		ret = '%s %s (%s)' % (lval_str, n.op, rval_str)

		return ret


	def visit_Compound(self, n):
		old = self.visitingcompound
		self.visitingcompound = True

		s = super(self.__class__, self).visit_Compound(n)

		self.visitingcompound = old

		return s


	def visit_ID(self, n):
		## Find the block (if any) where n was declared.
		#scope = self._blockdefid(self.blockid,n.name)
		#ptr = self._ispointer(self.blockid,n.name)
		#
		#if scope and ptr:
		#	a = self.Parser._generate_type(self.Parser.var[scope,n.name].type)
		#	self.warn("visiting id [%s,%s] scope:[%s] type:[%s] pointer:[%s]" % (self.blockid,n.name,scope,a,ptr))

		# If this ID corresponds either to a global variable,
		# or to a pointer...
		#
		if ((not self.visitingcompound and not self.visitingfunction and self.Parser.isglobal(self.blockid,n.name) or self.Parser.ispointer(self.blockid,n.name)) and not n.name.startswith('__cs_thread_local_')):
			#self.warn("- - - - - id [%s,%s] potentially accessing global memory" % (self.blockid,n.name))
			#self.__globalMemoryAccessed = True
			self._ids.append(n.name)

		return n.name


	def visit_FuncCall(self, n):
		self.visitingfunction = True

		fref = self._parenthesize_unless_simple(n.name)

		if fref == "__VERIFIER_atomic_begin": self.__atomicSection = True
		elif fref == "__VERIFIER_atomic_end": self.__atomicSection = False

		ret = fref + '(' + self.visit(n.args) + ')'

		self.visitingfunction = False

		return ret


	def visit_BinaryOp(self, n):
		lval_str = self._parenthesize_if(n.left, lambda d: not self._is_simple_node(d))
		rval_str = self._parenthesize_if(n.right, lambda d: not self._is_simple_node(d))

		# remove brackets enclosing constants (e.g. (1234) -> 1234)
		if lval_str.startswith('(') and lval_str.endswith(')') and self._isInteger(lval_str[1:-1]):
			lval_str = lval_str[1:-1] 

		if rval_str.startswith('(') and rval_str.endswith(')') and self._isInteger(rval_str[1:-1]):
			rval_str = rval_str[1:-1] 

		if self._isInteger(lval_str) and self._isInteger(rval_str):
			if n.op == '-': return str(int(lval_str) - int(rval_str))
			if n.op == '+': return str(int(lval_str) + int(rval_str))
			if n.op == '*': return str(int(lval_str) * int(rval_str))
			if n.op == '/' and (int(lval_str) % int(rval_str) == 0): return str(int(lval_str) / int(rval_str))

		return '%s %s %s' % (lval_str, n.op, rval_str)


	bytewidth = {}
	bytewidth['long'] = 4 
	bytewidth['unsigned'] = 4 
	bytewidth['signed'] = 4 
	bytewidth['int'] = 4

	bytewidth['_Bool'] = 1
	bytewidth['char'] = 1
	bytewidth['short'] = 2
	bytewidth['long'] = 4
	bytewidth['long int'] = 4
	bytewidth['long long'] = 8
	bytewidth['float'] = 4
	bytewidth['double'] = 8
	bytewidth['*'] = 4

	def _simplify_type(self,typestring):
		if typestring.startswith('const '): typestring = typestring.replace('const ', '', 1)
		if typestring.startswith('unsigned '): typestring = typestring.replace('unsigned ', '', 1)
		if typestring.startswith('signed '): typestring = typestring.replace('signed ', '', 1)
		#if typestring.endswith(' *') and typestring.count('*') ==1: typestring = 'int'
		return typestring


	def visit_UnaryOp(self, n):
		operand = self._parenthesize_unless_simple(n.expr)
		if n.op == 'p++':
			return '%s++' % operand
		elif n.op == 'p--':
			return '%s--' % operand
		elif n.op == 'sizeof':
			# Always parenthesize the argument of sizeof since it can be
			# a name.
			expr = self.visit(n.expr)


			#self.warn("-----> sizeof(%s)" % expr)
			a = None
			if self.deeppropagation: a = self._evaluate_sizeof(n.expr) 

			'''
			if expr == 'struct platform_device':
				return '%s' % 100
			if expr == 'struct kobject':
				return '%s' % 60
			if expr == 'struct dentry':
				return '%s' % 24
			'''

			if a:
				#self.warn("<----- %s\n\n" % a)
				self.debug("evaluating 'sizeof(%s)' to '%s'" % (expr,a))
				return '%s' % a
			else:
				#self.warn("not evaluating 'sizeof(%s)'" % (expr))
				#self.warn("<----- sizeof(%s)\n\n" % expr)
				return 'sizeof(%s)' % expr
		else:
			return '%s%s' % (n.op, operand)


	''' In order to achieve a deeper program simplification,
		evaluate sizeof().

		This is highly experimental.

		TODO: this assumes 32bits,
		      should add a parameter for 64bit byte width lookup tables for the basic datatypes.
	'''
	def _evaluate_sizeof(self, n, modifiers=[]):
		typ = type(n)
		name = n.name if hasattr(n,'name') else ''
		#print ("    visit? (%s,%s) typ:%s" % (self.blockid,name,typ))

		w = None

		if typ == pycparser.c_ast.ID:
			# e.g., sizeof(int)
			if n.name in self.bytewidth:
				w = self.bytewidth[n.name]
			# e.g., sizeof(varname) or sizeof(struct acjfdh)
			else:
				# need to check within the enclosing scopes too
				# TODO: the position of variables and their declaration within the scope is ignored!
				block = self.blockid

				while (block,n.name) not in self.Parser.var and block != '0':
					block = block[:block.rfind('.')]

				if (block,n.name) in self.Parser.var:
					w = self._evaluate_sizeof(self.Parser.var[block,n.name].type)
		elif typ == pycparser.c_ast.Typedef:
			w = self._evaluate_sizeof(n.type)
		elif typ == pycparser.c_ast.IdentifierType:
			t = ' '.join(n.names)
			t = self._simplify_type(t)

			if t in self.bytewidth:
				w = self.bytewidth[t]
			else:
				# typedef
				block = self.blockid

				while (block,t) not in self.Parser.type and block != '0':
					block = block[:block.rfind('.')]

				if (block,t) in self.Parser.type:
					t = self.Parser.type[block,t].type
					w = self._evaluate_sizeof(t)

		elif typ == pycparser.c_ast.Struct:
			block = self.blockid

			while (block,n.name) not in self.Parser.struct and block != '0':
				block = block[:block.rfind('.')]

			s = self.Parser.struct[block,n.name].decls

			cnt = 0

			if s is not None:
				for f in s:
					cnt += self._evaluate_sizeof(f)
			else:
				#print ("     none!")
				pass

			w = cnt
		elif typ == pycparser.c_ast.Union:
			block = self.blockid

			while (block,n.name) not in self.Parser.union and block != '0':
				block = block[:block.rfind('.')]

			s = self.Parser.union[block,n.name].decls

			cnt = 0

			if s is not None:
				for f in s:
					cnt = max(cnt,self._evaluate_sizeof(f))

			w = cnt
		elif typ == pycparser.c_ast.Decl:
			w = self._evaluate_sizeof(n.type)
		elif typ == pycparser.c_ast.TypeDecl:
			w = self._evaluate_sizeof(n.type)
		elif typ == pycparser.c_ast.Typename:
			w = self._evaluate_sizeof(n.type)
		elif typ == pycparser.c_ast.ArrayDecl:
			s = int(self.visit(n.dim))*self._evaluate_sizeof(n.type)
			w = s
		elif typ == pycparser.c_ast.PtrDecl:
			return self.bytewidth['*']
		elif typ == pycparser.c_ast.FuncDecl:
			self.debug("evaluation of sizeof not supported for type '%s'" % (typ))
			w = None
		else:
			self.debug("evaluation of sizeof not supported for type '%s'" % (typ))
			w = None

		#print ("    visit! (%s,%s) typ:%s  w:%s" % (self.blockid,name,typ,w))
		return w


	def _isInteger(self, s):
		if s[0] in ('-', '+'): return s[1:].isdigit()
		else: return s.isdigit()


	'''
	def _blockdefid(self,block,variable):
		b = block
		v = variable

		while (b,v) not in self.Parser.var and b != '0':
 			b = b[:b.rfind('.')]  # search within enclosing block

		if (b,v) in self.Parser.var and b == '0': # global variable
			return b

		if (b,v) in self.Parser.var and b != '0': # local variable
			return b

		# Then v is not a variable, e.g., may be a enum field, a function identifier, etc.
		#self.warn("unable to calculate scope for identifier '%s', block:%s" % (v,b))

		return None

	# Checks whether there is a global variable v visible from block b.
	def isglobal(self,b,v):
		return True if self.Parser.blockdefid(b,v) is '0' else False

	# Checks whether there is a pointer variable v visible from block b.
	def ispointer(self,b,v):
		c = self.Parser.blockdefid(b,v)

		if c:
			# no linemarks from core.Parser
			t = self.Parser._generate_type(self.Parser.var[c,v].type)
			return True if '*' in t else False

		return False  # not found anyway

	# Checks if there is variable v visible from block b, and
	# returns its type if so.
	def buildtype(self,b,v):
		c = self.Parser.blockdefid(b,v)

		if c:
			# no linemarks from core.Parser
			t = self.Parser._generate_type(self.Parser.var[c,v].type)
			return t

		return None  # not found
	'''



