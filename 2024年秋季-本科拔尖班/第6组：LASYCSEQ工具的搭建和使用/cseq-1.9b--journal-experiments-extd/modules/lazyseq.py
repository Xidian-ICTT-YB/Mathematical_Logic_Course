""" CSeq Program Analysis Framework
    lazy sequentialisation: main module

Implements the lazy sequentialization schema
(see Inverso, Tomasco, Fischer, La Torre, Parlato, CAV'14)

Author:
	Omar Inverso

Changes:
	2021.04.21  slight changes to make Klee work again (just for journal experiments, this version is no longer maintained)
	2020.04.18  replaced | in the jump marco with a placeholder to be instrumented either to | or ||
    2020.03.28 (CSeq 2.0)
    2020.03.28  block-based symbol table lookup (e.g., isglobal(), etc.)
    2020.03.22  merged context-bounded scheduler [SV-COMP 2020] + [PPoPP 2020]
    2019.11.20 [SV-COMP 2020]
    2019.11.20  static storage class for locks
    2019.11.15  using __VERIFIER_xyz() primitives rather than __CSEQ_xyz()
    2019.11.15 (CSeq 1.9) pycparserext
    2019.11.15  no longer relying on mapped pthread_xyz identifiers
    2019.11.13  support for pycparser 2.19 (backward compatibility preserved)
    2018.11.25  output params for thread endlines and thread sizes (used to build a more detailed error trace)
    2018.11.22  fixed insertion of cs-points for labeled statements
    2018.11.22  insert context-switch point before any mutex operation
    2018.11.21 [SV-COMP 2019]
    2018.11.21  transformation of local variables into static and separation of init exprs (previously done in inliner module, see visit_Decl)
    2018.11.21  always insert the first context-switch point at the very beginning of a thread (and not after the local declarations)
    2018.11.03  merged with [SV-COMP 2016] to [SV-COMP 2018] (after removing a lot of clutter)
    2018.11.10  improved modelling of thread-specific data management (+key destructors)
    2018.11.10  sequentialised threads now always end with a call to __cs_exit() (instead than STOP_VOID or STOP_NONVOID)
    2018.11.03  renamed __currentThread as __CurrentFun (bnot every function is a thread)
    2018.11.03  no longer using Parser.funcReferenced to check whether a function might be referenced
    2018.11.03  fixed detection of return statements within threads
    2018.11.02  added support for thread-specific data management (getspecific, setspecific, keys, etc.)
    2016.11.30  handling of main()'s argc and argv parameters disabled as not implemented properly
    2016.11.22  fix problem with function pointer reference (smacker benchmarks)
    2016.09.21  fix small bug that causes the injection of GUARD in atomic function
    2016.08.12  support for preanalysis from framac to guess the number of bits for each variable
    2016.01.19  code review to make it more uniform with the cba version
    2015.10.19 (CSeq 1.3) for unfinished journal
    2015.10.19  fix bug of __CSEQ_atomic_begin (definitely have a context switch before this statement) (Truc)
    2015.07.18 (CSeq 1.0) [ASE 2015]
    2015.07.18  new --schedule parameter to set schedule restrictions (Omar)
    2015.07.15  changed visit of atomic function definitions (Truc,Omar)
    2015.07.10  no context switch between __CSEQ_atomic_begin() and __CSEQ_atomic_end()
    2015.06.30  major refactory (converted to stand-alone instrumentation, etc.)
    2015.04.23  __globalAccess()  was causing  if(cond)  blocks to disappear
    2015.02.22  __CSEQ_assume() without occurrences of shared vars produces no context switch points
    2015.01.12  back to [CAV 2014]-style constraints in the main driver
    2015.01.27  using macros rather than functions to model pthread_mutex_lock/unlock() avoids using ptrs and thus yields faster analysis
    2014.01.17  main driver: first thread execution context must have length > 0 (faster analysis)
    2014.12.24  linemap (overrides the one provided by core.module)
                bugfixes, code maintenance
    2014.12.09  further code refactory to match the new organisation of the CSeq framework
    2014.10.29 (CSeq 1.0beta) (newseq-0.6c) [SV-COMP 2015]
    2014.10.29  bitvector encoding for all control variables (pc, pc_cs, ...)
                new main driver where guessed jump lenghts are all at the top (this allows inserting p.o.r. constraints right after them)
    2014.10.26 (newseq-0.6a) removed dead/commented-out/obsolete code
    2014.10.15  removed visit() and moved visit call-stack handling to module class (module.py)
    2014.06.26 (CSeq Lazy-0.4) improved backend-specific instrumentation
    2014.06.26  added new backend Klee
    2014.03.14 (CSeq Lazy-0.3) further code refactory to match module.Module class interface
    2014.02.25 (CSeq Lazy-0.2) switched to module.Module base class for modules
    2014.01.19  fixed assert()s missing their stamps at the beginning

Notes:
  - double-check __cs_pc_cs bitwidth (bitvector encoding), shouldn't it be the same as __cs_pc? (maybe one more is needed to go beyond the last thread stms)
  - all functions should have been inlined, except the main(), all thread functions, all __CSEQ_atomic_ functions, and function __CSEQ_assert
  - all loops should have been unrolled
  - no two threads refers to the same thread function (use module duplicator.py)
  - in the simulated pthread_xyz(), the id of the main thread is 1 (not 0!), e.g.
    mutex lock and unlock operations use thread_index+1.
    Index 0 is for unitialised global variables (which may include global mutexes).....

To do:
  - urgent: review/rewrite visit_Decl() (also check if keepstaticarray!)
  - urgent: general code clean up
  - urgent: replace isPointer/isGlobal with AST-based functions, add parser support if necessary
  - get rid of _init_scalar() (see old ext. notes)
  - check the STOP() inserting mechanism
  - this schema assumes no mutex_lock() in main() - is this fine?

"""
import math, re
from time import gmtime, strftime
import pycparserext.ext_c_parser, pycparser.c_ast, pycparserext.ext_c_generator
import core.module, core.parser, core.utils


typemap = {}
typemap['pthread_barrier_t'] = 'cspthread_barrier_t'
typemap['pthread_cond_t'] = 'cspthread_cond_t'
typemap['pthread_mutex_t'] = 'cspthread_mutex_t'
typemap['pthread_t'] = 'cspthread_t'
typemap['pthread_key_t'] = 'cspthread_key_t'
typemap['pthread_mutexattr_t'] = 'cspthread_mutexattr_t'
typemap['pthread_condattr_t'] = 'cspthread_condattr_t'
typemap['pthread_barrierattr_t'] = 'cspthread_barrierattr_t'
 

