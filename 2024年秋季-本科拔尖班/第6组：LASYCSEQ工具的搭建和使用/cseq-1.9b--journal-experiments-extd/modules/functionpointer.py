""" CSeq Program Analysis Framework
	Function call by pointer expansion module.

Author:
	Christof Rossouw

To do:
  - test in complex situations (meanwhile the module is disabled by default)

"""
import copy, re
import pycparserext.ext_c_parser, pycparser.c_ast, pycparserext.ext_c_generator
from pycparser import c_ast
import core.module, core.parser, core.utils


class functionpointer(core.module.Translator):
	_func_call_in_scope = False
	fptr = None

	def init(self):
		self.inputparam('fptr', 'remove calls to function pointers', '', default=None, optional=True)

	def loadfromstring(self, string, env):
		self.fptr = True if self.getinputparam('fptr') is not None else False
		super(self.__class__, self).loadfromstring(string, env)

	def visit_Decl(self, n):
		if not self.fptr: return super(self.__class__, self).visit_Decl(n)

		if n is not None:
			for child in n.children():
				if isinstance(child[1], c_ast.FuncCall) and self.is_pointer_function_call(child[1]):
					self._func_call_in_scope = True
					s = self.generate_if_structure(n)
					self._func_call_in_scope = False
					return s
		s = super(self.__class__, self).visit_Decl(n)
		return s

	def visit_Assignment(self, n):
		if not self.fptr: return super(self.__class__, self).visit_Assignment(n)

		if n is not None:
			for child in n.children():
				if isinstance(child[1], c_ast.FuncCall) and self.is_pointer_function_call(child[1]):
					self._func_call_in_scope = True
					s = self.generate_if_structure(n)
					self._func_call_in_scope = False
					return s
		s = super(self.__class__, self).visit_Assignment(n)
		return s

	def visit_FuncCall(self, n):
		if not self.fptr: return super(self.__class__, self).visit_FuncCall(n)

		if not self._func_call_in_scope and self.is_pointer_function_call(n):
			s = self.generate_if_structure(n)
			self.debug("expanding call to function pointer")
			return s
		s = super(self.__class__, self).visit_FuncCall(n)
		return s

	def is_pointer_function_call(self, n):
		if not isinstance(n, c_ast.FuncCall):
			return False

		for c in n.children():
			if isinstance(c[1], c_ast.UnaryOp) and c[1].op == '*':
				return True
		return False

	def generate_if_structure(self, n):
		decl_s = ''
		if isinstance(n, c_ast.Decl):
			decl_s = super(self.__class__, self)._generate_decl(n) + ';\n'
			if n.bitsize: decl_s += ' : ' + self.visit(n.bitsize)

		varname = ''
		func_call = None
		for i in n.children():
			if isinstance(i[1], c_ast.FuncCall):
				func_call = i[1]
				for j in i[1].children():
					if isinstance(j[1], c_ast.UnaryOp):
						for k in j[1].children():
							if isinstance(k[1], c_ast.ID):
								varname = k[1].name
								break
						break
				break
		if isinstance(n, c_ast.FuncCall):
			func_call = n
			for j in n.children():
				if isinstance(j[1], c_ast.UnaryOp):
					for k in j[1].children():
						if isinstance(k[1], c_ast.ID):
							varname = k[1].name
							break
					break
		is_first = True
		s = '' + decl_s
		for f_name in self.Parser.funcName:
			if len(f_name) == 0:
				continue
			apcnt = len(func_call.args.exprs) if func_call.args is not None else 0
			func_def = self.Parser.funcASTNode[f_name]
			fpcnt = len(func_def.decl.type.args.params) if func_def.decl.type.args is not None else 0
			if apcnt != fpcnt:
				continue

			if is_first:
				is_first = False
				s += 'if '
			else:
				s += ' else if '

			s += '( %s == &%s ) ' % (varname, f_name)

			if isinstance(n, c_ast.FuncCall):
				s += '{ %s( %s ); }' % (f_name, super(self.__class__, self).visit(n.args))
			elif isinstance(n, c_ast.Assignment):
				s += '{ %s = %s( %s ); }' % (n.lvalue.name, f_name, super(self.__class__, self).visit(func_call.args))
			elif isinstance(n, c_ast.Decl):
				s += '{ %s = %s( %s ); }' % (n.name, f_name, super(self.__class__, self).visit(func_call.args))

		return s



