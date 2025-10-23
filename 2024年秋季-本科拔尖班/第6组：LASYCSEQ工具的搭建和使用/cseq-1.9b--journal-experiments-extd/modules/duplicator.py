""" CSeq Program Analysis Framework
    lazy sequentialisation: thread duplicator module

Last step to produce a bounded program (see CAV2014)
after running inliner+unroller on the input.

This module works on unfolded programs, and
it duplicates the functions used multiple times to create a thread,
so that each thread creation refers to a distinct function.

The number of copies is the number of times that the function
is used as an argument to pthread_create().

The copies share the body, and
the name of the function is indexed by adding a trailing counter.

The calls to pthread_create() are updated accordingly.

For example,
	the following input code:
		thread() { ... }

		pthread_create(thread);
		pthread_create(thread);

	will generate:
		thread_0() { ... }
		thread_1() { ... }

		pthread_create(thread_0);
		pthread_create(thread_1);

Author:
	Omar Inverso

Changes:
    2020.03.24 (CSeq 2.0)
    2019.11.15 [SV-COMP 2020] no longer mapping pthread_xyz function identifiers
    2018.11.23  handling the case of same function used to spawn threads and in explicit calls
    2015.07.15 [ASE 2015]
    2015.07.15  fixed linemapping not working for non-thread functions (e.g. atomic functions) (Truc,Omar)
    2015.07.13  fixed linemapping not working from the 2nd copy of a thread onwards (Omar)
    2015.06.23  re-implemented 3rd parameter extraction from the call to pthread_create()
    2014.12.24 (CSeq 1.0beta)
    2014.12.09  further code refactory to match the new organisation of the CSeq framework
    2014.10.26 (CSeq Lazy-0.6, newseq-0.6a, newseq-0.6c), [SV-COMP 2015]
    2014.10.26  removed dead/commented-out/obsolete code
    2014.10.15  removed visit() and moved visit call-stack handling to module class (module.py)
    2014.03.14 (CSeq Lazy-0.4) further code refactory to match  module.Module  class interface
    2014.02.25 (CSeq Lazy-0.2)switched to module.Module base class for modules

Notes:
  - the input needs to be completely unfolded, needs inliner+unroller first.

To do:
  - replace the quick hacks in visit_FuncDef() with proper AST-based implementation
  - visit_FuncDef() visit the same AST multiple times - inefficient..
  - re-implement AST-based prototype cloning

"""
import re
import pycparserext.ext_c_parser, pycparser.c_ast, pycparserext.ext_c_generator
import core.module, core.parser, core.utils