class lazyseq(core.module.Translator):
	__lines = {}                     # # count of visible statements for each thread
	__threadName = ['main']          # name of threads, as they are found in pthread_create(s) - the threads all have different names
	__threadIndex = {}               # index of the thread = value of threadcount when the pthread_create to that thread was discovered
	__threadCount = 0                # pthread create()s found so far

	__labelLine = {}                 # statement number where labels are defined [function, label]
	__gotoLine = {}                  # statement number where goto to labels appear [function, label]
	__maxInCompound = 0              # max label within a compound
	__labelLength = 55               # for labels to have all the same length, adding padding when needed
	__startChar = 't'                # special char to distinguish between labeled and non-labelled lines

	__stmtCount = -1                 # thread statement counter (to build thread labels)

	__currentFun = ''                # name of the current thread (also used to build thread labels)
									 # or function (for functions not inlined)

	__firstThreadCreate = False      # set once the first thread creation is met
	__globalMemoryAccessed = False   # used to limit context-switch points (when global memory is not accessed, no need to insert them)

	__first = False
	_atomicsection = False           # no context-switch points between atomic_start() and atomic_end()

	_bitwidth = {}                   # custom bitwidth for specific int variables, e.g. ['main','var'] = 4

	__explicitround = []             # explicit schedules restrictions

	__visit_funcReference = False

	__preanalysis = {}
	__visiting_struct = False
	__struct_stack = []               # stack of struct name
	threadendlines  = {}

	staticlocks = ''   # declarations of static mutexes to be moved outside their threads as global variables

	thisblocknode = None              # AST node for the current block being visited


	def init(self):
		self.inputparam('rounds', 'round-robin schedules', 'r', '1', False)
		self.inputparam('contexts', 'execution contexts (replaces --rounds)', 'c', None, optional=True)
		self.inputparam('threads', 'max thread creations (0 = auto)', 't', '0', False)
		self.inputparam('schedule', 'schedule restriction (example: 1,2:+:3)', 's', default='', optional=True)
		self.inputparam('deadlock', 'check for deadlock', '', default=False, optional=True)
		self.inputparam('norobin', 'alternative scheduler', '', default=False, optional=True)
		self.inputparam('preanalysis', 'use preanalysis from abstract interpretation', 'u', default=None, optional=True)
		self.inputparam('nondet-condvar-wakeups', 'spurious conditional variables wakeups', '', default=False, optional=True)

		self.outputparam('bitwidth')
		self.outputparam('header')
		self.outputparam('threadsizes')    # no. of visible statements for each thread, used to build cex
		self.outputparam('threadendlines')

		# - - - -
		###self.inputparam('keepstaticarray', 'keep static array, do not change to pointer version', '', default=None, optional=True)

	def loadfromstring(self, string, env):
		rounds = int(self.getinputparam('rounds'))
		contexts = int(self.getinputparam('contexts')) if self.getinputparam('contexts') is not None else 0
		threads = int(self.getinputparam('threads'))
		schedule = self.getinputparam('schedule')
		deadlock = True if self.getinputparam('deadlock') else False
		#roundrobin = False if self.getinputparam('norobin') is not None else True
		norobin = True if self.getinputparam('norobin') is not None else False
		pedanticthreads = False if self.getinputparam('nondet-condvar-wakeups') is None else True

		# Schedule control.
		# TODO TODO TODO this only works with round-robin scheduler!
		if schedule is not None:
			while schedule.startswith(':'): schedule = schedule[1:]
			while schedule.endswith(':'): schedule = schedule[:-1]
			while schedule.find('::') != -1: schedule = schedule.replace('::',':')
			while schedule.find(',,') != -1: schedule = schedule.replace(',,',',')
			while schedule.startswith(','): schedule = schedule[1:]
			while schedule.endswith(','): schedule = schedule[:-1]

		if schedule is not None and schedule != '':
			for i in schedule.split(':'):
				self.__explicitround.append(i)

		for x in self.__explicitround:
			for y in x.split(','):
				if y != '+' and not y.isdigit():
					self.warn("invalid scheduling ignored")
					self.__explicitround = []
				elif y.isdigit() and int(y) > threads:
					self.warn("invalid scheduling ignored (thread %s does not exist)" % y)
					self.__explicitround = []

		if len(self.__explicitround) > rounds: # schedules > rounds: adjust rounds
			#self.warn('round bound increased to %s due to longer schedule' % len(schedule.split(':')))
			rounds = len(schedule.split(':'))
		elif len(self.__explicitround) < rounds: # schedules < rounds: add more unconstrained entries
			for i in range(len(self.__explicitround),rounds):
				self.__explicitround.append('+')

		self.__explicitround[0] += ',0'   # main thread must always be schedulable in the 1st round

		# Pre-analysis
		if self.getinputparam("preanalysis") is not None:
			self.__preanalysis = self.getinputparam("preanalysis")
			if env.debug:
				seqfile = core.utils.rreplace(env.inputfile, '/', '/_cs_', 1) if '/' in env.inputfile else '_cs_' + env.inputfile
				if env.outputfile is not None and env.outputfile != '':
					seqfile = env.outputfile
				logfile = seqfile + '.framac.log.extract'
				with open(logfile, "w") as logfile:
					logfile.write(str(self.__preanalysis))

		super(self.__class__, self).loadfromstring(string, env)

		# Add the new main().
		if norobin:       self.output += self.__schedulernorobin(rounds,threads)
		elif contexts==0: self.output += self.__scheduler(rounds,threads)
		else:             self.output += self.__schedulercba(contexts,threads)

		# Insert the thread sizes (i.e. number of visible statements).
		lines = ''

		i = maxsize = 0

		for t in self.__threadName:
			if i <= threads:
				if i>0: lines += ', '
				lines += str(self.__lines[t])
				maxsize = max(int(maxsize), int(self.__lines[t]))
				#print "CONFRONTO %s %s " % (int(maxsize), int(self.__lines[t]))
			i +=1

		ones = ''  # only used when deadlock check is enabled (see below)
		if i <= threads:
			if i>0: ones += ', '
			ones += '-1'
		i +=1

		# Generate the header.
		#
		# the first part is not parsable (contains macros)
		# so it is passed to next module as a header...
		header = core.utils.printFile('modules/lazyseqA.c')
		header = header.replace('<insert-maxthreads-here>',str(threads))
		header = header.replace('<insert-maxrounds-here>',str(contexts) if contexts > 1 else str(rounds))
		self.setoutputparam('header', header)

		# ..this is parsable and is added on top of the output code,
		# as next module is able to parse it.
		if not deadlock and not pedanticthreads:
			header = core.utils.printFile('modules/lazyseqB.c').replace('<insert-threadsizes-here>',lines)
		elif not deadlock and pedanticthreads:
			header = core.utils.printFile('modules/lazyseqB.nondet-condvar-wakeups.c').replace('<insert-threadsizes-here>',lines)
		else:
			header = core.utils.printFile('modules/lazyseqBdeadlock.c').replace('<insert-threadsizes-here>',lines)
			header = header.replace('<insert-all1-here>',  ones)

		self.insertheader(header)

		# Calculate exact bitwidth size for a few integer control variables of the seq. schema,
		# good in case the backend handles bitvectors.
		try:
			k = int(math.floor(math.log(maxsize,2)))+1
			self._bitwidth['','__cs_active_thread'] = 1
			self._bitwidth['','__cs_pc'] = k
			self._bitwidth['','__cs_pc_cs'] = k+1
			self._bitwidth['','__cs_thread_lines'] = k

			k = int(math.floor(math.log(threads+1,2)))+1
			self._bitwidth['','__cs_thread_index'] = k
			self._bitwidth['','__cs_last_thread'] = k
		except: pass

		# Fix gotos by inserting ASS_GOTO(..) blocks before each goto,
		# excluding gotos which destination is the line below.
		for (a,b) in self.__labelLine:
			if (a,b) in self.__gotoLine and (self.__labelLine[a,b] == self.__gotoLine[a,b]+1):
				self.output = self.output.replace('<%s,%s>' % (a,b), '')
			else:
				self.output = self.output.replace('<%s,%s>' % (a,b), 'ASS_GOTO(%s)' % self.__labelLine[a,b])

		self.setoutputparam('bitwidth', self._bitwidth)
		self.setoutputparam('threadsizes',self.__lines)
		self.setoutputparam('threadendlines',self.threadendlines)


	'''
	def visit_ArrayRef(self, n):
		arrref = self._parenthesize_unless_simple(n.name)
		subscript = self.visit(n.subscript)
		threadIndex = self.Parser.threadIndex[self.__currentFun] if self.__currentFun in self.Parser.threadIndex else 0

		if subscript == '__cs_thread_index' and self.__currentFun != '':
			subscript = '%s' % threadIndex

		s = arrref + '[' + subscript + ']'
		return s
	'''


	def visit_Compound(self,n):
		#print ("VISITING BLOCK : %s" % (self.Parser.blocknode[n]))
		s = self._make_indent() + '{\n'
		self.indent_level += 1

		oldblocknode = self.thisblocknode
		self.thisblocknode = n

		# Insert the labels at the beginning of each statement,
		# with a few exclusions to reduce context-switch points...
		#
		if n.block_items:
			for stmt in n.block_items:
				# Case 1: last statement in a thread (must correspond to last label)
				if type(stmt) == pycparser.c_ast.FuncCall and stmt.name.name == 'pthread_exit':
					self.__stmtCount += 1
					self.__maxInCompound = self.__stmtCount
					stamp = '__CSEQ_rawline("%s%s_%s: ");\n' % (self.__startChar, self.__currentFun, str(self.__stmtCount))
					code = self.visit(stmt)
					newStmt =  stamp + code + ';\n'
					s += newStmt
				# Case 2: labeled statements
				elif type(stmt) == pycparser.c_ast.Label:
					# --1-- Simulate a visit to the stmt block to see whether it makes any use of pointers or shared memory.
					#
					globalAccess = self.__globalAccess(stmt)
					newStmt = ''

					# --2-- Now rebuilds the stmt block again,
					#       this time using the proper formatting
					#      (now we know if the statement is accessing global memory,
					#       so to insert the stamp at the beginning when needed)
					#
					if self.__stmtCount == -1 and not self._atomicsection:   # first statement in a thread
						self.__stmtCount += 1
						self.__maxInCompound = self.__stmtCount
						threadIndex = self.Parser.threadIndex[self.__currentFun] if self.__currentFun in self.Parser.threadIndex else 0
						stamp = '__CSEQ_rawline("IF(%s,%s,%s%s_%s)");\n' % (threadIndex,str(self.__stmtCount), self.__startChar, self.__currentFun, str(self.__stmtCount+1))
						code = self.visit(stmt)
						newStmt = stamp + code + ';\n'
					elif (not self.__visit_funcReference and (
						(type(stmt.stmt) == pycparser.c_ast.FuncCall and stmt.stmt.name.name == '__VERIFIER_atomic_begin') or
						(not self._atomicsection and
							(globalAccess or
							(type(stmt.stmt) == pycparser.c_ast.FuncCall and stmt.stmt.name.name == 'pthread_create') or
							(type(stmt.stmt) == pycparser.c_ast.FuncCall and stmt.stmt.name.name == 'pthread_join') or
							(type(stmt.stmt) == pycparser.c_ast.FuncCall and stmt.stmt.name.name == 'pthread_mutex_lock') or
							(type(stmt.stmt) == pycparser.c_ast.FuncCall and stmt.stmt.name.name == 'pthread_mutex_unlock') or
							(type(stmt.stmt) == pycparser.c_ast.FuncCall and stmt.stmt.name.name == 'pthread_mutex_destroy') or
							(type(stmt.stmt) == pycparser.c_ast.FuncCall and stmt.stmt.name.name.startswith('__VERIFIER_atomic') and not stmt.name.name == '__VERIFIER_atomic_end') or
							(type(stmt.stmt) == pycparser.c_ast.FuncCall and stmt.stmt.name.name.startswith('__VERIFIER_assume')) or
							(type(stmt.stmt) == pycparser.c_ast.FuncCall and stmt.stmt.name.name == 'pthread_cond_wait_2')
							)
						)
						)):
						self.__stmtCount += 1
						self.__maxInCompound = self.__stmtCount
						threadIndex = self.Parser.threadIndex[self.__currentFun] if self.__currentFun in self.Parser.threadIndex else 0
						stamp = '__CSEQ_rawline("%s%s_%s: IF(%s,%s,%s%s_%s)");\n' % (self.__startChar, self.__currentFun, str(self.__stmtCount),threadIndex,str(self.__stmtCount), self.__startChar, self.__currentFun, str(self.__stmtCount+1))
						code = self.visit(stmt.stmt)
						newStmt = stamp + code + ';\n'
						#####self.log("     (A) STAMP")
					else:
						#####self.log("     (A) no STAMP")
						newStmt = self.visit(stmt.stmt) + ';\n'

					threadIndex = self.Parser.threadIndex[self.__currentFun] if self.__currentFun in self.Parser.threadIndex else 0
					guard = '__VERIFIER_assume( __cs_pc_cs[%s] >= %s );\n' % (threadIndex,self.__stmtCount+1) if not self._atomicsection else ''
					newStmt = self._make_indent()+ stmt.name + ': ' + guard + newStmt+ '\n'

					s += newStmt
				# Case 3: all the rest....
				#elif (type(stmt) not in (pycparser.c_ast.Compound, pycparser.c_ast.Goto, pycparser.c_ast.Decl)
				elif (type(stmt) not in (pycparser.c_ast.Compound, pycparser.c_ast.Goto)
					and not (self.__currentFun=='main' and self.__firstThreadCreate == False) or (self.__currentFun=='main' and self.__stmtCount == -1)):
					#####if type(stmt) == pycparser.c_ast.FuncCall: self.log("(B) ----> %s" % stmt.name.name)

					# --1-- Simulate a visit to the stmt block to see whether it makes any use of pointers or shared memory.
					#
					globalAccess = self.__globalAccess(stmt)
					newStmt = ''

					self.lines = []   # override core.module marking behaviour, otherwise  module.visit()  won't insert any marker

					# --2-- Now rebuilds the stmt block again,
					#       this time using the proper formatting
					#      (now we know if the statement is accessing global memory,
					#       so to insert the stamp at the beginning when needed)
					#
					if self.__stmtCount == -1 and not self._atomicsection:   # first statement in a thread
						self.__stmtCount += 1
						self.__maxInCompound = self.__stmtCount
						threadIndex = self.Parser.threadIndex[self.__currentFun] if self.__currentFun in self.Parser.threadIndex else 0
						stamp = '__CSEQ_rawline("IF(%s,%s,%s%s_%s)");\n' % (threadIndex,str(self.__stmtCount), self.__startChar, self.__currentFun, str(self.__stmtCount+1))
						code = self.visit(stmt)
						newStmt = stamp + code + ';\n'
					elif (not self.__visit_funcReference and (
						(type(stmt) == pycparser.c_ast.FuncCall and stmt.name.name == '__VERIFIER_atomic_begin') or
						(not self._atomicsection and
							(globalAccess or
							(type(stmt) == pycparser.c_ast.FuncCall and stmt.name.name == 'pthread_create') or
							(type(stmt) == pycparser.c_ast.FuncCall and stmt.name.name == 'pthread_join') or
							(type(stmt) == pycparser.c_ast.FuncCall and stmt.name.name == 'pthread_mutex_lock') or
							(type(stmt) == pycparser.c_ast.FuncCall and stmt.name.name == 'pthread_mutex_unlock') or
							(type(stmt) == pycparser.c_ast.FuncCall and stmt.name.name == 'pthread_mutex_destroy') or
							(type(stmt) == pycparser.c_ast.FuncCall and stmt.name.name.startswith('__VERIFIER_atomic') and not stmt.name.name == '__VERIFIER_atomic_end') or
							(type(stmt) == pycparser.c_ast.FuncCall and stmt.name.name.startswith('__VERIFIER_assume')) or
							(type(stmt) == pycparser.c_ast.FuncCall and stmt.name.name == 'pthread_cond_wait_2')
							)
						)
						)):
						self.__stmtCount += 1
						self.__maxInCompound = self.__stmtCount
						threadIndex = self.Parser.threadIndex[self.__currentFun] if self.__currentFun in self.Parser.threadIndex else 0
						stamp = '__CSEQ_rawline("%s%s_%s: IF(%s,%s,%s%s_%s)");\n' % (self.__startChar, self.__currentFun, str(self.__stmtCount),threadIndex,str(self.__stmtCount), self.__startChar, self.__currentFun, str(self.__stmtCount+1))
						code = self.visit(stmt)
						newStmt =  stamp + code + ';\n'
						#####self.log("     (B) STAMP")
					else:
						#####self.log("     (B) no STAMP")
						newStmt = self.visit(stmt) + ";\n"

					s += newStmt
				else:
					newStmt = self.visit(stmt) + ";\n"
					s += newStmt

		self.indent_level -= 1
		s += self._make_indent() + '}\n'

		self.thisblocknode = oldblocknode

		return s


	def visit_FuncDef(self, n):
		cntoveralloccurrences = self.Parser.funcIdCnt[n.decl.name]
		cntexplicitcalls = self.Parser.funcCallCnt[n.decl.name]
		cntthreads = self.Parser.threadCallCnt[n.decl.name]
		#print "---> blubluuu: %s   callcnlt:%s   idcnt:%s   thrcnt:%s" % (n.decl.name,cntexplicitcalls,cntoveralloccurrences,cntthreads) 

		# Remove functions that are never invoked (not even via call to pointer to function)
		if cntoveralloccurrences==cntexplicitcalls==cntthreads==0 and n.decl.name != 'main':
			self.debug("removing unused definition of function %s" % n.decl.name)
			return ''

		# No function sequentialisation
		if (n.decl.name.startswith('__VERIFIER_atomic_') or
			n.decl.name == '__VERIFIER_assert' or
			###n.decl.name in self.Parser.funcReferenced ):
			cntoveralloccurrences > cntthreads): # <--- e.g. functions called through pointers are not inlined yet

			self.__currentFun = n.decl.name
			self.__visit_funcReference = True
			oldatomic = self._atomicsection
			self._atomicsection = True
			decl = self.visit(n.decl)
			body = self.visit(n.body)
			self._atomicsection = oldatomic
			self.__visit_funcReference = False
			self.__currentFun = ''  # don't need a stack as FuncDef cannot nest
			return decl + '\n' + body + '\n'

		#print "---> function definition no skip"
		self.__first = False
		self.__currentFun = n.decl.name
		self.__firstThreadCreate = False

		decl = self.visit(n.decl)
		self.indent_level = 0
		body = self.visit(n.body)

		f = ''

		self.__lines[self.__currentFun] = self.__stmtCount

		#
		if n.param_decls:
			knrdecls = ';\n'.join(self.visit(p) for p in n.param_decls)
			self.__stmtCount = -1
			f = decl + '\n' + knrdecls + ';\n'
		else:
			self.__stmtCount = -1
			f = decl + '\n'

		# Remove arguments (if any) for main() and transform them into local variables in main_thread.
		# TODO re-implement seriously.
		if self.__currentFun == 'main':
			f = '%s main_thread(void)\n' % self.Parser.funcBlockOut[self.__currentFun]
			mainargs = self.Parser.funcBlockIn['main']
			args = ''

			if mainargs.find('void') != -1 or mainargs == '':
				mainargs = ''
			else:
				# Change *argv[] and **argv[] --> **argv
				mainargs = re.sub(r'\*(.*)\[\]', r'** \1', mainargs)
				mainargs = re.sub(r'(.*)\[\]\[\]', r'** \1', mainargs)

				# split arguments
				mainargs = mainargs.split(',')

				if len(mainargs) != 2:
					self.warn('ignoring argument passing (%s) to main function' % mainargs)

				# args = 'static ' + mainargs[0] + '= %s; ' % self.__argc
				# args = 'static ' + mainargs[0] + '; '   # Disable this for SVCOMP
				args = mainargs[0] + '; '
				# argv = self.__argv.split(' ')
				# argv = '{' + ','.join(['\"%s\"' % v for v in argv]) + '}'
				# args += 'static ' + mainargs[1] + '= %s;' % argv
				# args += 'static ' + mainargs[1] + ';'     # Disable this for SVCOMP
				args += mainargs[1] + ';'

			body = '{' + args + body[body.find('{') + 1:]

		f += body + '\n'

		endline = self._mapbacklineno(self.currentinputlineno)[0]
		self.threadendlines[self.__currentFun] = endline

		self.__currentFun = ''

		#
		staticlocksdecl = self.staticlocks
		self.staticlocks = ''

		return staticlocksdecl + f + '\n\n'


	def visit_If(self, n):
		ifStart = self.__maxInCompound   # label where the if stmt begins

		s = 'if ('

		if n.cond:
			condition = self.visit(n.cond)
			s += condition

		s += ')\n'
		s += self._generate_stmt(n.iftrue, add_indent=True)

		ifEnd = self.__maxInCompound   # label for the last stmt in the if block:  if () { block; }
		nextLabelID = ifEnd+1

		if n.iffalse:
			elseBlock = self._generate_stmt(n.iffalse, add_indent=True)

			elseEnd = self.__maxInCompound   # label for the last stmt in the if_false block if () {...} else { block; }

			if ifStart < ifEnd:
				threadIndex = self.Parser.threadIndex[self.__currentFun] if self.__currentFun in self.Parser.threadIndex else 0
				#elseHeader = 'GUARD(%s,%s)' % (threadIndex, str(ifEnd+1))
				if not self.__visit_funcReference:
					elseHeader = '__VERIFIER_assume( __cs_pc_cs[%s] >= %s );' % (threadIndex, str(ifEnd+1))
			else:
				elseHeader = ''

			nextLabelID = elseEnd+1
			s += self._make_indent() + 'else\n'

			elseBlock = elseBlock.replace('{', '{ '+elseHeader, 1)
			s += elseBlock

		header = ''

		if ifStart+1 < nextLabelID:
			threadIndex = self.Parser.threadIndex[self.__currentFun] if self.__currentFun in self.Parser.threadIndex else 0
			#footer = 'GUARD(%s,%s)' % (threadIndex, nextLabelID)
			if not self.__visit_funcReference:
				footer = '__VERIFIER_assume( __cs_pc_cs[%s] >= %s );' % (threadIndex, nextLabelID)
		else:
			footer = ''

		'''
		if n.iffalse:
			header = 'ASS_ELSE(%s, %s, %s)' % (condition, ifEnd+1, elseEnd+1) + '\n' + self._make_indent()
		else:
			if ifEnd > ifStart:
				header = 'ASS_THEN(%s, %s)' % (condition, ifEnd+1) + '\n' + self._make_indent()
			else: header = ''
		'''

		return header + s + self._make_indent() + footer


	def visit_Return(self, n):
		# ??? Note that the same function may at the same time
		# be passed as an argument to pthread_create() to spawn a thread, and
		# explicitly invoked.  Therefore, just checking whether a function
		# belongs to the set of threads is not sufficient here.
		#
		'''
		if (self.__currentFun != '__CSEQ_assert' and
			self.__currentFun not in self.Parser.funcReferenced and
			not self._atomicsection):
		'''
		if (self.__currentFun in self.Parser.threadName and
			self.__currentFun not in self.Parser.funcName):
			self.error("error: %s: return statement in thread '%s'.\n" % (self.name(), self.__currentFun))

		s = 'return'
		if n.expr: s += ' ' + self.visit(n.expr)
		return s + ';'


	def visit_Label(self, n):
		self.__labelLine[self.__currentFun, n.name] = self.__stmtCount
		return n.name + ':\n' + self._generate_stmt(n.stmt)


	def visit_Goto(self, n):
		self.__gotoLine[self.__currentFun, n.name] = self.__stmtCount
		extra = '<%s,%s>\n' % (self.__currentFun, n.name) + self._make_indent()
		extra = ''
		return extra + 'goto ' + n.name + ';'


	def visit_ID(self, n):
		# If this ID corresponds either to a global variable,
		# or to a pointer...
		#
		if ((self.__isGlobal(self.__currentFun, n.name) or self.__isPointer(self.__currentFun, n.name)) and not
		#if ((self.Parser.isglobal(self.blockid,n.name) or self.Parser.ispointer(self.blockid,n.name)) and not
			n.name.startswith('__cs_thread_local_')):
			#print "variable %s in %s is global\n" % (n.name, self.__currentFun)
			self.__globalMemoryAccessed = True

		return n.name


	def visit_FuncCall(self, n):
		fref = self._parenthesize_unless_simple(n.name)
		args = self.visit(n.args)

		if fref == '__VERIFIER_atomic_begin':
			if not self.__visit_funcReference: self._atomicsection = True
			return ''
		elif fref == '__VERIFIER_atomic_end':
			if not self.__visit_funcReference: self._atomicsection = False
			return ''
		elif fref.startswith('__VERIFIER_atomic_'):
			self.__globalMemoryAccessed = True   # TODO why? shouldn't be False instead? needs checking TODO
		elif fref == 'pthread_cond_wait':
			self.error('pthread_cond_wait in input code (use conditional wait converter module first)')


		# When a thread is created, extract its function name
		# based on the 3rd parameter in the pthread_create() call:
		#
		# pthread_create(&id, NULL, f, &arg);
		#                          ^^^
		#
		if fref == 'pthread_create': # TODO re-write AST-based (see other modules)
			fName = args[:args.rfind(',')]
			fName = fName[fName.rfind(',')+2:]
			fName = fName.replace('&', '')

			##print "checking fName = %s\n\n" % fName

			if fName not in self.__threadName:
				self.__threadName.append(fName)
				self.__threadCount = self.__threadCount + 1
				self.__threadIndex[fName] = self.__threadCount
				args = args + ', %s' % (self.__threadCount)
			else:
				# Reuse the old thread indexes when visiting multiple times
				args = args + ', %s' % (self.__threadIndex[fName])

			self.__firstThreadCreate = True

		# Avoid using pointers to handle mutexes
		# by changing the function calls,
		# there are two cases:
		#
		#    pthread_mutex_lock(&l)   ->  __cs_mutex_lock(l)
		#    pthread_mutex_lock(ptr)  ->  __cs_mutex_lock(*ptr)
		#
		# TODO:
		#    this needs proper implementation,
		#    one should check that the argument is not referenced
		#    elsewhere (otherwise this optimisation will not work)
		#
		'''
		if (fref == 'pthread_mutex_lock') or (fref == 'pthread_mutex_unlock'):
			if args[0] == '&': args = args[1:]
			else: args = '*'+args
		'''

		# Optimization for removing __cs_thread_index variable from global scope
		'''
		if ((fref == 'pthread_mutex_lock') or (fref == 'pthread_mutex_unlock') or
				fref.startswith('pthread_cond_wait_')):
			threadIndex = self.Parser.threadIndex[self.__currentFun] if self.__currentFun in self.Parser.threadIndex else 0
			return fref + '(' + args + ', %s)' % threadIndex
		'''

		return fref + '(' + args + ')'


	def __scheduler(self,ROUNDS,THREADS):
		# Explicit non-deterministic initialisation for Klee
		backend = self.getinputparam('backend').lower() if self.getinputparam('backend') else ''
		kleeinit = '= __VERIFIER_nondet_uint()' if backend and backend == 'klee' else ''

		# the new main() is created according to the following sort of scheduling:
		#
		# main_thread    t1 t2    t1 t2   t1 t2    t1 t2     t1 t2    t1 t2      t1 t2    t1 t2    main_thread
		#
		main = ''
		main += "int main(void) {\n"

		''' Part I:
			Pre-guessed jump lenghts have a size in bits depending on the size of the thread.
		'''
		for r in range(0,ROUNDS):
			for t in range(0,THREADS+1):
				if str(t) in self.__explicitround[r].split(',') or '+' in self.__explicitround[r]:
					#print("----- t  %s" % t)
					#print("----- threadname  %s" % self.__threadName[t])
					#print("----- threadnames %s " % self.__threadName)
					#print("----- lines       %s" % self.__lines)
					threadsize = self.__lines[self.__threadName[t]]
					k = int(math.floor(math.log(threadsize,2)))+1
					self._bitwidth['main','__cs_tmp_t%s_r%s' % (t,r)] = k

		k = int(math.floor(math.log(self.__lines['main'],2)))+1
		self._bitwidth['main','__cs_tmp_t%s_r%s' % (0,ROUNDS)] = k

		''' Part II:
			Schedule pruning constraints.
		'''
		'''
		main += '\n'

		schedulesPruned = []  # remeember which rounds have been pruned

		for t in range(0,self.__threadbound+1):
			#print "thread %s,  name %s,   maxrepr %s,  threadsize %s" % (t,self.__threadName[t],maxrepresentable, threadsize)
			threadsize = self.__lines[self.__threadName[t]]
			maxrepresentable =  2**int((math.floor(math.log(threadsize,2)))+1) - 1

			sumall = ''

			for r in range(0, ROUNDS):
				sumall += '__cs_tmp_t%s_r%s%s' % (t,r, ' + ' if r<ROUNDS-1 else '')

			if t == 0:
				sumall += ' + __cs_tmp_t0_r%s' % (ROUNDS)

			######if (maxrepresentable > threadsize+1) and int((math.floor(math.log(threadsize,2)))+1)+1 > 4:
			if (maxrepresentable > threadsize+1) and int((math.floor(math.log(threadsize,2)))+1)+1 > 4:
				schedulesPruned.append(True)
				if t == 0:
					wow =   int(math.ceil(math.log((maxrepresentable*(ROUNDS+1)),2)))
				else:
					wow =   int(math.ceil(math.log((maxrepresentable*ROUNDS),2)))
				##wow =   int(math.ceil(math.log((maxrepresentable*ROUNDS),2)))

				#main += "          unsigned __CSEQ_bitvector[%s] top%s = %s;\n" % (wow, t, threadsize)
				main += "          unsigned int __cs_top%s = %s;\n" % (t, threadsize)
				self._bitwidth['main','__cs_top%s' % t] = wow
				#main += "          unsigned __CSEQ_bitvector[%s] sum%s = %s;\n" % (wow, t, sumall)
				#main += "          __CSEQ_assume(sum%s <= top%s);\n" % (t,t)
			else:
				schedulesPruned.append(False)
		'''


		''' Part III:
		'''
		# 1st round (round 0)
		#
		round=0

		i=0
		t='main'

		main +="__CSEQ_rawline(\"/* round  %s */\");\n" % round
		main +="__CSEQ_rawline(\"    /* main */\");\n"
		main +="          __cs_thread_index = %s;\n" % i
		main +="          unsigned int __cs_tmp_t%s_r%s%s;\n" % (i,round,kleeinit)
		main +="          __cs_pc_cs[%s] = __cs_tmp_t%s_r%s;\n" % (i,i,round)
		main +="          __VERIFIER_assume(__cs_pc_cs[%s] > 0);\n" % i   # do not remove, faster analysis
		main +="          __VERIFIER_assume(__cs_pc_cs[%s] <= %s);\n" % (i,self.__lines[t])
		main +="          main_thread();\n"
		main +="          __cs_pc[%s] = __cs_pc_cs[%s];\n" % (i,i)
		main +="\n"

		i = 1
		for t in self.__threadName:
			if t == 'main': continue
			if i <= THREADS:
				if str(i) in self.__explicitround[0].split(',') or '+' in self.__explicitround[0]:
					main +="__CSEQ_rawline(\"    /* %s */\");\n" % t
					main +="          unsigned int __cs_tmp_t%s_r%s%s;\n" % (i,round,kleeinit)
					main +="          if (__cs_active_thread[%s]) {\n" % i
					main +="             __cs_thread_index = %s;\n" % i
					###main +="             __cs_pc_cs[%s] = __cs_pc[%s] + __cs_tmp_t%s_r%s;\n" % (i,i,i,0)
					main +="             __cs_pc_cs[%s] = __cs_tmp_t%s_r%s;\n" % (i,i,round)
					main +="             __VERIFIER_assume(__cs_pc_cs[%s] <= %s);\n" % (i,self.__lines[t])
					main +="             %s(%s);\n" % (t, '__cs_threadargs[%s]') % (i)
					main +="             __cs_pc[%s] = __cs_pc_cs[%s];\n" % (i,i)
					main +="          }\n\n"
				i += 1

		# remaining rounds
		#
		for round in range(1,ROUNDS):
			i=0
			t='main'
			main +="__CSEQ_rawline(\"/* round  %s */\");\n" % round
			main +="__CSEQ_rawline(\"    /* main */\");\n"

			if str(i) in self.__explicitround[round].split(',') or '+' in self.__explicitround[round]:
				main +="          unsigned int __cs_tmp_t%s_r%s%s;\n" % (i,round,kleeinit)
				main +="          if (__cs_active_thread[%s]) {\n" % i
				main +="             __cs_thread_index = %s;\n" % i
				###main +="              __cs_pc_cs[%s] = __cs_pc[%s] + __cs_tmp_t%s_r%s;\n" % (i,i,i,round)
				main +="              __cs_pc_cs[%s] = __cs_tmp_t%s_r%s;\n" % (i,i,round)
				main +="              __VERIFIER_assume(__cs_pc_cs[%s] >= __cs_pc[%s]);\n" % (i,i)
				main +="              __VERIFIER_assume(__cs_pc_cs[%s] <= %s);\n" % (i,self.__lines[t])
				main +="              main_thread();\n"
				main +="              __cs_pc[%s] = __cs_pc_cs[%s];\n" % (i,i)
				main +="          }\n\n"

			i = 1
			for t in self.__threadName:
				if t == 'main': continue
				if i <= THREADS:
					if str(i) in self.__explicitround[round].split(',') or '+' in self.__explicitround[round]:
						main +="__CSEQ_rawline(\"    /* %s */\");\n" % t
						main +="          unsigned int __cs_tmp_t%s_r%s%s;\n" % (i,round,kleeinit)
						main +="          if (__cs_active_thread[%s]) {\n" % i
						main +="             __cs_thread_index = %s;\n" % i
						###main +="             __cs_pc_cs[%s] = __cs_pc[%s] + __cs_tmp_t%s_r%s;\n" % (i,i,i,round)
						main +="             __cs_pc_cs[%s] = __cs_tmp_t%s_r%s;\n" % (i,i,round)
						main +="             __VERIFIER_assume(__cs_pc_cs[%s] >= __cs_pc[%s]);\n" % (i,i)
						main +="             __VERIFIER_assume(__cs_pc_cs[%s] <= %s);\n" % (i, self.__lines[t])
						main +="             %s(%s);\n" % (t, '__cs_threadargs[%s]') % (i)
						main +="             __cs_pc[%s] = __cs_pc_cs[%s];\n" % (i,i)
						main +="          }\n\n"
					i += 1

		# Last call to main()
		#
		main += "          unsigned int __cs_tmp_t0_r%s%s;\n" % (ROUNDS,kleeinit)
		main +="          if (__cs_active_thread[0]) {\n"
		main +="             __cs_thread_index = 0;\n"
		###main +="             __cs_pc_cs[0] = __cs_pc[0] + __cs_tmp_t0_r%s;\n" % (ROUNDS)
		main +="             __cs_pc_cs[0] = __cs_tmp_t0_r%s;\n" % (ROUNDS)
		main +="             __VERIFIER_assume(__cs_pc_cs[0] >= __cs_pc[0]);\n"
		main +="             __VERIFIER_assume(__cs_pc_cs[0] <= %s);\n" % (self.__lines['main'])
		main +="             main_thread();\n"
		main +="          }\n\n"
		main += "   return 0;\n"
		main += "}\n\n"

		return main


	def __schedulernorobin(self,ROUNDS,THREADS):
		main = ''
		main += "int main(void) {\n"

		''' Part I:
			Pre-guessed jump lengths have a size in bits depending on the size of the thread.
		'''
		for r in range(0, ROUNDS):
			for t in range(0,THREADS+1):
				threadsize = self.__lines[self.__threadName[t]]
				k = int(math.floor(math.log(threadsize,2)))+1
				self._bitwidth['main','__cs_tmp_t%s_r%s' % (t,r)] = k

		''' First round (round 0)
		'''
		round=0

		i=0
		t='main'

		# Main thread
		main +="__CSEQ_rawline(\"/* round  %s */\");\n" % round
		main +="__CSEQ_rawline(\"    /* main */\");\n"
		main +="          __cs_thread_index = %s;\n" % i
		main +="          unsigned int __cs_tmp_t0_r0;\n" 
		main +="          __VERIFIER_assume(__cs_tmp_t0_r0 > 0);\n"
		main +="          __cs_pc_cs[0] = __cs_tmp_t0_r0;\n"
		main +="          __VERIFIER_assume(__cs_pc_cs[0] <= %s);\n" % (self.__lines[t])
		main +="          main_thread();\n"
		main +="          __cs_last_thread = 0;\n"
		main +="          __cs_pc[0] = __cs_pc_cs[0];\n"
		main +="\n"

		i = 1
		for t in self.__threadName:
			if t == 'main': continue
			if i <= THREADS:
				main +="__CSEQ_rawline(\"    /* %s */\");\n" % t
				main +="         unsigned int __cs_tmp_t%s_r0;\n" % (i)
				main +="         unsigned int __cs_run_t%s_r0 = (__cs_tmp_t%s_r0 && (__cs_active_thread[%s] == 1));\n" % (i, i, i)
				self._bitwidth['main','__cs_run_t%s_r0' % (i)] = 1
				main +="         if (__cs_run_t%s_r0) {\n" % (i)
				main +="             __cs_thread_index = %s;\n" % i
				main +="             __cs_pc_cs[%s] = __cs_tmp_t%s_r0;\n" % (i, i)
				main +="             __VERIFIER_assume(__cs_pc_cs[%s] <= %s);\n" % (i, self.__lines[t])
				main +="             %s(__cs_threadargs[%s]);\n" % (t, i)
				main +="             __cs_last_thread = %s;\n" % (i)
				main +="             __cs_pc[%s] = __cs_pc_cs[%s];\n" % (i, i)
				main +="         }\n\n"
				i += 1

		# remaining rounds
		#
		for round in range(1, ROUNDS):
			i=0
			t='main'
			main +="__CSEQ_rawline(\"/* round  %s */\");\n" % round
			main +="__CSEQ_rawline(\"    /* main */\");\n"
			main +="          __VERIFIER_assume(__cs_last_thread != 0);\n"
			main +="          unsigned int __cs_tmp_t0_r%s;\n" % (round)
			main +="          unsigned int __cs_run_t0_r%s = (__cs_tmp_t0_r%s && (__cs_active_thread[0] == 1));\n" % (round, round)
			self._bitwidth['main','__cs_run_t0_r%s' % (round)] = 1
			main +="          if (__cs_run_t0_r%s) {\n" % (round)
			main +="             __cs_thread_index = %s;\n" % i
			main +="             __cs_pc_cs[0] = __cs_pc[0] + __cs_tmp_t0_r%s;\n" % (round)
			main +="             __VERIFIER_assume(__cs_pc_cs[0] >= __cs_pc[0]);\n"
			main +="             __VERIFIER_assume(__cs_pc_cs[0] <= %s);\n" % (self.__lines['main'])
			main +="             main_thread();\n"
			main +="             __cs_last_thread = 0;\n"
			main +="             __cs_pc[0] = __cs_pc_cs[0];\n"
			main +="          }\n\n"
			main +="\n"

			i = 1
			for t in self.__threadName:
				if t == 'main': continue
				if i <= THREADS:
					main +="__CSEQ_rawline(\"    /* %s */\");\n" % t
					main +="         __VERIFIER_assume(__cs_last_thread != %s);\n" % (i)
					main +="         unsigned int __cs_tmp_t%s_r%s;\n" % (i, round)
					main +="         unsigned int __cs_run_t%s_r%s = (__cs_tmp_t%s_r%s && (__cs_active_thread[%s] == 1));\n" % (i, round, i, round, i)
					self._bitwidth['main','__cs_run_t%s_r%s' % (i, round)] = 1
					main +="         if (__cs_run_t%s_r%s) {\n" % (i, round)
					main +="             __cs_thread_index = %s;\n" % i
					main +="             __cs_pc_cs[%s] = __cs_pc[%s] + __cs_tmp_t%s_r%s;\n" % (i, i, i, round)
					main +="             __VERIFIER_assume(__cs_pc_cs[%s] >= __cs_pc[%s]);\n" % (i, i)
					main +="             __VERIFIER_assume(__cs_pc_cs[%s] <= %s);\n" % (i, self.__lines[t])
					main +="             %s(__cs_threadargs[%s]);\n" % (t, i)
					main +="             __cs_last_thread = %s;\n" % (i)
					main +="             __cs_pc[%s] = __cs_pc_cs[%s];\n" % (i, i)
					main +="         }\n\n"
					i += 1

		# Last call to main()
		#
		k = int(math.floor(math.log(self.__lines['main'],2)))+1
		main += "          unsigned int __cs_tmp_t0_r%s;\n" % (ROUNDS)
		self._bitwidth['main','__cs_tmp_t0_r%s' % (ROUNDS)] = k
		main +="           if (__cs_active_thread[0] == 1) {\n"
		main +="             __cs_thread_index = %s;\n" % 0
		main +="             __cs_pc_cs[0] = __cs_pc[0] + __cs_tmp_t0_r%s;\n" % (ROUNDS)
		main +="             __VERIFIER_assume(__cs_pc_cs[0] >= __cs_pc[0]);\n"
		main +="             __VERIFIER_assume(__cs_pc_cs[0] <= %s);\n" % (self.__lines['main'])
		main +="             main_thread();\n"
		main +="           }\n\n"
		main += "    return 0;\n"
		main += "}\n\n"

		return main


	def __getmaxthreadsize(self,threads):
 		i = maxsize = 0

		for t in self.__threadName:
			if i <= threads:
				if i>0: lines += ', ' 
				maxsize = max(int(maxsize), int(self.__lines[t]))

		return maxsize


	def __schedulercba(self,CONTEXTS,THREADS):
		round = 0

		main = ''
		main += "int main(void) {\n"
		main += '\n'

		main += '   unsigned int __cs_tid[%s];\n' % (CONTEXTS)
		self._bitwidth['main','__cs_tid'] = int(math.ceil(math.log(float(THREADS+1),2.0)))

		main += '   unsigned int __cs_cs[%s];\n' % (CONTEXTS)
		#self._bitwidth['main','__cs_cs'] = int(math.ceil(math.log(float(CONTEXTS),2.0)))
		self._bitwidth['main','__cs_cs'] =int(math.ceil(math.log(float(self.__getmaxthreadsize(THREADS)),2.0)))


		# variant I: tid multiplexer (to be used instead of __cs_tid)
		'''
		main += '   unsigned int prova[%s][%s];\n' % (CONTEXTS,threads+1)
		self._bitwidth['main','prova'] = 1

		boh = ''
		for u in range(0,threads+1):
			truefalse = 1 if u==0 else 0
			boh += 'prova[0][%s] == %s;' % (u, truefalse)
		main +=   '%s;\n' % boh
		'''

		#main += '   int tid;\n'
		main += '   int k;\n'
		main += '   __cs_tid[0] = 0;\n'

		####main += '     unsigned int guess[%s][%s] = {};' %(CONTEXTS,threads+1)
		####self._bitwidth['main','guess'] =int(math.ceil(math.log(float(self.__getmaxthreadsize(THREADS)),2.0)))


		for k in range (0,CONTEXTS):
			'''
			for t in range(0,threads+1):
				name = '__cs_out_%s_%s' % (k,t)
				main += '         unsigned int %s;' % (name)
				self._bitwidth['main', name] =int(math.ceil(math.log(float(self.__lines[self.__threadName[t]]),2.0)))
				#main += '         guess[%s][%s] = %s;' % (k,t,name)
			'''


		for k in range (0,CONTEXTS):
			main +="__CSEQ_rawline(\"/* context %s */\");\n" % k
			main += '      k = %s;\n' % k

			if k==0:
				t=0
				#name = '__cs_out_%s_%s' % (k,t)
				#main += '         __VERIFIER_assume(__cs_out_%s_%s >= __cs_pc_cs[%s]);\n' %(k,t,t)
				#main += '         __VERIFIER_assume(__cs_out_%s_%s <= __cs_thread_lines[%s]);\n' %(k,t,t)
				#main += '         __cs_pc_cs[%s] = __cs_out_%s_%s;\n' %(t,k,t)

				main += '         __VERIFIER_assume(__cs_cs[%s] >= __cs_pc_cs[%s]);\n' %(k,t)
				main += '         __VERIFIER_assume(__cs_cs[%s] <= __cs_thread_lines[%s]);\n' %(k,t)
				main += '         __cs_pc_cs[%s] = __cs_cs[%s];\n' %(t,k)

				main += '         %s(%s);\n' %('main_thread' if t==0 else 't%s_0'%t, '' if t==0 else '0')
				main += '         __cs_pc[%s] = __cs_pc_cs[%s];\n' %(t,t)

			else:
				for t in range(0,THREADS+1):
					# variant I: tid multiplexer (to be used instead of __cs_tid)
					'''
					tidcheck = ''
					for u in range(0,threads+1):
						conjunct = '' if u==0 else '& '
						truefalse = '' if u==t else '!'
						tidcheck += '%s %sprova[k][%s] ' % (conjunct,truefalse,u)
					'''
					tidcheck = '__cs_tid[%s] == %s' %(k,t)

					#name = '__cs_out_%s_%s' % (k,t)

					main += '      if (%s) {\n' %(tidcheck)
					#main += '         tid = %s;\n' %t
					main += '         __VERIFIER_assume(__cs_active_thread[%s]);' %(t)

					#main += '         __VERIFIER_assume(__cs_out_%s_%s >= __cs_pc_cs[%s]);\n' %(k,t,t)
					#main += '         __VERIFIER_assume(__cs_out_%s_%s <= __cs_thread_lines[%s]);\n' %(k,t,t)
					#main += '         __cs_pc_cs[%s] = __cs_out_%s_%s;\n' %(t,k,t)

					main += '         __VERIFIER_assume(__cs_cs[%s] >= __cs_pc_cs[%s]);\n' %(k,t)
					main += '         __VERIFIER_assume(__cs_cs[%s] <= __cs_thread_lines[%s]);\n' %(k,t)
					main += '         __cs_pc_cs[%s] = __cs_cs[%s];\n' %(t,k)

					main += '         %s(%s);\n' %('main_thread' if t==0 else self.__threadName[t], '' if t==0 else '__cs_threadargs[%s]'%t)
					main += '         __cs_pc[%s] = __cs_pc_cs[%s];\n' %(t,t)
					###main += '      } %s\n' % ('else' if t<threads else 'else assume(0);')
					main += '      } %s\n' % ('' if t<THREADS else '')

		main += "}\n\n"

		return main


	# Checks whether variable  v  from function  f  is a pointer.
	#
	def __isPointer(self, f, v):
		if v in self.Parser.varNames[f] and self.Parser.varType[f,v].endswith('*'): return True
		elif v in self.Parser.varNames[''] and self.Parser.varType['',v].endswith('*'): return True
		else: return False


	# Checks whether variable  v  from function  f  is global.
	#
	def __isGlobal(self, f, v):
		if (v in self.Parser.varNames[''] and v not in self.Parser.varNames[f]): return True
		else: return False


	# Check whether the given AST node:
	# accesses global memory, or
	# uses a pointer or references (*), or 
	# uses dereferencing (&).
	#
	# TODO: this overapproximation is very rough,
	#      (variable dependency, pointer analysis etc,
	#       could be useful for refinement)
	#
	def __globalAccess(self, stmt):
		if self._atomicsection: return False  # if between atomic_begin() and atomic_end() calls no context switchs needed..

		oldStmtCount = self.__stmtCount             # backup counters
		oldMaxInCompound = self.__maxInCompound
		oldGlobalMemoryAccessed = self.__globalMemoryAccessed

		globalAccess = False
		self.__globalMemoryAccessed = False

		if type(stmt) not in (pycparser.c_ast.If, ):
			tmp = self._generate_stmt(stmt)
		else:
			tmp = self._generate_stmt(stmt.cond)

		globalAccess = self.__globalMemoryAccessed

		self.__stmtCount = oldStmtCount             # restore counters
		self.__maxInCompound = oldMaxInCompound
		self.__globalMemoryAccessed = oldGlobalMemoryAccessed

		return globalAccess






















	# - - - - 
	#
	#           Initialisation of local variable,
	#           once they are transformed into static.
	#
	# - - - - 
	__parsingStruct = False
	keepstaticarray = None


	@staticmethod
	def _initVar(varT, varName, varTypeUnExpanded):
		#print ("querying vartype:>%s< varnme>%s< unexp>%s<" %(varT, varName, varTypeUnExpanded))
		s = ''
		if varT == 'int':
			s = '%s = __VERIFIER_nondet_int()' % varName
		elif varT == 'unsigned int':
			s = '%s = __VERIFIER_nondet_uint()' % varName
		elif varT == '_Bool':
			s = '%s = __VERIFIER_nondet_bool()' % varName
		elif varT == 'char':
			s = '%s = __VERIFIER_nondet_char()' % varName
		elif varT == 'unsigned char':
			s = '%s = __VERIFIER_nondet_uchar()' % varName
		elif varT == 'cspthread_t':
			s = ''
		elif varT == 'cspthread_mutex_t':
			s = ''
		elif varT == 'cspthread_cond_t':
			s = ''
		elif varT == 'cspthread_barrier_t':
			s = ''
		elif varT == 'pthread_attr_t':   # no cspthread_att_t yet
			s = ''
		else:
			#print ("querying vartype:%s varnme%s unexp%s" %(varT, varName, varTypeUnExpanded))
			if varTypeUnExpanded in typemap: varTypeUnExpanded = typemap[varTypeUnExpanded]
			s = '__cs_init_scalar(&%s, sizeof(%s))' % (varName, varTypeUnExpanded)
		return s


	def _hasBeenAssignedLater(self, varname):
		# There is case where a variable does not need an nondet assignment
		# 1. There is an immediate assign statement after the declaration of variable
		# 2. This variable is created in the sack of for loop
		# --> the two cases above can be compacted into one case: there is an assignment to variable after this
		if (self.__currentFun != '' and
			self.__currentFun in self.Parser.varNoNeedInit and
			varname in self.Parser.varNoNeedInit[self.__currentFun]):
			return True

		return False


	# TODO: avoid unnecessary special treatment for the __cs_ variables below.
	def _needInit(self, varname):
		if ('__cs_switch_cond' in varname or           # from switchtransformer.py
			'__cs_tmp_if_cond_' in varname or               # from extractor.py
			'__cs_tmp_while_cond_' in varname or              # from extractor.py
			'__cs_tmp_for_cond_' in varname or            # from extractor.py
			'__cs_dowhile_onetime_' in varname or    # from remover.py
			self._hasBeenAssignedLater(varname)):
			return False

		return True


	'''
	def visit_Decl(self, n, no_type=False):
		# There are two transformations for declaration statements of local variables.
		#
		# 1. split the type declaration from the initialisation, e.g.:
		#       int x = 3; ---> int x; x = 3;
		#
		# 2. force static storage class (unless already static), e.g.:
		#       int y; --> static int y;
		#
		if n.name and self.thisblocknode:
			if self.Parser.blocknode[self.thisblocknode] == self.Parser.blockdefid(self.Parser.blocknode[self.thisblocknode],n.name):
				print ("local variable: %s" % n.name)
				#print ("block: %s" % self.Parser.blocknode[self.thisblocknode])
				#print ("globl: %s" % self.Parser.isglobal(self.Parser.blocknode[self.thisblocknode],n.name))
				#print (" type: %s" % type(n))
				#print ("defid: %s\n" % self.Parser.blockdefid(self.Parser.blocknode[self.thisblocknode],n.name))

		if self.__currentFun != '' and n.name in self.Parser.varNames[self.__currentFun]:
			decl = ''

			if n.init:
				# Break up declaration and initialisation into two statements.
				oldinit = n.init
				n.init = None # temporarily disable generation of init expression
				declnoinit = super(self.__class__, self).visit_Decl(n,no_type)   # decl without init expr
				declinit = self.visit(oldinit)
				n.init = oldinit
				decl = declnoinit + '; %s = %s' % (n.name,declinit)
			else:
				# TODO: this warning should exclude temporary variables introduced by previous modules,
				#       such as __cs_tmp_if_cond, __cs_retval_, and so on.
				#
				# TODO: some backends (e.g. CBMC 5.8) can automatically handle initialisation of nondet static variables (--nondet-static),
				#       however variable-length arrays can't be statically declared.....
				#
				#       need to handle variable-length arrays
				#      (see old code snippet in inliner.py for nondet initialisation)
				#
				self.warn("uninitialised local variable %s in function %s" % (n.name, self.__currentFun))
				decl = super(self.__class__, self).visit_Decl(n,no_type)

			if not decl.startswith('static '):
				decl = 'static '+decl

			return decl

		return super(self.__class__, self).visit_Decl(n,no_type)
	'''

	def visit_Decl(self, n, no_type=False):
		# no_type is used when a Decl is part of a DeclList, where the type is
		# explicitly only for the first delaration in a list.
		#
		s = n.name if no_type else self._generate_decl(n)

		if n.bitsize: s += ' : ' + self.visit(n.bitsize)

		# Change local variables to be static vars,
		# needed for this particular encoding to remember the old values of local variables
		# between simulated context switches.
		#
		# If the variable is scalar or it is an array of fixed size
		# then just add  static  to its declaration.
		#
		# If the variable is an array of non fixed size,
		# then change it to a static pointer and adds a call to malloc() to complete the initialization,
		# (e.g.    int x[size];  -->  static int * x; x = (int *)malloc(sizeof(int)*size);  )
		#
		# TODO: init_scalar()/malloc() should not be called when variables have init expressions!
		#
		processInit = False    # Has processed the init expression

		# Detect declaration of constant variables
		# (also see _generate_type)
		#
		# TODO the detection is quite accurate,
		#      but the translation is very poor. Should be AST-based.
		#
		###if type(n.type) == pycparser.c_ast.TypeDecl and n.type.quals and 'const' in n.type.quals:
		if n.quals and 'const' in n.quals:
			if s.startswith('const '): s = s[6:]                   # something like "const int ...."
			elif ' const ' in s: s = s.replace(' const ', ' ', 1)  # something like "static const int ...."
			#self.warn("this variable is a constant %s" % n.name)

		if (isinstance(n, pycparser.c_ast.Decl) and              # it is a declaration
			self.__currentFun != '' and     # Not a global declaration
			self.indent_level > 0 and              # This is kind of useless
			not s.startswith('static ') and        # This may not usefull
			not self.__parsingStruct):             # and not part of a struct

			if ((self.__isScalar(self.__currentFun, n.name) or
				self.__isStruct(self.__currentFun, n.name)) and
				# Do not believe this check of having init expression??
				not self.Parser.varInitExpr[self.__currentFun, n.name]):
				s = 'static ' + s    # declaration
				if n.init:    # This variables has Init expression
					processInit = True
					if isinstance(n.init, pycparser.c_ast.InitList):
						s += ' = {' + self.visit(n.init) + '}'
					elif isinstance(n.init, pycparser.c_ast.ExprList):
						s += '; %s = (' % n.name + self.visit(n.init) + ')'
					else:
						s += '; %s = ' % n.name + self.visit(n.init)
				else:   # no init
					if self.__isScalar(self.__currentFun, n.name):
						varType = self.Parser.varType[self.__currentFun,n.name]
						#varType2 = self.Parser.buildtype(self.Parser.blocknode[self.thisblocknode],n.name)
						#varType3 = super(self.__class__, self).visit_Decl(n,no_type) 
						#print("type1:<%s>" % varType)
						#print("type2:<%s> initial block:<%s>"  % (varType2, self.Parser.blocknode[self.thisblocknode]   ))
						#print("type3:<%s>"  % (varType3))

						varTypeUnExpanded = self.Parser.varTypeUnExpanded[self.__currentFun,n.name]
						initialStmt = '; ' + self._initVar(varType, n.name, varTypeUnExpanded) if self._needInit(n.name) else ''
						s += initialStmt
					elif self.__isStruct(self.__currentFun, n.name):
						s += ''
					else:   ## what can it be?
						s += '; __cs_init_scalar(&%s, sizeof(%s))' % (
							n.name, self.Parser.varType[self.__currentFun, n.name])

			elif (self.__isScalar(self.__currentFun, n.name) and
				# Do not believe this check, it is not always true???
				self.Parser.varInitExpr[self.__currentFun, n.name]):
				s = 'static ' + s
				if n.init:
					processInit = True
					if isinstance(n.init, pycparser.c_ast.InitList):
						s += ' = {' + self.visit(n.init) + '}'
					elif isinstance(n.init, pycparser.c_ast.ExprList):
						s += '; %s = (' % n.name + self.visit(n.init) + ')'
					else:
						s += '; %s = ' % n.name + self.visit(n.init)
				else:
					varType = self.Parser.varType[self.__currentFun, n.name]
					varTypeUnExpanded = self.Parser.varTypeUnExpanded[self.__currentFun, n.name]
					initialStmt = '; ' + self._initVar(varType, n.name, varTypeUnExpanded) if self._needInit(n.name) else ''
					s += initialStmt

			elif self.__isArray(self.__currentFun, n.name):
				# There are two cases:
				# 1. this array has a constant expression of compound literal
				# 2. anything else
				init = ''
				initType = 0
				if n.init:
					processInit = True
					if isinstance(n.init, pycparser.c_ast.InitList):
						init = ' = {' + self.visit(n.init) + '}'
						initType = 1
					elif isinstance(n.init, pycparser.c_ast.ExprList):
						init = ' = (' + self.visit(n.init) + ')'
						initType = 0
					else:
						init = ' = ' + self.visit(n.init)
						initType = 0

				if initType == 1:
					# Case 1
					s = 'static ' + s + init
				else:
					# Anything else
					if processInit:
						if self._is_dynamic_size_array(self.__currentFun, n.name):
							s = 'static ' + s + init
						else:
							s = 'static ' + s + '; %s' % n.name + init
					else:
						if self.keepstaticarray:
							s = 'static ' + s
						else:
							stars = '*' * self.Parser.varArity[self.__currentFun, n.name]
							vartype = self.Parser.varTypeUnExpanded[self.__currentFun, n.name]
							s = 'static %s %s %s; ' % (vartype, stars, n.name)
							vartype = typemap[vartype] if vartype in typemap else vartype
							s += n.name + ' = (%s %s) %s(sizeof(%s)*%s)' % (vartype, stars, 'malloc', vartype, self._totalSize(self.__currentFun, n.name))
			else:    # Anything else, Truc's modification
				init = ''
				initType = 0
				if n.init:
					processInit = True
					if isinstance(n.init, pycparser.c_ast.InitList):
						init = ' = {' + self.visit(n.init) + '}'
						initType = 1
					elif isinstance(n.init, pycparser.c_ast.ExprList):
						init = ' = (' + self.visit(n.init) + ')'
						initType = 0
					else:
						init = ' = ' + self.visit(n.init)
						initType = 0
				if initType == 1:
					s = 'static ' + s + init
				else:
					if processInit:
						if self._is_dynamic_size_array(self.__currentFun, n.name):
							s = 'static ' + s + init
						else:
							s = 'static ' + s + '; %s' % n.name + init
					else:
						s = 'static ' + s + '; __cs_init_scalar(&%s, sizeof(%s))' % (
							n.name, self.Parser.varType[self.__currentFun, n.name])

		# Global variables and already static variables
		if n.init and not processInit:
			if isinstance(n.init, pycparser.c_ast.InitList):
				s += ' = {' + self.visit(n.init) + '}'
			elif isinstance(n.init, pycparser.c_ast.ExprList):
				s += ' = (' + self.visit(n.init) + ')'
			else:
				s += ' = ' + self.visit(n.init)

		if 'pthread_mutex_t' in s and s.startswith('static '):
			self.warn("static storage class for locks", snippet=True)
			self.staticlocks += s + ';\n'
			return ';'

		return s


	def visit_Struct(self, n):
		oldParsingStruct = self.__parsingStruct
		self.__parsingStruct = True
		#s = self._generate_struct_union(n, 'struct')
		#s = self._generate_struct_union_enum(n, 'struct')    # pycparser 2.10
		s = super(self.__class__, self).visit_Struct(n)
		self.__parsingStruct = oldParsingStruct

		return s


	''' The following two functions  (hasfixedsize, _is_dynamic_size_array)
		are both glitchy. Need to choose one and fix it properly.
	'''

	''' Check whether variable  v  from function  f  has a fixed size,
		or not (e.g.  int x[expr]   with expr not constant.
	'''
	def _hasFixedSize(self, f, v):
		if self.Parser.varArity[f,v] > 0:
			for i in range(0, self.Parser.varArity[f,v]):
				if not self.Parser.varSize[f,v][i].isdigit():
					return False

		return True

	def _is_dynamic_size_array(self, f, v):
		if (f, v) not in self.Parser.varID:
			return False

		if self.Parser.varArity[f, v] == 1 and self.Parser.varSize[f, v][0] == -1:
			return True

		return False


	''' Return the total size of a given array in a string,
		as the expression of the product of all sizes.

		For example:

			int x[10][expr][3];

		returns:

			size = 10*(expr)*30;
	'''
	def _totalSize(self, f, v):
		sizeExpression = ''

		for i in range(0, self.Parser.varArity[f,v]):
			#if self.Parser.varSize[f,v][i].isdigit():     # simple digit
			sizeExpression += str(self.Parser.varSize[f,v][i]) + '*'

		sizeExpression = sizeExpression[:-1]

		return sizeExpression


	# Checks whether variable  v  from function  f  is an array.
	#
	def __isArray(self, f, v):
		return 1 if self.Parser.varArity[f,v] > 0 else 0


	# Checks whether variable  v  from function  f  is scalar.
	# TODO redo properly at AST-level
	#
	def __isScalar(self, f, v):
		if self.Parser.varArity[f,v] == 0  and not self.Parser.varType[f,v].startswith('struct ') and not self.Parser.varType[f,v].startswith('union '):
			return 1
		else:
			return 0


	# Checks whether variable  v  from function  f  is a struct.
	# TODO redo properly at AST-level
	#
	def __isStruct(self, f, v):
		return 1 if self.Parser.varType[f, v].startswith('struct ') else 0





