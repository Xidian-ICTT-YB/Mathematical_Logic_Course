""" CSeq Program Analysis Framework
    function inlining preliminary module

Removes nested function calls, for example by transforming from:

    f(g(x));

to:

    var tmp = g(x); f(var);

Author:
    Omar Inverso

Changes:
    2020.03.24 (CSeq 2.0)
    2019.11.21 [SV-COMP 2020]
    2018.11.27  good luck

Notes:
  - this should be part of the inlining module

"""
import copy,re
import pycparserext.ext_c_parser, pycparser.c_ast, pycparserext.ext_c_generator
from pycparser import c_ast
import core.module, core.parser, core.utils


class preinliner(core.module.Translator):
	depth = 0
	extra = ''             # code to inject right before the nested call within the same block
	extracnt = 0
	depth = 0
	countextravars = 0     # temporary variable to store the return value of the nested call
	cnt = [0]


	def init(self):
		pass


	def visit_Compound(self, n):
		s = self._make_indent() + '{\n'
		self.indent_level += 2

		if n.block_items:
			blocks = ''

			for stmt in n.block_items:
				block = self._generate_stmt(stmt)

				if self.extra != '':
					blocks += self._make_indent()+self.extra + block
					self.extra = ''
				else: 
					blocks += block

			s += blocks 

		self.indent_level -= 2
		s += self._make_indent() + '}\n'
		return s


	def visit_ExprList(self, n):
		visited_subexprs = []

		for expr in n.exprs:
			self.cnt[-1] +=1
			if isinstance(expr, pycparser.c_ast.ExprList):
				visited_subexprs.append('{' + self.visit(expr) + '}')
			else:
				visited_subexprs.append(self.visit(expr))

		return ', '.join(visited_subexprs)


	'''
	'''
	def visit_FuncCall(self, n):
		fref = self._parenthesize_unless_simple(n.name)

		# Nested call
		if self.depth > 0 and self.__needsExpandedHere(fref):
			self.debug("transforming nested call (depth:%s) to function %s (in turn argument no.%s of the external call)" % (self.depth,fref,self.cnt[-1]+1))

			self.depth+=1
			args = self.visit(n.args)
			self.depth-=1

			tempvarid = '__cs_preinliner_%s' % (self.countextravars)
			s = tempvarid   # replace the nested call 

			self.countextravars+=1

			if 1: #fref in self.Parser.funcBlockOut:
				self.extra += '%s %s = %s; ' % (self.Parser.funcBlockOut[fref],tempvarid,fref + '(' + args + ')')

			return s

		# Base case (i.e., the most external function call)
		self.depth+=1
		self.cnt.append(-1)
		args = self.visit(n.args)
		s = fref + '(' + args + ')'
		self.cnt.pop()
		self.depth-=1

		return s


	''' Check whether function  f  needs to be inlined.
	'''
	def __needsInlining(self,f):
		# If the number of occurrences of the identifier of a given function
		# is greater than then number of explicit calls to that function,
		# then the function identifier is passed as a reference somewhere
		# (this includes when the function identifier is passed as an argument to
		#  pthread_create).
		# The definitions of any such function should be retained in the output.
		#
		cntoveralloccurrences = self.Parser.funcIdCnt[f]
		cntexplicitcalls = self.Parser.funcCallCnt[f]
		cntthreads = self.Parser.threadCallCnt[f]

		#self.log( "- - - -> function: %s   overall:%s   explicit:%s   threads:%s" % (f,cntoveralloccurrences,cntexplicitcalls,cntthreads))
		# function: check_gcd   overall:2   explicit:1   threads:0

		return (not f == 'main' and
			not f == '__CSEQ_assert' and
			not f == '__VERIFIER_assert' and
			not f.startswith('__VERIFIER_atomic') and 
			not cntoveralloccurrences > cntexplicitcalls and  # this also counts threads
			not cntthreads >= cntoveralloccurrences and
			f in self.Parser.funcName)


	''' Check whether function call to  f  needs to be expanded.
	'''
	def __needsExpandedHere(self,f):
		cntoveralloccurrences = self.Parser.funcIdCnt[f]
		cntexplicitcalls = self.Parser.funcCallCnt[f]
		cntthreads = self.Parser.threadCallCnt[f]

		#self.log( "= = = => function: %s   overall:%s   explicit:%s   threads:%s" % (f,cntoveralloccurrences,cntexplicitcalls,cntthreads))
		#self.log("= = = =  funcnames: %s" % (self.Parser.funcName))

		return (not f.startswith('__CSEQ_') and
			not f.startswith('__VERIFIER_') and
			#not cntoveralloccurrences > cntexplicitcalls and  # this also counts threads
			#not cntthreads >= cntoveralloccurrences and
			f in self.Parser.funcName)