class duplicator(core.module.Translator):
	__actualthreads = 0	   # the extra thread for main() is not counted at this stage
	__threadCallCnt = {}	  # number of pthread_create()s on the same function generated so far
	__threadsnamesmap = {}	# from thread copy to original thread (example: threadf_10 --> threadf)
	__threadindexes = {}	  # index of thread copies by name (statically determined)
	__threadindextoname = {}  # from integer thread indexes to function names (not indexed)


	def init(self):
		self.outputparam('threads')		   # no. of thread creations (statically determined)
		self.outputparam('threadnamesmap')	# map from thread copies to original threads
		self.outputparam('threadindexes')	 # map from thread copies (renamed id) to thread indexes
		self.outputparam('threadindextoname') # map from thread index to original thread/function name


	def loadfromstring(self, string, env):
		# Safety check for SVCOMP
		'''
		if len(string) > 2000000 and 'unwind-for' in env.paramvalues and env.paramvalues['unwind-for'] >= 16:
			raise core.module.ModuleError("sequentialized file is too big")
		'''

		super(self.__class__, self).loadfromstring(string, env)
		self.postprocess()

		env.threads = self.getactualthreads() #if env.threads == 0 else env.threads
		#print "threads: %s" % env.threads

		self.__threadindextoname[0] = 'main'

		self.setoutputparam('threads', env.threads)
		self.setoutputparam('threadnamesmap', self.__threadsnamesmap)
		self.setoutputparam('threadindexes', self.__threadindexes)
		self.setoutputparam('threadindextoname', self.__threadindextoname)


	def postprocess(self):
		#for t in self.Parser.threadName:
		#   print "thread %s times %s" % (t, self.Parser.threadCallCnt[t])

		# The thread functions prototypes of duplicated threads
		# need to be duplicated too.
		#
		for f in self.Parser.threadName:
			if f in self.Parser.funcDecl:
				oldPrototype = self.Parser.funcDecl[f] + ';'
				newPrototype = ''

				# TODO: this needs AST-based implemetation
				for i in range(0, self.Parser.threadCallCnt[f]):
					newPrototype += oldPrototype.replace(f+'(', f+'_'+str(i)+'(', 1)

				#print "replacing '%s' with '%s'\n\n\n\n" %( oldPrototype, newPrototype)
				self.output = self.output.replace(oldPrototype, newPrototype)


	def getactualthreads(self):
		return self.__actualthreads


	def visit_FuncCall(self, n):
		fref = self._parenthesize_unless_simple(n.name)
		args = ''

		#if fref == core.common.changeID['pthread_create']:
		if fref == 'pthread_create':
			self.__actualthreads += 1

			# Extract the function name (passed as 3rd argument)
			fName = self.visit(n.args.exprs[2])
			fName = fName[1:] if fName.startswith('&') else fName

			# Count how many times the same function is used to create a thread, and
			# append to the function name the corresponding index.
			if fName not in self.__threadCallCnt: self.__threadCallCnt[fName] = 0;
			else: self.__threadCallCnt[fName] += 1;

			fNameIndexed = fName +'_'+ str(self.__threadCallCnt[fName])

			# Append  _K  to the 3rd parameter in the call to pthread_create(),
			# where  K  is the number calculated previous steps
			args += self.visit(n.args.exprs[0]) + ', '
			args += self.visit(n.args.exprs[1]) + ', '
			args += fNameIndexed + ', '
			args += self.visit(n.args.exprs[3])

			#self.warn("new thread found: %s %s" % (fNameIndexed, self.__actualthreads))
			self.__threadindexes[fNameIndexed] = self.__actualthreads
			self.__threadindextoname[self.__actualthreads] = fName
		else:
			args = self.visit(n.args)

		return fref + '(' + args + ')'


	def visit_FuncDef(self, n):
		if n.decl.name == 'main': return super(self.__class__, self).visit_FuncDef(n)

		# No transformation for non-threads.
		cntthreads = self.Parser.threadCallCnt[n.decl.name]
		#self.log("visiting definition of function %s, number %s" % (n.decl.name,cntthreads))

		if cntthreads == 0:
			return super(self.__class__, self).visit_FuncDef(n)

		# Duplicate threads, but include the original function definition
		# in case it is also used otherwise (i.e. explicit calls or any other occurrences such as references).
		block = ''
		cntoveralloccurrences = self.Parser.funcIdCnt[n.decl.name]

		for i in range(0,cntthreads):
			# save the number of entries in self.lines so after the visit() we can revert them back
			oldlineslen = len(self.lines) 

			tmp = super(self.__class__, self).visit_FuncDef(n)
			tmp = tmp.replace(n.decl.name, n.decl.name+'_'+str(i), 1)   # TODO this needs proper implementation

			self.__threadsnamesmap[n.decl.name+'_'+str(i)] = n.decl.name # map the renamed function

			# revert back self.lines otherwise line mapping won't work properly when duplicating threads
			self.lines = self.lines[:oldlineslen] 

			block += tmp

		if cntoveralloccurrences > cntthreads:   # same function is used both to spawn threads and in explicit invocations
			self.warn("function %s used both to create threads and explicitly invoked" % (n.decl.name))
			block += super(self.__class__, self).visit_FuncDef(n)

		return block













