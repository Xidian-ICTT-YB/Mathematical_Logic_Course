""" CSeq Program Analysis Framework

The purpose of this module is to remove assert functions when running the data race check,
in order to avoid wrong results from files that also have the unreach-call property

Authors:
	Alex Coto, Emerson Sales

Changes:
	2021.11.17  first version
"""

import core.module
import core.parser
import core.utils


class ignoreassertions(core.module.Translator):

	def init(self):
		self.inputparam(
			"data-race-check",
			"Enable data race detection (and disable assertions)",
			"",
			default=False,
			optional=True,
		)

		self.dataracecheck = False

	def loadfromstring(self, string, env):
		self.dataracecheck = True if self.getinputparam(
			'data-race-check') is not None else False

		super(self.__class__, self).loadfromstring(string, env)

	def visit_FuncCall(self, n):
		"""
		# name: Id
		# args: ExprList
		#
		FuncCall: [name*, args*]
		"""
		ret = super(self.__class__, self).visit_FuncCall(n)

		if not self.dataracecheck:
			return ret

		assertions = ["assert", "ASSERT", "reach_error", "abort"]

		if hasattr(n.name, 'name') and n.name.name in assertions:
			return "__dummy__()"

		return ret

	def visit_Label(self, n):
		"""
		Label: [name, stmt*]
		"""
		ret = super(self.__class__, self).visit_Label(n)

		if not self.dataracecheck:
			return ret
		
		if 'ERROR' in n.name:
			return self._generate_stmt(n.stmt)
		
		return ret
